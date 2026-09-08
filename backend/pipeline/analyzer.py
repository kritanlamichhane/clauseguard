import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Tuple, Dict, Any
from backend.core.config import GEMINI_API_KEY
from backend.core.rate_limiter import gemini_rate_limiter, RateLimitExceeded

_client = None

def get_client():
    global _client
    if _client is None:
        try:
            if GEMINI_API_KEY:
                _client = genai.Client(api_key=GEMINI_API_KEY)
            else:
                _client = genai.Client()
        except Exception as e:
            print(f"[WARNING] analyzer.py: Could not initialize Gemini client: {e}")
            _client = False
    return _client if _client is not False else None


# Define the schemas for structured batch contract risk assessment
class SingleClauseAssessment(BaseModel):
    clause_index: int = Field(description="The matching zero-based index of the clause")
    risk_level: str = Field(description="Must be 'high', 'medium', 'low', or 'safe'")
    risk_type: str = Field(description="Short label identifying the risk")
    explanation: str = Field(description="1-2 sentences in plain English")
    recommendation: str = Field(description="1 sentence practical next step")


class ContractBatchAnalysis(BaseModel):
    assessments: List[SingleClauseAssessment]
    summary: str = Field(description="A 2-3 sentence plain-English summary of the overall risk level")


def generate_contract_summary(all_clause_results: List[Dict[str, Any]]) -> str:
    """
    Generates a plain-English summary of the overall risk level of this contract locally.
    """
    high_risks = [r for r in all_clause_results if r.get("risk_level") == "high"]
    if high_risks:
        risks_str = ", ".join(set([r.get("risk_type", "Unknown") for r in high_risks]))
        return f"Warning: This contract contains high-risk issues related to: {risks_str}. Please review these sections carefully before signing."

    medium_risks = [r for r in all_clause_results if r.get("risk_level") == "medium"]
    if medium_risks:
        risks_str = ", ".join(set([r.get("risk_type", "Unknown") for r in medium_risks]))
        return f"This contract has medium-risk issues related to: {risks_str}. Consider negotiating these terms."

    return "This contract has minimal or low risk issues and appears generally standard. Review terms before signing."


def analyze_contract_batch(processed_clauses_list: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
    """
    Sends all clauses and their NLP signals to Gemini in one structured request,
    with local heuristic fallbacks if offline.
    """
    if not processed_clauses_list:
        return [], "No clauses analyzed."

    master_context = "Here is a list of contract clauses along with their pipeline analysis. Analyze each one:\n\n"
    for idx, item in enumerate(processed_clauses_list):
        master_context += f"--- Clause #{idx} ---\n"
        master_context += f"Text: \"{item['text']}\"\n"
        if item.get('classification'):
            master_context += f"ML Type: {item['classification'].get('clause_type', 'Unknown')}\n"
        if item.get('rule_matches'):
            master_context += f"Flags: {', '.join([m['risk_type'] for m in item['rule_matches']])}\n"
        if item.get('similarity_match'):
            master_context += f"Similarity Match: {item['similarity_match'].get('risk_type', 'None')}\n"
        master_context += "\n"

    prompt = f"""You are a contract risk analyst helping a small business owner.
    
{master_context}

Provide a final risk assessment for every single clause listed above. Your output must map back to the correct clause_index.
Also, write a 2-3 sentence overall plain-English summary of the contract's risks.
"""

    clause_results = []
    for idx, item in enumerate(processed_clauses_list):
        clause_results.append({
            "clause_text": item["text"],
            "clause_type_predicted": item.get("classification", {}).get("clause_type", "Unknown"),
            "risk_level": "safe",
            "risk_type": "Safe",
            "explanation": "No issues detected.",
            "recommendation": ""
        })

    summary = ""

    try:
        client = get_client()
        if not client:
            raise RuntimeError("Gemini SDK client unavailable or GEMINI_API_KEY missing.")

        # Estimate tokens: ~1 token per 4 chars of input + 1024 for output
        estimated_tokens = len(prompt) // 4 + 1024

        with gemini_rate_limiter.acquire(estimated_tokens=estimated_tokens):
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ContractBatchAnalysis,
                    temperature=0.1,
                ),
            )

        data = json.loads(response.text)
        assessments = data.get("assessments", [])
        summary = data.get("summary", "").strip()

        for assessment in assessments:
            if isinstance(assessment, dict):
                idx = assessment.get("clause_index")
                risk_level = assessment.get("risk_level", "safe")
                risk_type = assessment.get("risk_type", "Safe")
                explanation = assessment.get("explanation", "")
                recommendation = assessment.get("recommendation", "")
            else:
                idx = getattr(assessment, "clause_index", None)
                risk_level = getattr(assessment, "risk_level", "safe")
                risk_type = getattr(assessment, "risk_type", "Safe")
                explanation = getattr(assessment, "explanation", "")
                recommendation = getattr(assessment, "recommendation", "")

            if idx is not None and 0 <= idx < len(clause_results):
                risk_level = risk_level.lower() if risk_level else "safe"
                if risk_level not in ["high", "medium", "low", "safe"]:
                    risk_level = "safe"
                clause_results[idx]["risk_level"] = risk_level
                clause_results[idx]["risk_type"] = risk_type
                clause_results[idx]["explanation"] = explanation
                clause_results[idx]["recommendation"] = recommendation

    except RateLimitExceeded:
        # Re-raise so the API router can return a proper 429
        raise
    except Exception as e:
        print(f"[WARN] analyzer.py: LLM Batch analysis fallback: {str(e)}")
        for idx, item in enumerate(processed_clauses_list):
            rule_matches = item.get("rule_matches", [])
            similarity_match = item.get("similarity_match")

            highest_risk = "safe"
            risk_type = "Safe"
            explanation = "No issues detected."
            recommendation = ""

            if rule_matches:
                highest_risk = rule_matches[0].get("risk_level", "low").lower()
                risk_type = rule_matches[0].get("risk_type", "Rule Violation")
                explanation = f"Flagged by rule: {risk_type}."
                recommendation = "Review clause carefully."
            elif similarity_match and similarity_match.get("similarity_score", 0) > 0.8:
                highest_risk = "medium"
                risk_type = similarity_match.get("risk_type", "Similar Risk")
                explanation = f"Semantically similar to known risk: {risk_type}."
                recommendation = "Verify if terms are acceptable."

            clause_results[idx].update({
                "risk_level": highest_risk,
                "risk_type": risk_type,
                "explanation": explanation,
                "recommendation": recommendation
            })

    if not summary:
        summary = generate_contract_summary(clause_results)

    return clause_results, summary
