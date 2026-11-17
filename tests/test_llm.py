import json
from unittest.mock import patch

import pytest

from candidates.models import Candidate
from candidates.services.llm import (
    InvalidResponse,
    LLMError,
    evaluate_resume,
    parse_evaluation,
)
from candidates.tasks import process_candidate

VALID = {
    "name": "Иван Иванов",
    "score": 81,
    "summary": "Подходит.",
    "strengths": ["Django"],
    "gaps": [],
    "questions": ["В1?", "В2?", "В3?"],
}


def as_json(**overrides) -> str:
    return json.dumps({**VALID, **overrides}, ensure_ascii=False)


# --- parse_evaluation -------------------------------------------------------

def test_valid_response_is_parsed():
    ev = parse_evaluation(as_json())
    assert ev.name == "Иван Иванов" and ev.score == 81 and len(ev.questions) == 3
    assert ev.age is None and ev.skills == []  # profile fields are optional


def test_profile_fields_are_parsed_and_validated():
    ev = parse_evaluation(as_json(age=35, position="Backend-разработчик", experience_years=8, skills=["Python"]))
    assert ev.age == 35 and ev.skills == ["Python"]
    with pytest.raises(InvalidResponse):
        parse_evaluation(as_json(age=300))


def test_age_and_experience_labels():
    from candidates.models import years
    assert [years(n) for n in (1, 3, 11, 21, 35)] == ["1 год", "3 года", "11 лет", "21 год", "35 лет"]


@pytest.mark.parametrize(
    "raw",
    [
        "это не json",
        as_json(score=150),             # out of range
        as_json(score=-1),
        as_json(questions=["один?"]),   # must be exactly 3
        json.dumps({"name": "Без оценки"}),
    ],
)
def test_invalid_responses_are_rejected(raw):
    with pytest.raises(InvalidResponse):
        parse_evaluation(raw)


# --- evaluate_resume: retry logic -------------------------------------------

def test_retries_once_after_invalid_json(vacancy):
    with patch("candidates.services.llm._chat", side_effect=["oops", as_json()]) as chat:
        ev = evaluate_resume(vacancy, "резюме")
    assert ev.score == 81
    assert chat.call_count == 2
    # the second request tells the model what was wrong
    second_messages = chat.call_args_list[1].args[0]
    assert "некорректен" in second_messages[-1]["content"]


def test_raises_clear_error_after_two_invalid_answers(vacancy):
    with patch("candidates.services.llm._chat", side_effect=["oops", "still oops"]):
        with pytest.raises(LLMError, match="некорректный ответ"):
            evaluate_resume(vacancy, "резюме")


def test_prompt_contains_requirements(vacancy):
    with patch("candidates.services.llm._chat", return_value=as_json()) as chat:
        evaluate_resume(vacancy, "Текст резюме")
    user_prompt = chat.call_args.args[0][1]["content"]
    assert "- Django" in user_prompt and "- Docker" in user_prompt and "Текст резюме" in user_prompt


# --- background task --------------------------------------------------------

@pytest.mark.django_db
def test_task_saves_evaluation(vacancy):
    c = Candidate.objects.create(vacancy=vacancy, resume_text="резюме")
    with patch("candidates.services.llm._chat", return_value=as_json()):
        process_candidate(c.pk)
    c.refresh_from_db()
    assert c.processing == Candidate.Processing.DONE
    assert c.score == 81 and c.name == "Иван Иванов"


@pytest.mark.django_db
def test_task_marks_error_when_llm_unavailable(vacancy):
    c = Candidate.objects.create(vacancy=vacancy, resume_text="резюме")
    with patch("candidates.tasks.evaluate_resume", side_effect=LLMError("LLM недоступна")):
        process_candidate(c.pk)
    c.refresh_from_db()
    assert c.processing == Candidate.Processing.ERROR
    assert c.error == "LLM недоступна"
