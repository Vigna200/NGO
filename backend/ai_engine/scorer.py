class PriorityScorer:
    URGENCY_WEIGHTS = {
        "critical": 100,
        "urgent": 80,
        "moderate": 50,
        "low": 20,
    }

    CATEGORY_WEIGHTS = {
        "medical": 100,
        "food": 90,
        "water": 85,
        "shelter": 75,
        "education": 55,
        "general": 50,
    }

    def score(self, need):
        urgency_weight = self.URGENCY_WEIGHTS.get(need["urgency"], 50)
        people_weight = min(need["people_affected"], 500)
        category_weight = self.CATEGORY_WEIGHTS.get(need["category"], 50)

        repeat_bonus = max(0, need.get("source_count", 1) - 1) * 60
        score = urgency_weight + (people_weight * 0.3) + category_weight + repeat_bonus

        repeated_critical_need = need.get("source_count", 1) >= 2 and need.get("category") in {"water", "food", "medical", "shelter"}

        if score >= 220 or (repeated_critical_need and score >= 150):
            priority = "Very High"
        elif score >= 180:
            priority = "High"
        elif score >= 120:
            priority = "Medium"
        else:
            priority = "Low"

        return {
            "priority_score": round(score, 2),
            "priority": priority,
            "score_breakdown": {
                "urgency_weight": urgency_weight,
                "people_weight": people_weight,
                "category_weight": category_weight,
                "repeat_bonus": repeat_bonus,
            },
        }
