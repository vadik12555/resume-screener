"""Export a vacancy ranking to Excel."""

from collections.abc import Iterable
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from candidates.models import Candidate

HEADERS = [
    ("Место", 8),
    ("Кандидат", 26),
    ("Оценка", 10),
    ("Статус", 13),
    ("Кратко", 45),
    ("Сильные стороны", 45),
    ("Чего не хватает", 45),
    ("Вопросы для интервью", 55),
    ("Заметки HR", 35),
    ("Файл", 24),
]
FILLS = {
    "good": PatternFill("solid", fgColor="D1FAE5"),
    "mid": PatternFill("solid", fgColor="FEF3C7"),
    "low": PatternFill("solid", fgColor="FFE4E6"),
}


def _bullets(items: list[str]) -> str:
    return "\n".join(f"• {item}" for item in items)


def _tone(score: int) -> str:
    return "good" if score >= 75 else "mid" if score >= 50 else "low"


def build_ranking_xlsx(title: str, candidates: Iterable[Candidate]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Рейтинг"

    for col, (header, width) in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="4F46E5")
        cell.alignment = Alignment(vertical="center")
        ws.column_dimensions[cell.column_letter].width = width
    ws.freeze_panes = "A2"

    for rank, c in enumerate(candidates, start=1):
        row = [
            rank,
            c.display_name,
            c.score,
            c.get_decision_display(),
            c.summary or c.error,
            _bullets(c.strengths),
            _bullets(c.gaps),
            "\n".join(f"{i}. {q}" for i, q in enumerate(c.questions, 1)),
            c.notes,
            c.original_filename,
        ]
        ws.append(row)
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        if c.score is not None:
            score_cell = ws.cell(row=ws.max_row, column=3)
            score_cell.fill = FILLS[_tone(c.score)]
            score_cell.font = Font(bold=True)

    ws.auto_filter.ref = ws.dimensions
    wb.properties.title = title
    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
