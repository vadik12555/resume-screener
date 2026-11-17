from django.urls import reverse

from support.models import Ticket


def test_user_creates_ticket_and_sees_only_own(client, owner, stranger):
    Ticket.objects.create(user=stranger, subject="Чужое обращение", message="...")
    client.force_login(owner)
    response = client.post(
        reverse("support"), {"category": "bug", "subject": "Не грузится PDF", "message": "Ошибка"}
    )
    assert response.status_code == 302
    page = client.get(reverse("support")).content.decode()
    assert "Не грузится PDF" in page
    assert "Чужое обращение" not in page


def test_all_candidates_shows_only_own_and_searches(client, owner, stranger, candidate):
    client.force_login(stranger)
    assert candidate.name not in client.get(reverse("candidates_all")).content.decode()
    client.force_login(owner)
    assert candidate.name in client.get(reverse("candidates_all"), {"q": "иван"}).content.decode()
    assert candidate.name not in client.get(reverse("candidates_all"), {"q": "нет такого"}).content.decode()


def test_support_requires_login(client, db):
    assert client.get(reverse("support")).status_code == 302


def test_owner_saves_notes(client, owner, candidate):
    client.force_login(owner)
    client.post(reverse("candidate_notes", args=[candidate.pk]), {"notes": "Ждёт 250к"})
    candidate.refresh_from_db()
    assert candidate.notes == "Ждёт 250к"


def test_stranger_cannot_save_notes(client, stranger, candidate):
    client.force_login(stranger)
    assert client.post(reverse("candidate_notes", args=[candidate.pk]), {"notes": "x"}).status_code == 404
