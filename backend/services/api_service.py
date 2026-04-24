class APIService:
    SAMPLE_API_DATA = [
        {
            "headline": "Flood in Area Sunrise affecting 200 people and damaging homes",
            "region": "Area Sunrise",
            "impact": 200,
            "need": "shelter",
        },
        {
            "headline": "Water shortage reported in Village A affecting 120 villagers",
            "region": "Village A",
            "impact": 120,
            "need": "water",
        },
    ]

    @staticmethod
    def fetch_external_data():
        try:
            import requests

            response = requests.get("https://api.reliefweb.int/v1/reports?appname=ngo-platform&limit=2", timeout=4)
            response.raise_for_status()
            payload = response.json()
            data = []
            for item in payload.get("data", [])[:2]:
                fields = item.get("fields", {})
                title = fields.get("title") or "Disaster update"
                source = (fields.get("source") or [{}])[0].get("shortname", "ReliefWeb")
                data.append({"text": f"{title}. Source: {source}", "source_type": "api", "source_label": "ReliefWeb"})
            return data or APIService._fallback_data()
        except Exception:
            return APIService._fallback_data()

    @staticmethod
    def _fallback_data():
        return [
            {
                "text": f"{item['headline']} in {item['region']}. {item['impact']} people may need {item['need']} support.",
                "source_type": "api",
                "source_label": "Sample Disaster Feed",
            }
            for item in APIService.SAMPLE_API_DATA
        ]
