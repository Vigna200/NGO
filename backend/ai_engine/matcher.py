class VolunteerMatcher:
    CATEGORY_SKILL_MAP = {
        "food": ["food distribution", "logistics", "transport"],
        "water": ["water", "logistics", "transport"],
        "medical": ["medical", "health"],
        "education": ["education", "child support"],
        "shelter": ["shelter", "logistics", "transport"],
        "general": ["logistics"],
    }

    def match(self, need, volunteers):
        best_candidate = None
        best_score = -1
        desired_skills = self.CATEGORY_SKILL_MAP.get(need["category"], ["logistics"])

        for volunteer in volunteers:
            score = 0.0
            skills_blob = " ".join(volunteer["skills"]).lower()

            if volunteer["availability"]:
                score += 0.4
            if volunteer["location"].lower() == need["location"].lower():
                score += 0.35
            elif any(token in need["location"].lower() for token in volunteer["location"].lower().split()):
                score += 0.2
            if any(skill in skills_blob for skill in desired_skills):
                score += 0.25

            if score > best_score:
                best_candidate = volunteer
                best_score = score

        if not best_candidate:
            return {"assigned_volunteer": "Unassigned", "assigned_volunteer_id": None, "confidence": 0.0}

        return {
            "assigned_volunteer": best_candidate["name"],
            "assigned_volunteer_id": best_candidate["id"],
            "confidence": round(best_score, 2),
        }
