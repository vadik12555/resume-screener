from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from candidates.models import Candidate

from .forms import VacancyForm
from .models import Vacancy


def get_own_vacancy(request: HttpRequest, pk: int) -> Vacancy:
    """Only the owner may see a vacancy; everyone else gets 404 (not 403),
    so we don't even reveal that the vacancy exists."""
    return get_object_or_404(Vacancy, pk=pk, owner=request.user)


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    vacancies = Vacancy.objects.filter(owner=request.user).annotate(
        total=Count("candidates"),
        avg_score=Avg("candidates__score"),
        top_score=Max("candidates__score"),
        invited=Count("candidates", filter=Q(candidates__decision=Candidate.Decision.INVITED)),
    )
    candidates = Candidate.objects.filter(vacancy__owner=request.user)
    stats = {
        "vacancies": vacancies.count(),
        "candidates": candidates.count(),
        "strong": candidates.filter(score__gte=75).count(),
        "invited": candidates.filter(decision=Candidate.Decision.INVITED).count(),
    }
    return render(request, "vacancies/dashboard.html", {"vacancies": vacancies, "stats": stats})


@login_required
def create(request: HttpRequest) -> HttpResponse:
    form = VacancyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        vacancy = form.save(commit=False)
        vacancy.owner = request.user
        vacancy.save()
        messages.success(request, "Вакансия создана. Загрузите резюме кандидатов.")
        return redirect("vacancy_detail", pk=vacancy.pk)
    return render(request, "vacancies/form.html", {"form": form})


@login_required
def edit(request: HttpRequest, pk: int) -> HttpResponse:
    vacancy = get_own_vacancy(request, pk)
    form = VacancyForm(request.POST or None, instance=vacancy)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Изменения сохранены.")
        return redirect("vacancy_detail", pk=vacancy.pk)
    return render(request, "vacancies/form.html", {"form": form, "vacancy": vacancy})


@login_required
@require_POST
def delete(request: HttpRequest, pk: int) -> HttpResponse:
    get_own_vacancy(request, pk).delete()
    messages.success(request, "Вакансия удалена.")
    return redirect("dashboard")


@login_required
def detail(request: HttpRequest, pk: int) -> HttpResponse:
    vacancy = get_own_vacancy(request, pk)
    qs = vacancy.candidates.all()
    context = {
        "vacancy": vacancy,
        "candidates": qs,
        "progress": progress_for(vacancy),
        "stats": qs.aggregate(
            total=Count("id"),
            avg=Avg("score"),
            invited=Count("id", filter=Q(decision=Candidate.Decision.INVITED)),
            rejected=Count("id", filter=Q(decision=Candidate.Decision.REJECTED)),
        ),
        "decisions": Candidate.Decision.choices,
    }
    return render(request, "vacancies/detail.html", context)


def progress_for(vacancy: Vacancy) -> dict[str, int]:
    counts = vacancy.candidates.aggregate(
        total=Count("id"),
        active=Count(
            "id",
            filter=Q(processing__in=[Candidate.Processing.PENDING, Candidate.Processing.PROCESSING]),
        ),
        errors=Count("id", filter=Q(processing=Candidate.Processing.ERROR)),
    )
    total, active = counts["total"], counts["active"]
    done = total - active
    counts["done"] = done
    counts["percent"] = round(done / total * 100) if total else 100
    return counts
