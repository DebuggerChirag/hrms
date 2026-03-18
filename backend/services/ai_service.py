import os
import json
import logging
from typing import Tuple
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using pdfminer.six"""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(file_path)
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""

def evaluate_refund_request(pdf_path: str, reason: str, amount: float) -> Tuple[str, str]:
    """
    Sends document text and patient reason to Gemini.
    Returns: (status: 'Approved' or 'Rejected', decision_reason: str)
    """
    if not api_key:
        return "Pending", "Gemini API key is not configured in .env"

    doc_text = extract_text_from_pdf(pdf_path) if pdf_path else "No document provided."
    
    prompt = f"""
    You are an automated medical refund policy evaluator.
    A patient is requesting a refund of ${amount} for the following reason:
    "{reason}"
    
    The patient provided the following supporting document text:
    "{doc_text[:3000]}" # Limiting text to prevent context window issues
    
    Analyze the reason and document. Decide whether the refund should be Approved or Rejected based on reasonable standard medical refund policies (e.g., valid receipt, covered procedure, within time limits).
    
    Return your answer in strictly formatted JSON exactly like this:
    {{
      "status": "Approved" or "Rejected",
      "reason": "short explanation"
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_resp = response.text
        
        # Clean markdown formatting if present
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:-3]
        elif text_resp.startswith("```"):
            text_resp = text_resp[3:-3]
            
        ai_response = json.loads(text_resp.strip())
        status = ai_response.get("status", "Pending")
        explanation = ai_response.get("reason", "No reason provided by AI.")
        
        if "approve" in status.lower():
            return ("Approved", explanation)
        else:
            return ("Rejected", explanation)
            
    except Exception as e:
        logger.error(f"Error in evaluate_refund_request (Gemini): {e}")
        return ("Pending", f"Error communicating with AI service: {str(e)}")
