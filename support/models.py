from django.conf import settings
from django.db import models


class Ticket(models.Model):
    class Category(models.TextChoices):
        QUESTION = "question", "Вопрос по работе сервиса"
        BUG = "bug", "Что-то не работает"
        IDEA = "idea", "Предложение по улучшению"

    class Status(models.TextChoices):
        OPEN = "open", "В работе"
        ANSWERED = "answered", "Есть ответ"
        CLOSED = "closed", "Закрыто"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    category = models.CharField("Тема", max_length=20, choices=Category.choices, default=Category.QUESTION)
    subject = models.CharField("Кратко", max_length=150)
    message = models.TextField("Сообщение")
    answer = models.TextField("Ответ поддержки", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "обращение"
        verbose_name_plural = "обращения в поддержку"

    def __str__(self) -> str:
        return f"#{self.pk} {self.subject}"
