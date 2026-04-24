def build_task_payload(task_id, need, score, volunteer, issue_label):
    task_templates = {
        "food": "Deliver food supplies",
        "water": "Provide clean water support",
        "medical": "Deploy medical assistance",
        "education": "Deliver education kits",
        "shelter": "Arrange temporary shelter support",
        "general": "Dispatch field assessment team",
    }

    action = task_templates.get(need["category"], task_templates["general"])

    return {
        "id": task_id,
        "category": need["category"],
        "issue": issue_label,
        "headline": f"{issue_label} in {need['location']}",
        "priority": score["priority"],
        "priority_score": score["priority_score"],
        "confidence": need.get("confidence", "Medium"),
        "location": need["location"],
        "people_affected": need["people_affected"],
        "source_count": need.get("source_count", 1),
        "sources": need.get("sources", []),
        "assigned_to": volunteer["assigned_volunteer"],
        "assigned_volunteer_id": volunteer["assigned_volunteer_id"],
        "assignment_confidence": volunteer["confidence"],
        "task": f"{action} to {need['location']}",
        "status": "Action Required",
    }
