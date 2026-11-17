from django.conf import settings
from django.db import models


def _lines(text: str) -> list[str]:
    return [line.strip(" -•\t") for line in text.splitlines() if line.strip(" -•\t")]


class Vacancy(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vacancies"
    )
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    must_have = models.TextField("Обязательные навыки", help_text="По одному на строку")
    nice_to_have = models.TextField("Желательные навыки", blank=True, help_text="По одному на строку")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "вакансия"
        verbose_name_plural = "вакансии"

    def __str__(self) -> str:
        return self.title

    @property
    def must_have_list(self) -> list[str]:
        return _lines(self.must_have)

    @property
    def nice_to_have_list(self) -> list[str]:
        return _lines(self.nice_to_have)
