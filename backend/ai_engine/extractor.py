import json
import re

from config import GEMINI_API_KEY, GEMINI_MODEL

try:
    from google import genai
except ImportError:
    genai = None


class NeedExtractor:
    CATEGORY_KEYWORDS = {
        "food": ["food", "hunger", "ration", "nutrition", "meal"],
        "water": ["water", "drinking water", "hydration", "sanitation"],
        "medical": ["medical", "medicine", "doctor", "injury", "hospital", "health", "patients"],
        "education": ["education", "school", "teacher", "books", "students"],
        "shelter": ["shelter", "housing", "tent", "displaced", "roof"],
    }

    URGENCY_KEYWORDS = {
        "critical": ["critical", "immediate", "life-threatening", "emergency"],
        "urgent": ["urgent", "severe", "asap", "high priority"],
        "moderate": ["moderate", "soon", "needed"],
        "low": ["stable", "routine", "low"],
    }

    LOCATION_PATTERNS = [
        r"(?:in|at|near)\s+([A-Z][A-Za-z0-9\s-]*?)(?=\s+(?:affecting|for|with|where|requiring|and)\b|[.,]|$)",
        r"(Village\s+[A-Z][A-Za-z0-9-]*)",
        r"(City\s+[A-Z][A-Za-z0-9-]*)",
        r"(Area\s+[A-Z][A-Za-z0-9-]*)",
        r"(District\s+[A-Z][A-Za-z0-9-]*)",
        r"(Camp\s+[A-Z][A-Za-z0-9-]*)",
    ]

    VALID_CATEGORIES = {"food", "water", "medical", "education", "shelter", "general"}
    VALID_URGENCY = {"critical", "urgent", "moderate", "low"}

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY and genai else None

    def extract(self, text):
        clean_text = " ".join((text or "").split())
        gemini_result = self._extract_with_gemini(clean_text)
        if gemini_result:
            return {
                **gemini_result,
                "raw_text": clean_text,
                "extraction_method": "gemini",
                "ai_service": "Google Gemini API",
            }

        lowered = clean_text.lower()
        return {
            "category": self._extract_category(lowered),
            "location": self._extract_location(clean_text),
            "people_affected": self._extract_people(clean_text),
            "urgency": self._extract_urgency(lowered),
            "raw_text": clean_text,
            "extraction_method": "rule_based",
            "ai_service": "Rule-based NLP fallback",
        }

    def _extract_with_gemini(self, text):
        if not self.client or not text:
            return None

        prompt = f"""
Extract structured NGO relief information from the report below.
Return only valid JSON with exactly these keys:
- category: one of food, water, medical, education, shelter, general
- location: short place name
- people_affected: integer
- urgency: one of critical, urgent, moderate, low

If any field is unclear, use:
- category: general
- location: Location pending verification
- people_affected: 0
- urgency: moderate

Report:
\"\"\"{text}\"\"\"
""".strip()

        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            payload = self._parse_gemini_json(response.text if response else "")
            if not payload:
                return None

            category = str(payload.get("category", "general")).strip().lower()
            urgency = str(payload.get("urgency", "moderate")).strip().lower()
            location = str(payload.get("location", "Location pending verification")).strip() or "Location pending verification"
            people = self._coerce_people(payload.get("people_affected", 0))

            return {
                "category": category if category in self.VALID_CATEGORIES else "general",
                "location": location,
                "people_affected": people,
                "urgency": urgency if urgency in self.VALID_URGENCY else "moderate",
            }
        except Exception:
            return None

    def _parse_gemini_json(self, raw_text):
        cleaned = (raw_text or "").strip()
        if not cleaned:
            return None

        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    def _coerce_people(self, value):
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0

    def _extract_category(self, lowered):
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                return category
        return "general"

    def _extract_urgency(self, lowered):
        for urgency, keywords in self.URGENCY_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                return urgency
        return "moderate"

    def _extract_people(self, text):
        patterns = [
            r"(\d+)\s+(?:people|families|villagers|children|patients|students)",
            r"(\d+)\s+(?:households|residents|persons|adults)",
            r"affecting\s+(\d+)",
            r"for\s+(\d+)",
            r"impacting\s+(\d+)",
            r"around\s+(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        standalone = re.search(r"\b(\d{1,5})\b", text)
        return int(standalone.group(1)) if standalone else 0

    def _extract_location(self, text):
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip().rstrip(".")
        return "Location pending verification"
