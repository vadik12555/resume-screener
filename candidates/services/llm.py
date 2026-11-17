"""Resume evaluation with a local LLM (Ollama).

Flow: build prompt -> ask the model for JSON (Ollama `format` = our JSON schema)
-> validate with pydantic -> if invalid, ask once more showing the error
-> if still invalid, raise LLMError with a clear message.
"""

import json
from typing import Protocol

import requests
from django.conf import settings
from pydantic import BaseModel, Field, ValidationError

MAX_ATTEMPTS = 2
MAX_RESUME_CHARS = 12_000


class Evaluation(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    age: int | None = Field(default=None, ge=14, le=80)
    position: str = Field(default="", max_length=150)
    city: str = Field(default="", max_length=100)
    experience_years: int | None = Field(default=None, ge=0, le=50)
    skills: list[str] = Field(default_factory=list, max_length=12)
    score: int = Field(ge=0, le=100)
    summary: str = Field(min_length=1, max_length=600)
    strengths: list[str] = Field(min_length=1, max_length=6)
    gaps: list[str] = Field(max_length=6)
    questions: list[str] = Field(min_length=3, max_length=3)


class LLMError(Exception):
    """Final, user-facing error: the evaluation could not be produced."""


class InvalidResponse(Exception):
    """Model answered, but not with valid JSON matching the schema."""


class VacancyLike(Protocol):
    title: str
    description: str
    must_have_list: list[str]
    nice_to_have_list: list[str]


SYSTEM_PROMPT = """Ты — опытный технический рекрутер. Оцени резюме кандидата относительно вакансии.

Правила:
- Опирайся только на факты из резюме, ничего не выдумывай.
- score от 0 до 100: обязательные навыки весят больше всего (около 70%), желательные — около 20%, опыт и качество резюме — 10%.
  Нет ни одного обязательного навыка — score не выше 30.
- name — имя и фамилия кандидата из резюме; если их нет — "Не указано".
- age — возраст числом, если указан или вычисляется из даты рождения, иначе null.
- position — текущая или желаемая должность, коротко (например, "Backend-разработчик").
- city — город, если указан, иначе пустая строка.
- experience_years — полных лет коммерческого опыта по профессии (0, если нет), null, если не понять.
- skills — до 10 ключевых технологий кандидата, коротко ("Python", "Django", "PostgreSQL").
- summary — 1–2 предложения: кто это и подходит ли он.
- strengths — до 5 конкретных сильных сторон под эту вакансию.
- gaps — чего не хватает относительно требований (пустой список, если всего хватает).
- questions — ровно 3 вопроса для собеседования, проверяющих слабые места и заявленный опыт.
- Пиши по-русски. Отвечай ТОЛЬКО JSON-объектом с полями: name, age, position, city, experience_years, skills, score, summary, strengths, gaps, questions."""


def build_user_prompt(vacancy: VacancyLike, resume_text: str) -> str:
    must = "\n".join(f"- {s}" for s in vacancy.must_have_list) or "- не указаны"
    nice = "\n".join(f"- {s}" for s in vacancy.nice_to_have_list) or "- не указаны"
    return (
        f"ВАКАНСИЯ: {vacancy.title}\n{vacancy.description}\n\n"
        f"ОБЯЗАТЕЛЬНЫЕ НАВЫКИ:\n{must}\n\nЖЕЛАТЕЛЬНЫЕ НАВЫКИ:\n{nice}\n\n"
        f"РЕЗЮМЕ:\n{resume_text[:MAX_RESUME_CHARS]}"
    )


def parse_evaluation(raw: str) -> Evaluation:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InvalidResponse("ответ не является корректным JSON") from exc
    try:
        return Evaluation.model_validate(data)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(p) for p in err['loc']) or 'объект'}: {err['msg']}" for err in exc.errors()
        )
        raise InvalidResponse(problems) from exc


def evaluate_resume(vacancy: VacancyLike, resume_text: str) -> Evaluation:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(vacancy, resume_text)},
    ]
    last_problem = ""
    for _ in range(MAX_ATTEMPTS):
        raw = _chat(messages)
        try:
            return parse_evaluation(raw)
        except InvalidResponse as exc:
            last_problem = str(exc)
            messages += [
                {"role": "assistant", "content": raw},
                {
                    "role": "user",
                    "content": f"Ответ некорректен: {last_problem}. "
                    "Верни исправленный JSON строго по схеме, без пояснений.",
                },
            ]
    raise LLMError(
        f"Модель {MAX_ATTEMPTS} раза вернула некорректный ответ ({last_problem}). "
        "Нажмите «Повторить анализ»."
    )


def _chat(messages: list[dict[str, str]]) -> str:
    """One request to Ollama. Returns the raw text of the model answer."""
    try:
        response = requests.post(
            f"{settings.OLLAMA_URL}/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "format": Evaluation.model_json_schema(),
                "options": {"temperature": 0.2, "num_ctx": 8192},
            },
            timeout=settings.OLLAMA_TIMEOUT,
        )
    except requests.ConnectionError as exc:
        raise LLMError("LLM недоступна: сервис Ollama не запущен.") from exc
    except requests.Timeout as exc:
        raise LLMError(f"Модель не ответила за {settings.OLLAMA_TIMEOUT} с.") from exc

    if response.status_code == 404:
        raise LLMError(
            f"Модель {settings.OLLAMA_MODEL} ещё скачивается. Подождите пару минут и повторите."
        )
    if not response.ok:
        raise LLMError(f"Ollama вернула ошибку {response.status_code}.")
    return response.json()["message"]["content"]
