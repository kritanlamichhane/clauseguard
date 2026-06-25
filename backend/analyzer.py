import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def build_clause_context(clause_text, rule_matches, classification, similarity_match):
    """
    Combines all our NLP pipeline outputs for ONE clause into a
    structured context block to feed Gemini. This is the bridge
    between our NLP work and the LLM.
    """
    context = f'Clause text: "{clause_text}"\n'

    if classification:
        context += f"Predicted clause type (ML model): {classification['clause_type']} (confidence: {classification['confidence']})\n"

    if rule_matches:
        context += "Rule-based risk flags found:\n"
        for match in rule_matches:
            context += f"  - {match['risk_type']} ({match['risk_level']})\n"

    if similarity_match:
        context += f"Semantic similarity match: {similarity_match['risk_type']} (similarity score: {similarity_match['similarity_score']})\n"

    return context


def analyze_clause(clause_text, rule_matches, classification, similarity_match):
    """
    Sends one clause + all our NLP signals to Gemini for final judgment.
    Returns a clean, structured risk assessment.
    """
    context = build_clause_context(clause_text, rule_matches, classification, similarity_match)

    prompt = f"""You are a contract risk analyst helping a small business owner who has no legal background.

{context}

Based on the clause text and the signals above, provide a final risk assessment.
Respond ONLY with valid JSON in this exact format, nothing else:

{{
  "risk_level": "high" or "medium" or "low" or "safe",
  "risk_type": "short label, e.g. Auto-renewal trap",
  "explanation": "1-2 sentences in plain English explaining the risk to a non-lawyer",
  "recommendation": "1 sentence suggesting what to do about it"
}}
"""

    response = model.generate_content(prompt)

    # Clean up response — Gemini sometimes wraps JSON in markdown code blocks
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {
            "risk_level": "unknown",
            "risk_type": "Could not analyze",
            "explanation": "The analysis could not be completed for this clause.",
            "recommendation": "Please review this clause manually."
        }

    return result


def generate_contract_summary(all_clause_results):
    """
    After all clauses are analyzed individually, ask Gemini for one
    overall plain-English summary of the contract's biggest risks.
    """
    high_risks = [r for r in all_clause_results if r.get("risk_level") == "high"]

    summary_input = "High risk issues found in this contract:\n"
    for r in high_risks:
        summary_input += f"- {r['risk_type']}: {r['explanation']}\n"

    if not high_risks:
        summary_input = "No high-risk issues were found in this contract."

    prompt = f"""You are summarizing a contract risk analysis for a small business owner.

{summary_input}

Write a 2-3 sentence plain-English summary of the overall risk level of this contract and what they should pay most attention to before signing.
"""

    response = model.generate_content(prompt)
    return response.text.strip()