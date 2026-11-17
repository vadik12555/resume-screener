from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import TicketForm

FAQ = [
    (
        "Как считается оценка кандидата?",
        "Модель сравнивает резюме с требованиями вакансии: обязательные навыки дают около 70% балла, "
        "желательные — около 20%, опыт и качество резюме — 10%. Если нет ни одного обязательного навыка, "
        "балл не выше 30.",
    ),
    (
        "Куда уходят резюме кандидатов?",
        "Никуда. ИИ-модель работает на том же сервере, что и сервис. Данные не передаются во внешние API.",
    ),
    (
        "Какие файлы можно загружать?",
        "PDF с текстовым слоем и DOCX, до 5 МБ каждый. Сканы-картинки распознать не получится — "
        "кандидат получит статус «Ошибка» с объяснением.",
    ),
    (
        "Почему кандидат долго «в очереди»?",
        "На обычном процессоре модель тратит 20–60 секунд на резюме, файлы обрабатываются по очереди. "
        "Страницу можно закрыть — обработка продолжится.",
    ),
    (
        "Анализ завершился ошибкой — что делать?",
        "Откройте карточку кандидата и нажмите «Повторить анализ». Если ошибка повторяется — напишите нам.",
    ),
]


@login_required
def index(request: HttpRequest) -> HttpResponse:
    form = TicketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        ticket.user = request.user
        ticket.save()
        messages.success(request, f"Обращение #{ticket.pk} отправлено. Ответ появится на этой странице.")
        return redirect("support")
    return render(
        request,
        "support/index.html",
        {"form": form, "faq": FAQ, "tickets": request.user.tickets.all()},
    )
