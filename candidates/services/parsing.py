"""Extract plain text from uploaded resumes (PDF / DOCX)."""

import re
import zipfile
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader
from pypdf.errors import PdfReadError

SUPPORTED_EXTENSIONS = (".pdf", ".docx")
MIN_TEXT_LENGTH = 50


class ParsingError(Exception):
    """Raised with a user-friendly message when a file can't be read."""


def is_supported(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def extract_text(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        text = _from_pdf(data)
    elif ext == ".docx":
        text = _from_docx(data)
    else:
        raise ParsingError(f"Формат «{ext or 'без расширения'}» не поддерживается. Загрузите PDF или DOCX.")

    text = normalize(text)
    if len(text) < MIN_TEXT_LENGTH:
        raise ParsingError(
            "В файле почти нет текста. Возможно, это скан — нужен PDF с текстовым слоем."
        )
    return text


def normalize(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _from_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except (PdfReadError, ValueError, KeyError) as exc:
        raise ParsingError("Не удалось прочитать PDF: файл повреждён или защищён.") from exc


def _from_docx(data: bytes) -> str:
    try:
        doc = Document(BytesIO(data))
    except (zipfile.BadZipFile, KeyError, ValueError) as exc:
        raise ParsingError("Не удалось прочитать DOCX: файл повреждён.") from exc

    parts = [p.text for p in doc.paragraphs]
    # Many resumes are laid out with tables — read them too.
    for table in doc.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(parts)
