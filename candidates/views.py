from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from vacancies.models import Vacancy
from vacancies.views import get_own_vacancy, progress_for

from .models import Candidate
from .services.export import build_ranking_xlsx
from .services.parsing import is_supported
from .tasks import process_candidate


def get_own_candidate(request: HttpRequest, pk: int) -> Candidate:
    return get_object_or_404(
        Candidate.objects.select_related("vacancy"), pk=pk, vacancy__owner=request.user
    )


def _enqueue(candidate: Candidate) -> None:
    # Start the task only after the DB transaction commits,
    # otherwise the worker may not see the new row yet.
    transaction.on_commit(lambda: process_candidate.delay(candidate.pk))


def filter_candidates(request: HttpRequest, vacancy: Vacancy) -> QuerySet[Candidate]:
    qs = vacancy.candidates.all()
    min_score = request.GET.get("min_score", "")
    if min_score.isdigit() and int(min_score) > 0:
        qs = qs.filter(score__gte=int(min_score))
    decision = request.GET.get("decision", "")
    if decision in Candidate.Decision.values:
        qs = qs.filter(decision=decision)
    return qs


@login_required
def all_candidates(request: HttpRequest) -> HttpResponse:
    """Every candidate of the current HR across all vacancies, with search."""
    qs = Candidate.objects.filter(vacancy__owner=request.user).select_related("vacancy")
    query = request.GET.get("q", "").strip()
    vacancy_id = request.GET.get("vacancy", "")
    if vacancy_id.isdigit():
        qs = qs.filter(vacancy_id=int(vacancy_id))
    decision = request.GET.get("decision", "")
    if decision in Candidate.Decision.values:
        qs = qs.filter(decision=decision)
    candidates = list(qs)
    if query:
        # Case-insensitive search in Python: SQLite's LIKE ignores case only for ASCII,
        # so "иван" wouldn't match "Иван". An HR's candidate list is small enough for this.
        needle = query.casefold()
        candidates = [
            c for c in candidates
            if needle in f"{c.display_name} {c.position} {c.city} {' '.join(c.skills)} {c.summary}".casefold()
        ]
    context = {
        "candidates": candidates,
        "vacancies": Vacancy.objects.filter(owner=request.user),
        "decisions": Candidate.Decision.choices,
        "q": query,
    }
    is_htmx = request.headers.get("HX-Request") == "true"
    return render(request, "candidates/_all_rows.html" if is_htmx else "candidates/all.html", context)


@login_required
@require_POST
def upload(request: HttpRequest, pk: int) -> HttpResponse:
    vacancy = get_own_vacancy(request, pk)
    files = request.FILES.getlist("files")
    if not files:
        messages.error(request, "Выберите хотя бы один файл.")
        return redirect("vacancy_detail", pk=pk)

    max_bytes = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
    queued = 0
    with transaction.atomic():
        for f in files:
            candidate = Candidate(vacancy=vacancy, original_filename=f.name)
            if not is_supported(f.name):
                candidate.processing = Candidate.Processing.ERROR
                candidate.error = "Поддерживаются только PDF и DOCX."
            elif f.size > max_bytes:
                candidate.processing = Candidate.Processing.ERROR
                candidate.error = f"Файл больше {settings.MAX_RESUME_SIZE_MB} МБ."
            else:
                candidate.file = f
            candidate.save()
            if candidate.processing == Candidate.Processing.PENDING:
                _enqueue(candidate)
                queued += 1

    messages.success(request, f"Загружено резюме: {len(files)}. В обработке: {queued}.")
    return redirect("vacancy_detail", pk=pk)


@login_required
def candidates_table(request: HttpRequest, pk: int) -> HttpResponse:
    vacancy = get_own_vacancy(request, pk)
    return render(
        request,
        "candidates/_table.html",
        {"vacancy": vacancy, "candidates": filter_candidates(request, vacancy)},
    )


@login_required
def progress(request: HttpRequest, pk: int) -> HttpResponse:
    vacancy = get_own_vacancy(request, pk)
    response = render(
        request, "candidates/_progress.html", {"vacancy": vacancy, "progress": progress_for(vacancy)}
    )
    response["HX-Trigger"] = "candidatesUpdated"  # tell the table to refresh
    return response


@login_required
def detail(request: HttpRequest, pk: int) -> HttpResponse:
    candidate = get_own_candidate(request, pk)
    is_htmx = request.headers.get("HX-Request") == "true"
    template = "candidates/_detail_body.html" if is_htmx else "candidates/detail.html"
    return render(request, template, {"c": candidate, "decisions": Candidate.Decision.choices})


@login_required
@require_POST
def set_decision(request: HttpRequest, pk: int) -> HttpResponse:
    candidate = get_own_candidate(request, pk)
    decision = request.POST.get("decision", "")
    if decision in Candidate.Decision.values:
        candidate.decision = decision
        candidate.save(update_fields=["decision"])
    return render(
        request, "candidates/_decision.html", {"c": candidate, "decisions": Candidate.Decision.choices}
    )


@login_required
@require_POST
def save_notes(request: HttpRequest, pk: int) -> HttpResponse:
    candidate = get_own_candidate(request, pk)
    candidate.notes = request.POST.get("notes", "")[:5000]
    candidate.save(update_fields=["notes"])
    return HttpResponse('<span class="text-emerald-600">✓ Сохранено</span>')


@login_required
@require_POST
def retry(request: HttpRequest, pk: int) -> HttpResponse:
    candidate = get_own_candidate(request, pk)
    if not candidate.file and not candidate.resume_text:
        messages.error(request, "Файл не был загружен — повторить анализ нельзя.")
        return redirect("candidate_detail", pk=pk)
    candidate.processing = Candidate.Processing.PENDING
    candidate.error = ""
    candidate.save(update_fields=["processing", "error"])
    _enqueue(candidate)
    return redirect("candidate_detail", pk=pk)


@login_required
@require_POST
def delete(request: HttpRequest, pk: int) -> HttpResponse:
    candidate = get_own_candidate(request, pk)
    vacancy_pk = candidate.vacancy_id
    candidate.file.delete(save=False)
    candidate.delete()
    messages.success(request, "Кандидат удалён.")
    return redirect("vacancy_detail", pk=vacancy_pk)


@login_required
def export(request: HttpRequest, pk: int) -> HttpResponse:
    vacancy = get_own_vacancy(request, pk)
    content = build_ranking_xlsx(vacancy.title, filter_candidates(request, vacancy))
    filename = f"Рейтинг — {vacancy.title}.xlsx"
    response = HttpResponse(
        content, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
    return response
