import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    pass


class LLMService:
    """Handle LLM-based entity extraction using Gemini API."""

    def __init__(self):
        # Read Gemini API key from environment
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_client = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.gemini_client = genai.GenerativeModel("gemini-pro")
                logger.info("[LLM] Gemini client initialized.")
            except Exception as e:
                logger.error(f"[LLM] Failed to initialize Gemini client: {e}")
        else:
            logger.warning("[LLM] GEMINI_API_KEY not set. Gemini client disabled.")

    def extract_entities(self, raw_text: str, file_path: str, blocks: list | None = None) -> Dict[str, Any]:
        """
        Extract structured entities from raw OCR text using Gemini LLM.
        """
        logger.info(f"[LLM] Extracting entities from text (length: {len(raw_text)})")

        fallback = self._fallback_extract(raw_text)

        if not self.gemini_client:
            logger.warning("[LLM] Gemini client not initialized. Using fallback extraction.")
            return fallback

        try:
            prompt = (
                """
                Extract the following fields from the OCR text below. Return a JSON object with these keys:
                - holder: { name, fatherName, dob }
                - credential: { degree, institution, year, cgpa }
                - issuer: { name }
                - confidence: { name, fatherName, dob, degree, institution, year, cgpa, issuer }
                - documentType
                
                OCR TEXT:
                """ + raw_text + "\n\nOCR BLOCKS:\n" + (str(blocks) if blocks else "[]")
            )
            response_text = self._call_gemini(prompt)
            parsed = self._parse_json(response_text)
            logger.info("[LLM] Gemini extraction succeeded.")
            return self._merge_extraction(fallback, parsed)
        except Exception as e:
            logger.error(f"[LLM] Gemini extraction failed: {e}")
            return fallback

    def detect_document_type(self, raw_text: str) -> str:
        text = raw_text.lower()
        if "aadhaar" in text:
            return "AADHAAR"
        if "passport" in text:
            return "PASSPORT"
        if "driving" in text and "license" in text:
            return "DRIVING_LICENSE"
        if "statement of marks" in text:
            return "MARKSHEET"
        if "marksheet" in text or "mark sheet" in text:
            return "MARKSHEET"
        if "degree" in text or "certificate" in text:
            return "DEGREE_CERTIFICATE"
        return "UNKNOWN"

    def repair_json(self, raw_text: str) -> Dict[str, Any]:
        return self._parse_json(raw_text)

    def _call_gemini(self, prompt: str) -> str:
        for attempt in range(3):
            try:
                response = self.gemini_client.generate_content(prompt)
                return response.text if hasattr(response, "text") else response["text"]
            except RateLimitError:
                logger.warning(f"[LLM] Rate limit hit, retry {attempt + 1}/3")
                if attempt == 2:
                    raise
            except Exception:
                raise
        return ""

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        import json
        try:
            return json.loads(raw_text)
        except Exception:
            # Attempt to salvage a JSON object substring
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(raw_text[start:end + 1])
                except Exception:
                    return {}
            return {}

    def _fallback_extract(self, raw_text: str) -> Dict[str, Any]:
        import re

        text = " ".join(raw_text.split())
        doc_type = self.detect_document_type(raw_text)

        def pick_group(match: re.Match | None, idx: int) -> str | None:
            if not match:
                return None
            value = match.group(idx).strip()
            return value if value else None

        name_match = re.search(
            r"(?:Student\s+Full\s+Name|Student\s+Name)\s*[:\-]?\s*([A-Z][A-Z\s]+)",
            text,
            re.IGNORECASE,
        )
        degree_match = re.search(
            r"(Bachelor|Master)\s+of\s+[A-Za-z\s]+(?:Engineering|Science|Arts|Commerce|Technology)",
            text,
            re.IGNORECASE,
        )
        institution_match = re.search(r"([A-Z][A-Z\s]+UNIVERSITY)", text)
        year_match = re.search(r"(19\d{2}|20\d{2})", text)
        sgpa_match = re.search(r"SGPA\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
        cgpa_match = re.search(r"CGPA\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)

        name = pick_group(name_match, 1)
        degree = pick_group(degree_match, 0)
        institution = pick_group(institution_match, 1)
        year = pick_group(year_match, 1)
        cgpa = pick_group(cgpa_match, 1) or pick_group(sgpa_match, 1)

        confidence = {}
        if name:
            confidence["name"] = 0.6
        if degree:
            confidence["degree"] = 0.6
        if institution:
            confidence["institution"] = 0.6
        if year:
            confidence["year"] = 0.5
        if cgpa:
            confidence["cgpa"] = 0.5

        return {
            "holder": {"name": name},
            "credential": {
                "degree": degree,
                "institution": institution,
                "year": year,
                "cgpa": cgpa,
            },
            "issuer": {"name": institution},
            "confidence": confidence,
            "documentType": doc_type,
        }

    def _merge_extraction(self, fallback: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
        if not parsed:
            return fallback

        merged = {
            "holder": {**fallback.get("holder", {}), **parsed.get("holder", {})},
            "credential": {**fallback.get("credential", {}), **parsed.get("credential", {})},
            "issuer": {**fallback.get("issuer", {}), **parsed.get("issuer", {})},
            "confidence": {**fallback.get("confidence", {}), **parsed.get("confidence", {})},
            "documentType": parsed.get("documentType") or fallback.get("documentType"),
        }

        return merged

