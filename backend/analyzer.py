import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field
from typing import List

# Load environment variables
load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        try:
            _client = genai.Client()
        except Exception as e:
            print(f"[WARNING] analyzer.py: Could not initialize Gemini client: {e}")
            _client = False
    return _client if _client is not False else None



# Define the schemas for batch contract risk assessment
class SingleClauseAssessment(BaseModel):
    clause_index: int = Field(description="The matching zero-based index of the clause")
    risk_level: str = Field(description="Must be 'high', 'medium', 'low', or 'safe'")
    risk_type: str = Field(description="Short label identifying the risk")
    explanation: str = Field(description="1-2 sentences in plain English")
    recommendation: str = Field(description="1 sentence practical next step")

class ContractBatchAnalysis(BaseModel):
    assessments: List[SingleClauseAssessment]
    summary: str = Field(description="A 2-3 sentence plain-English summary of the " \
                                    "overall risk level of this contract and what the user" \
                                    " should pay most attention to before signing")


def generate_contract_summary(all_clause_results):
    """
    Generates a plain-English summary of the overall risk level of this contract
    locally to avoid API rate limiting.
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


def analyze_contract_batch(processed_clauses_list):
    """
    Sends ALL clauses and their NLP signals to Gemini in ONE single request,
    then maps the response back to each clause and returns (clause_results, overall_summary).
    """
    if not processed_clauses_list:
        return [], "No clauses analyzed."

    # Build a single master context block
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

    # Initialize default results for every input clause
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

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ContractBatchAnalysis,
                temperature=0.1,
            ),
        )


        
        # Parse the JSON response
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
                # Normalize risk_level to match backend expectations (lowercase)
                risk_level = risk_level.lower() if risk_level else "safe"
                if risk_level not in ["high", "medium", "low", "safe"]:
                    risk_level = "safe"
                clause_results[idx]["risk_level"] = risk_level
                clause_results[idx]["risk_type"] = risk_type
                clause_results[idx]["explanation"] = explanation
                clause_results[idx]["recommendation"] = recommendation
                
    except Exception as e:
        print(f"[ERROR] Batch analysis failed: {str(e)}")
        # If Gemini fails, fall back to local NLP heuristics
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
            
    # Generate fallback summary if empty
    if not summary:
        summary = generate_contract_summary(clause_results)

    return clause_results, summary