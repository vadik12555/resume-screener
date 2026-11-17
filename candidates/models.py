from django.db import models
from django.db.models import F

from vacancies.models import Vacancy


def years(n: int) -> str:
    """Russian plural: 1 год, 3 года, 35 лет, 11 лет."""
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} год"
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return f"{n} года"
    return f"{n} лет"


class Candidate(models.Model):
    class Processing(models.TextChoices):
        PENDING = "pending", "В очереди"
        PROCESSING = "processing", "Анализ"
        DONE = "done", "Готово"
        ERROR = "error", "Ошибка"

    class Decision(models.TextChoices):
        NEW = "new", "Новый"
        INVITED = "invited", "Приглашён"
        REJECTED = "rejected", "Отказ"

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="candidates")
    file = models.FileField(upload_to="resumes/%Y/%m/", blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    resume_text = models.TextField(blank=True)

    processing = models.CharField(
        max_length=20, choices=Processing.choices, default=Processing.PENDING
    )
    decision = models.CharField(max_length=20, choices=Decision.choices, default=Decision.NEW)
    error = models.TextField(blank=True)
    notes = models.TextField("Заметки HR", blank=True)

    # Filled by the LLM
    name = models.CharField(max_length=200, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    position = models.CharField("Должность", max_length=150, blank=True)
    city = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveSmallIntegerField(null=True, blank=True)
    skills = models.JSONField(default=list, blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    summary = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    gaps = models.JSONField(default=list, blank=True)
    questions = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [F("score").desc(nulls_last=True), "-created_at"]
        verbose_name = "кандидат"
        verbose_name_plural = "кандидаты"

    def __str__(self) -> str:
        return self.display_name

    @property
    def display_name(self) -> str:
        return self.name or self.original_filename or f"Кандидат #{self.pk}"

    @property
    def age_label(self) -> str:
        """Russian plural: 21 год, 23 года, 35 лет."""
        return "" if self.age is None else years(self.age)

    @property
    def experience_label(self) -> str:
        if self.experience_years is None:
            return ""
        return "без опыта" if self.experience_years == 0 else f"опыт {years(self.experience_years)}"

    @property
    def is_active(self) -> bool:
        return self.processing in (self.Processing.PENDING, self.Processing.PROCESSING)
