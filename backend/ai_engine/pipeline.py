from uuid import uuid4

from ai_engine.extractor import NeedExtractor
from ai_engine.matcher import VolunteerMatcher
from ai_engine.scorer import PriorityScorer
from database.db import get_store
from models.task_model import build_task_payload


class AIPipeline:
    ISSUE_LABELS = {
        "food": "Food shortage",
        "water": "Water shortage",
        "medical": "Medical support needed",
        "education": "Education support needed",
        "shelter": "Shelter support needed",
        "general": "Community support needed",
    }

    def __init__(self):
        self.extractor = NeedExtractor()
        self.scorer = PriorityScorer()
        self.matcher = VolunteerMatcher()

    def run(self, normalized_entry):
        clean_text = normalized_entry["text"]
        need = self.extractor.extract(clean_text)
        need["source_count"] = normalized_entry.get("source_count", 1)
        need["sources"] = normalized_entry.get("sources", [])
        need["confidence"] = "High" if need["source_count"] >= 2 else "Medium"
        score = self.scorer.score(need)
        volunteer = self.matcher.match(need, get_store().get_volunteers())
        issue = self.ISSUE_LABELS.get(need["category"], self.ISSUE_LABELS["general"])
        task = build_task_payload(
            task_id=str(uuid4()),
            need=need,
            score=score,
            volunteer=volunteer,
            issue_label=issue,
        )

        source_labels = [item.get("source_label", "Unknown source") for item in need["sources"]]
        people_label = (
            f"{need['people_affected']} people"
            if need["people_affected"]
            else "People count needs confirmation"
        )

        return {
            "headline": f"{issue} in {need['location']}",
            "issue": issue,
            "category": need["category"],
            "location": need["location"],
            "people_affected": need["people_affected"],
            "affected_summary": people_label,
            "urgency": need["urgency"],
            "ai_service_used": need.get("ai_service", "Rule-based NLP fallback"),
            "extraction_method": need.get("extraction_method", "rule_based"),
            "confidence": need["confidence"],
            "source_count": need["source_count"],
            "source_labels": source_labels,
            "source_details": need["sources"],
            "priority_score": score["priority_score"],
            "priority": score["priority"],
            "assigned_volunteer": volunteer["assigned_volunteer"],
            "assigned_volunteer_id": volunteer["assigned_volunteer_id"],
            "volunteer_confidence": volunteer["confidence"],
            "recommended_action": task["task"],
            "task": task["task"],
            "status": task["status"],
            "score_breakdown": score["score_breakdown"],
            "task_record": task,
        }
