import json
from copy import deepcopy
from datetime import datetime
from difflib import SequenceMatcher
from uuid import uuid4

from config import LOCAL_DB_FILE, MONGO_DB_NAME, MONGO_URI
from ai_engine.scorer import PriorityScorer
from models.volunteer_model import seed_volunteers

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None


class DataStore:
    def __init__(self):
        self.last_updated = datetime.utcnow().isoformat() + "Z"
        self.use_mongo = False
        self.client = None
        self.db = None
        self._initialize()

    def _initialize(self):
        LOCAL_DB_FILE.parent.mkdir(parents=True, exist_ok=True)

        if MongoClient:
            try:
                self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
                self.client.server_info()
                self.db = self.client[MONGO_DB_NAME]
                self.use_mongo = True
                self._ensure_seed_data()
                return
            except Exception:
                self.use_mongo = False

        if not LOCAL_DB_FILE.exists():
            self._write_local(
                {
                    "volunteers": seed_volunteers(),
                    "tasks": [],
                    "processed_cases": [],
                    "last_updated": self.last_updated,
                }
            )

    def _ensure_seed_data(self):
        seeded_ids = {item["id"] for item in seed_volunteers()}
        existing_ids = {item["id"] for item in self.db.volunteers.find({}, {"id": 1, "_id": 0})}

        missing = [item for item in seed_volunteers() if item["id"] not in existing_ids]
        if missing:
            self.db.volunteers.insert_many(missing)

        stale_ids = existing_ids - seeded_ids
        if stale_ids:
            self.db.volunteers.delete_many({"id": {"$in": list(stale_ids)}})

    def _read_local(self):
        payload = json.loads(LOCAL_DB_FILE.read_text(encoding="utf-8"))
        self.last_updated = payload.get("last_updated", self.last_updated)
        return payload

    def _write_local(self, payload):
        self.last_updated = datetime.utcnow().isoformat() + "Z"
        payload["last_updated"] = self.last_updated
        LOCAL_DB_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def create_case(self, case_payload):
        record = deepcopy(case_payload)
        record["case_id"] = str(uuid4())
        record["created_at"] = datetime.utcnow().isoformat() + "Z"

        existing_task = self._find_duplicate_task(record["task_record"])
        if existing_task:
            return self._merge_existing_issue(record, existing_task)

        if self.use_mongo:
            self.db.processed_cases.insert_one(record)
            self.db.tasks.insert_one(deepcopy(record["task_record"]))
            self.last_updated = datetime.utcnow().isoformat() + "Z"
            return record

        payload = self._read_local()
        payload["processed_cases"].append(record)
        payload["tasks"].append(deepcopy(record["task_record"]))
        self._write_local(payload)
        return record

    def _find_duplicate_task(self, incoming_task):
        tasks = self.get_tasks()
        for task in tasks:
            same_category = task.get("category") == incoming_task.get("category")
            same_location = task.get("location") == incoming_task.get("location")
            similar_task = SequenceMatcher(None, task.get("task", "").lower(), incoming_task.get("task", "").lower()).ratio() >= 0.72
            if same_category and same_location and similar_task:
                return task
        return None

    def _merge_existing_issue(self, record, existing_task):
        merged_sources = existing_task.get("sources", []) + record["task_record"].get("sources", [])
        source_count = len(merged_sources) or max(existing_task.get("source_count", 1), record["task_record"].get("source_count", 1))
        existing_task["sources"] = merged_sources
        existing_task["source_count"] = source_count
        existing_task["confidence"] = "High" if source_count >= 2 else existing_task.get("confidence", "Medium")
        existing_task["people_affected"] = max(existing_task.get("people_affected", 0), record["task_record"]["people_affected"])
        rescored = PriorityScorer().score(
            {
                "urgency": record.get("urgency", "moderate"),
                "people_affected": existing_task["people_affected"],
                "category": existing_task["category"],
                "source_count": source_count,
            }
        )
        existing_task["priority_score"] = rescored["priority_score"]
        existing_task["priority"] = rescored["priority"]

        if self.use_mongo:
            self.db.tasks.update_one({"id": existing_task["id"]}, {"$set": existing_task})
            self.db.processed_cases.insert_one(record)
            self.last_updated = datetime.utcnow().isoformat() + "Z"
            return record

        payload = self._read_local()
        for index, task in enumerate(payload["tasks"]):
            if task["id"] == existing_task["id"]:
                payload["tasks"][index] = existing_task
                break
        payload["processed_cases"].append(record)
        self._write_local(payload)
        return record

    def get_tasks(self):
        if self.use_mongo:
            return list(self.db.tasks.find({}, {"_id": 0}))
        return self._read_local()["tasks"]

    def get_volunteers(self):
        if self.use_mongo:
            return list(self.db.volunteers.find({}, {"_id": 0}))
        return self._read_local()["volunteers"]

    def assign_volunteer(self, task_id, volunteer_id):
        volunteers = self.get_volunteers()
        volunteer = next((item for item in volunteers if item["id"] == volunteer_id), None)
        if not volunteer:
            return None

        if self.use_mongo:
            task = self.db.tasks.find_one({"id": task_id}, {"_id": 0})
            if not task:
                return None
            task["assigned_to"] = volunteer["name"]
            task["assigned_volunteer_id"] = volunteer["id"]
            task["status"] = "Assigned"
            self.db.tasks.update_one({"id": task_id}, {"$set": task})
            self.last_updated = datetime.utcnow().isoformat() + "Z"
            return task

        payload = self._read_local()
        task = next((item for item in payload["tasks"] if item["id"] == task_id), None)
        if not task:
            return None
        task["assigned_to"] = volunteer["name"]
        task["assigned_volunteer_id"] = volunteer["id"]
        task["status"] = "Assigned"
        self._write_local(payload)
        return deepcopy(task)

    def update_task_status(self, task_id, status):
        valid_statuses = {"Action Required", "Assigned", "In Progress", "Completed"}
        if status not in valid_statuses:
            return "invalid_status"

        if self.use_mongo:
            task = self.db.tasks.find_one({"id": task_id}, {"_id": 0})
            if not task:
                return None
            task["status"] = status
            self.db.tasks.update_one({"id": task_id}, {"$set": task})
            self.last_updated = datetime.utcnow().isoformat() + "Z"
            return task

        payload = self._read_local()
        task = next((item for item in payload["tasks"] if item["id"] == task_id), None)
        if not task:
            return None
        task["status"] = status
        self._write_local(payload)
        return deepcopy(task)

    def get_dashboard_snapshot(self):
        tasks = self.get_tasks()
        priority_counts = {"Very High": 0, "High": 0, "Medium": 0, "Low": 0}
        location_needs = {}
        category_needs = {}
        volunteers_available = sum(1 for volunteer in self.get_volunteers() if volunteer["availability"])
        people_impacted = 0
        completed_tasks = 0
        assigned_tasks = 0

        for task in tasks:
            priority_counts[task["priority"]] = priority_counts.get(task["priority"], 0) + 1
            location_needs[task["location"]] = location_needs.get(task["location"], 0) + 1
            category_needs[task["category"]] = category_needs.get(task["category"], 0) + 1
            people_impacted += task["people_affected"]
            if task["status"] == "Completed":
                completed_tasks += 1
            if task.get("assigned_volunteer_id"):
                assigned_tasks += 1

        open_tasks = max(0, len(tasks) - completed_tasks)
        volunteer_coverage = round((assigned_tasks / len(tasks)) * 100, 1) if tasks else 0

        return {
            "summary": {
                "total_tasks": len(tasks),
                "open_tasks": open_tasks,
                "very_high_priority_tasks": priority_counts.get("Very High", 0),
                "high_priority_tasks": priority_counts.get("High", 0),
                "volunteers_available": volunteers_available,
                "people_impacted": people_impacted,
                "completed_tasks": completed_tasks,
                "volunteer_coverage": volunteer_coverage,
            },
            "priority_breakdown": priority_counts,
            "category_breakdown": category_needs,
            "location_needs": [
                {"location": location, "needs_count": count}
                for location, count in sorted(location_needs.items(), key=lambda item: item[1], reverse=True)
            ],
            "recent_cases": self.get_recent_cases(),
            "last_updated": self.last_updated,
            "database_mode": "mongo" if self.use_mongo else "local_fallback",
        }

    def get_recent_cases(self):
        if self.use_mongo:
            return list(self.db.processed_cases.find({}, {"_id": 0}).sort("created_at", -1).limit(5))
        payload = self._read_local()
        return deepcopy(payload["processed_cases"][-5:])[::-1]


store = None


def initialize_database():
    global store
    if store is None:
        store = DataStore()
    return store


def get_store():
    return initialize_database()
