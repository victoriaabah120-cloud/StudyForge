from io import BytesIO

from pypdf import PdfReader


def extract_text(file_bytes: bytes) -> tuple[str, int]:
    """Read a PDF from bytes. Returns (all text, number of pages)."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(reader.pages)