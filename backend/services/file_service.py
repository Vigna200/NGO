from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename


class FileService:
    def __init__(self, upload_folder):
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def save_upload(self, uploaded_file):
        file_name = f"{uuid4()}_{secure_filename(uploaded_file.filename)}"
        destination = self.upload_folder / file_name
        uploaded_file.save(destination)
        return destination

    def extract_text(self, file_path):
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._extract_pdf_text(file_path)
        if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}:
            return self._extract_image_text(file_path)
        return file_path.read_text(encoding="utf-8", errors="ignore")

    def describe_source(self, file_path):
        suffix = file_path.suffix.lower()
        source_kind = {
            ".pdf": "PDF report",
            ".png": "Image report",
            ".jpg": "Image report",
            ".jpeg": "Image report",
            ".bmp": "Image report",
            ".tiff": "Image report",
            ".txt": "Text file",
        }.get(suffix, "Uploaded file")

        return {
            "source_type": "file",
            "source_label": source_kind,
            "file_name": file_path.name,
        }

    def _extract_pdf_text(self, file_path):
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return "PyPDF2 is not installed. Install backend dependencies to enable PDF extraction."

        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    def _extract_image_text(self, file_path):
        try:
            import pytesseract
            from PIL import Image
        except ImportError:
            return "OCR dependencies missing. Install pytesseract and Pillow to extract image text."

        return pytesseract.image_to_string(Image.open(file_path)).strip()
