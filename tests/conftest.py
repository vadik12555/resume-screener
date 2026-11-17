from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from candidates.models import Candidate
from vacancies.models import Vacancy


@pytest.fixture(autouse=True)
def no_real_ollama():
    """Header status check must never hit a real Ollama in tests."""
    with patch("core.context_processors._check", return_value="ready"):
        yield


@pytest.fixture
def owner(db):
    return get_user_model().objects.create_user("owner", password="pass12345")


@pytest.fixture
def stranger(db):
    return get_user_model().objects.create_user("stranger", password="pass12345")


@pytest.fixture
def vacancy(owner):
    return Vacancy.objects.create(
        owner=owner, title="Python-разработчик", must_have="Python\nDjango", nice_to_have="Docker"
    )


@pytest.fixture
def candidate(vacancy):
    return Candidate.objects.create(
        vacancy=vacancy,
        resume_text="Иван Иванов, Python-разработчик, 3 года Django и PostgreSQL.",
        name="Иван Иванов",
        score=80,
        processing=Candidate.Processing.DONE,
    )
