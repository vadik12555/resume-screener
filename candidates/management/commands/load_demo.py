from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from docx import Document

from candidates.demo_data import ALL_VACANCIES, PROFILES
from candidates.models import Candidate
from candidates.tasks import process_candidate
from vacancies.models import Vacancy

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo12345"


def _filename(name: str) -> str:
    return f"{name.replace(' ', '_')}.docx"


class Command(BaseCommand):
    help = "Создаёт демо-пользователя и 3 вакансии с выдуманными кандидатами."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--llm", action="store_true", help="Оценить резюме локальной LLM вместо готовых оценок"
        )
        parser.add_argument(
            "--if-empty", action="store_true", help="Ничего не делать, если демо уже загружено"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        User = get_user_model()
        user, created = User.objects.get_or_create(username=DEMO_USERNAME)
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        elif options["if_empty"] and Vacancy.objects.filter(owner=user).exists():
            self.stdout.write("Демо-данные уже загружены — пропускаю.")
            return

        total = 0
        with transaction.atomic():
            for vacancy_data, candidates in ALL_VACANCIES:
                Vacancy.objects.filter(owner=user, title=vacancy_data["title"]).delete()
                vacancy = Vacancy.objects.create(owner=user, **vacancy_data)
                for item in candidates:
                    self._create_candidate(vacancy, item, use_llm=options["llm"])
                total += len(candidates)

        files_dir = self._write_docx_files()
        self.stdout.write(self.style.SUCCESS(
            f"Готово: {len(ALL_VACANCIES)} вакансии и {total} кандидатов.\n"
            f"Вход: {DEMO_USERNAME} / {DEMO_PASSWORD}\n"
            f"DOCX-резюме для ручной загрузки: {files_dir}"
        ))

    def _create_candidate(self, vacancy: Vacancy, item: dict, *, use_llm: bool) -> None:
        candidate = Candidate(
            vacancy=vacancy, original_filename=_filename(item["name"]), resume_text=item["text"]
        )
        if use_llm:
            candidate.save()
            transaction.on_commit(lambda pk=candidate.pk: process_candidate.delay(pk))
            return
        candidate.name = item["name"]
        if item["name"] in PROFILES:
            (candidate.age, candidate.position, candidate.city,
             candidate.experience_years, candidate.skills) = PROFILES[item["name"]]
        candidate.score = item["score"]
        candidate.summary = item["summary"]
        candidate.strengths = item["strengths"]
        candidate.gaps = item["gaps"]
        candidate.questions = item["questions"]
        candidate.decision = item["decision"]
        candidate.processing = Candidate.Processing.DONE
        candidate.save()

    def _write_docx_files(self) -> Path:
        """Save resumes as real .docx so you can try the upload flow by hand."""
        out = Path(settings.BASE_DIR) / "demo_data"
        out.mkdir(exist_ok=True)
        for _, candidates in ALL_VACANCIES:
            for item in candidates:
                doc = Document()
                for line in item["text"].splitlines():
                    doc.add_paragraph(line)
                doc.save(out / _filename(item["name"]))
        return out
