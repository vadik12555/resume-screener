"""Every HR user must see only their own vacancies and candidates."""

from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from candidates.models import Candidate


def vacancy_urls(v):
    return [
        reverse("vacancy_detail", args=[v.pk]),
        reverse("vacancy_edit", args=[v.pk]),
        reverse("candidates_table", args=[v.pk]),
        reverse("candidates_progress", args=[v.pk]),
        reverse("candidates_export", args=[v.pk]),
    ]


def test_anonymous_is_redirected_to_login(client, vacancy, candidate):
    for url in [reverse("dashboard"), *vacancy_urls(vacancy), reverse("candidate_detail", args=[candidate.pk])]:
        response = client.get(url)
        assert response.status_code == 302 and "/accounts/login/" in response.url, url


def test_stranger_gets_404_on_foreign_vacancy(client, stranger, vacancy):
    client.force_login(stranger)
    for url in vacancy_urls(vacancy):
        assert client.get(url).status_code == 404, url
    assert client.post(reverse("vacancy_delete", args=[vacancy.pk])).status_code == 404


def test_stranger_cannot_touch_foreign_candidate(client, stranger, candidate):
    client.force_login(stranger)
    assert client.get(reverse("candidate_detail", args=[candidate.pk])).status_code == 404
    response = client.post(reverse("candidate_decision", args=[candidate.pk]), {"decision": "rejected"})
    assert response.status_code == 404
    candidate.refresh_from_db()
    assert candidate.decision == Candidate.Decision.NEW


def test_stranger_cannot_upload_to_foreign_vacancy(client, stranger, vacancy):
    client.force_login(stranger)
    f = SimpleUploadedFile("cv.pdf", b"%PDF-1.4")
    assert client.post(reverse("candidates_upload", args=[vacancy.pk]), {"files": [f]}).status_code == 404
    assert vacancy.candidates.count() == 0


def test_dashboard_lists_only_own_vacancies(client, stranger, vacancy):
    client.force_login(stranger)
    assert vacancy.title not in client.get(reverse("dashboard")).content.decode()


def test_owner_sees_everything(client, owner, vacancy, candidate):
    client.force_login(owner)
    for url in vacancy_urls(vacancy):
        assert client.get(url).status_code == 200, url
    assert client.get(reverse("candidate_detail", args=[candidate.pk])).status_code == 200


def test_owner_can_change_decision(client, owner, candidate):
    client.force_login(owner)
    client.post(reverse("candidate_decision", args=[candidate.pk]), {"decision": "invited"})
    candidate.refresh_from_db()
    assert candidate.decision == Candidate.Decision.INVITED


@pytest.mark.django_db(transaction=True)
def test_upload_rejects_unsupported_files(client, owner, vacancy):
    client.force_login(owner)
    files = [SimpleUploadedFile("photo.jpg", b"jpg")]
    with patch("candidates.views.process_candidate.delay") as delay:
        client.post(reverse("candidates_upload", args=[vacancy.pk]), {"files": files})
    c = vacancy.candidates.get()
    assert c.processing == Candidate.Processing.ERROR
    delay.assert_not_called()


def test_export_returns_xlsx(client, owner, vacancy, candidate):
    client.force_login(owner)
    response = client.get(reverse("candidates_export", args=[vacancy.pk]))
    assert response["Content-Type"].startswith("application/vnd.openxmlformats")
    assert response.content[:2] == b"PK"  # xlsx is a zip archive
