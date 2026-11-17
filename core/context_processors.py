"""Shows the real state of the local LLM in the header."""

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

CACHE_KEY = "llm_status"
CACHE_SECONDS = 30


def llm_status(request: HttpRequest) -> dict[str, str]:
    if not request.user.is_authenticated:
        return {}
    status = cache.get(CACHE_KEY)
    if status is None:
        status = _check()
        cache.set(CACHE_KEY, status, CACHE_SECONDS)
    return {"llm_status": status}


def sidebar(request: HttpRequest) -> dict:
    if not request.user.is_authenticated:
        return {}
    from django.db.models import Count

    from vacancies.models import Vacancy

    return {
        "sidebar_vacancies": Vacancy.objects.filter(owner=request.user).annotate(n=Count("candidates"))[:12]
    }


def _check() -> str:
    """'ready' — model is loaded, 'loading' — Ollama up but model not pulled yet, 'offline'."""
    try:
        response = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=0.7)
        models = {m.get("name", "") for m in response.json().get("models", [])}
    except (requests.RequestException, ValueError):
        return "offline"
    return "ready" if settings.OLLAMA_MODEL in models else "loading"
