class ScraperService:
    SAMPLE_HTML = """
    <html>
      <body>
        <article>Villagers struggling due to lack of water in Village A after pipeline damage.</article>
        <article>Flooding near Area Sunrise has left families needing temporary shelter and food.</article>
      </body>
    </html>
    """

    @staticmethod
    def fetch_news_signals():
        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get("https://reliefweb.int/updates", timeout=4)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            articles = [item.get_text(" ", strip=True) for item in soup.select("article")[:3]]
            cleaned = [text for text in articles if text]
            return [
                {"text": text, "source_type": "scraped", "source_label": "ReliefWeb Updates"}
                for text in cleaned
            ] or ScraperService._fallback_data()
        except Exception:
            return ScraperService._fallback_data()

    @staticmethod
    def _fallback_data():
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(ScraperService.SAMPLE_HTML, "html.parser")
        return [
            {"text": article.get_text(" ", strip=True), "source_type": "scraped", "source_label": "Sample News Scrape"}
            for article in soup.select("article")
        ]
