import re


class ProcessingService:
    @staticmethod
    def clean_text(text):
        text = text or ""
        text = text.replace("\x00", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
