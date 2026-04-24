from difflib import SequenceMatcher


class AggregatorService:
    @staticmethod
    def normalize_entries(entries):
        normalized = []
        for entry in entries:
            text = (entry.get("text") or entry.get("headline") or "").strip()
            if not text:
                continue
            normalized.append(
                {
                    "text": text,
                    "source_type": entry.get("source_type", "manual"),
                    "source_label": entry.get("source_label", "Direct Input"),
                    "file_name": entry.get("file_name"),
                }
            )
        return normalized

    @staticmethod
    def deduplicate_entries(entries):
        merged = []
        for entry in entries:
            duplicate = next((item for item in merged if AggregatorService._is_similar(item["text"], entry["text"])), None)
            if duplicate:
                duplicate["sources"].append(
                    {
                        "source_type": entry["source_type"],
                        "source_label": entry["source_label"],
                        "text": entry["text"],
                        "file_name": entry.get("file_name"),
                    }
                )
                duplicate["source_count"] = len(duplicate["sources"])
                if len(entry["text"]) > len(duplicate["text"]):
                    duplicate["text"] = entry["text"]
            else:
                merged.append(
                    {
                        "text": entry["text"],
                        "sources": [
                            {
                                "source_type": entry["source_type"],
                                "source_label": entry["source_label"],
                                "text": entry["text"],
                                "file_name": entry.get("file_name"),
                            }
                        ],
                        "source_count": 1,
                    }
                )
        return merged

    @staticmethod
    def collect_entries(manual_text=None, file_entry=None, api_entries=None, scraped_entries=None):
        entries = []
        if manual_text:
            entries.append({"text": manual_text, "source_type": "manual", "source_label": "Manual Input"})
        if file_entry:
            entries.append(file_entry)
        entries.extend(api_entries or [])
        entries.extend(scraped_entries or [])
        return AggregatorService.deduplicate_entries(AggregatorService.normalize_entries(entries))

    @staticmethod
    def _is_similar(left_text, right_text):
        left = left_text.lower().strip()
        right = right_text.lower().strip()
        if left == right:
            return True
        return SequenceMatcher(None, left, right).ratio() >= 0.68
