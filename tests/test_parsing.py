from io import BytesIO

import pytest
from docx import Document

from candidates.services.parsing import ParsingError, extract_text, is_supported, normalize

LONG_LINE = "Python developer with five years of Django and PostgreSQL experience"


def make_pdf(text: str) -> bytes:
    """Build a minimal valid one-page PDF with the given (latin) text."""
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return out


def make_docx(paragraphs: list[str], table: list[list[str]] | None = None) -> bytes:
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    if table:
        t = doc.add_table(rows=len(table), cols=len(table[0]))
        for r, row in enumerate(table):
            for c, value in enumerate(row):
                t.cell(r, c).text = value
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_pdf_text_is_extracted():
    assert LONG_LINE in extract_text("cv.PDF", make_pdf(LONG_LINE))


def test_docx_paragraphs_and_tables_are_extracted():
    data = make_docx(["Мария Ковалёва", "Python-разработчик, 3 года опыта"], [["Навыки", "Django, PostgreSQL"]])
    text = extract_text("cv.docx", data)
    assert "Мария Ковалёва" in text
    assert "Навыки | Django, PostgreSQL" in text


def test_unsupported_format_raises_clear_error():
    with pytest.raises(ParsingError, match="не поддерживается"):
        extract_text("cv.txt", b"plain text")


def test_corrupted_files_raise_parsing_error():
    with pytest.raises(ParsingError):
        extract_text("cv.pdf", b"definitely not a pdf")
    with pytest.raises(ParsingError):
        extract_text("cv.docx", b"definitely not a docx")


def test_empty_document_is_rejected():
    with pytest.raises(ParsingError, match="почти нет текста"):
        extract_text("cv.docx", make_docx([""]))


def test_is_supported():
    assert is_supported("a.pdf") and is_supported("b.DOCX")
    assert not is_supported("c.doc") and not is_supported("noext")


def test_normalize_collapses_whitespace():
    assert normalize("a\xa0 \t b \n\n\n\n c ") == "a b\n\nc"
