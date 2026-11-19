import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.models import GuidelineChunk, ApprovedFact

logger = logging.getLogger("inkloom.nemotron")

ANALYSIS_SYSTEM_PROMPT = """You are Inkloom AI's Enterprise Brand Governance Intelligence Engine.
Your purpose is to rigorously inspect marketing, technical, and business communications against provided brand guidelines and approved factual records.

CRITICAL OPERATIONAL RULES:
1. EVIDENCE-BACKED ONLY: Every violation you identify MUST be grounded in the provided Brand Guidelines or Approved Facts. Never hallucinate or fabricate guidelines or citations.
2. UNVERIFIED CLAIMS: If the text makes a factual or performance claim that is NOT supported by the Approved Facts, flag it as 'unsupported_claim' with severity 'medium' or 'high' and citation_source 'Unverified Fact'.
3. INTENT-PRESERVING CORRECTIONS: For every finding, provide an exact replacement sentence that maintains the author's original message, core value proposition, and professional tone without introducing unapproved factual claims.
4. STRICT JSON FORMAT: Output MUST be a valid JSON object matching the requested schema. Do not include markdown codeblocks or text outside the JSON.

Expected JSON output format:
{
  "overall_score": 88.5,
  "summary": "Brief executive summary of brand governance findings.",
  "findings": [
    {
      "problematic_text": "exact snippet from submitted text",
      "finding_type": "guideline_violation | unsupported_claim | tone_inconsistency | terminology | restricted_phrase",
      "severity": "critical | high | medium | low | info",
      "explanation": "Why this violates brand governance rules.",
      "citation_source": "Source document name or 'Approved Facts' or 'Unverified'",
      "citation_section": "Specific guideline section or fact category",
      "suggested_sentence": "Full replacement sentence preserving author intent",
      "intent_explanation": "How this correction preserves the original meaning while meeting brand compliance"
    }
  ]
}
"""

class NemotronService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.NEMOTRON_MODEL

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your-"))

    async def validate_connection(self) -> Dict[str, Any]:
        """Validates API credentials without exposing the key in logs."""
        if not self.is_configured():
            return {"configured": False, "status": "Missing OPENROUTER_API_KEY in backend environment."}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                if res.status_code == 200:
                    return {"configured": True, "status": "Active", "model": self.model}
                else:
                    return {"configured": False, "status": f"OpenRouter returned status {res.status_code}"}
        except Exception as e:
            return {"configured": False, "status": f"Connection error: {str(e)}"}

    async def analyze_content(
        self,
        content: str,
        content_type: str,
        guideline_chunks: List[GuidelineChunk],
        approved_facts: List[ApprovedFact]
    ) -> Optional[Dict[str, Any]]:
        """Invokes NVIDIA Nemotron via OpenRouter with context-aware prompt."""
        if not self.is_configured():
            logger.warning("OPENROUTER_API_KEY not configured. Falling back to rule-based engine.")
            return None

        # Format context
        guidelines_text = "\n\n".join([
            f"--- GUIDELINE [{c.guideline.title if c.guideline else 'General'} | Section: {c.section_name}] ---\n{c.content}"
            for c in guideline_chunks
        ]) if guideline_chunks else "No specific guidelines provided."

        facts_text = "\n".join([
            f"- [{f.category}] {f.statement} (Verified by: {f.verification_source})"
            for f in approved_facts
        ]) if approved_facts else "No approved facts provided."

        user_prompt = f"""CONTENT TYPE: {content_type}

### STORED BRAND GUIDELINES:
{guidelines_text}

### APPROVED CORPORATE FACTS & METRICS:
{facts_text}

### SUBMITTED CONTENT FOR GOVERNANCE REVIEW:
\"\"\"{content}\"\"\"

Perform complete brand governance analysis and respond ONLY in valid JSON matching the system schema.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": settings.FRONTEND_URL,
            "X-Title": "Inkloom AI Brand Governance",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )

                    if response.status_code != 200:
                        logger.error(f"OpenRouter error {response.status_code}: {response.text}")
                        continue

                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        continue

                    message_content = choices[0].get("message", {}).get("content", "")
                    
                    # Clean markdown formatting if present
                    clean_content = message_content.strip()
                    if clean_content.startswith("```"):
                        clean_content = clean_content.split("```")[1]
                        if clean_content.startswith("json"):
                            clean_content = clean_content[4:]
                        clean_content = clean_content.strip()

                    parsed = json.loads(clean_content)
                    return parsed
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} Nemotron analysis failed: {str(e)}")

        return None

nemotron_service = NemotronService()
