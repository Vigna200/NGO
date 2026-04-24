import re


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

    def extract(self, text):
        clean_text = " ".join((text or "").split())
        lowered = clean_text.lower()

        return {
            "category": self._extract_category(lowered),
            "location": self._extract_location(clean_text),
            "people_affected": self._extract_people(clean_text),
            "urgency": self._extract_urgency(lowered),
            "raw_text": clean_text,
        }

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
