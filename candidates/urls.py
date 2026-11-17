from django.urls import path

from . import views

urlpatterns = [
    path("candidates/", views.all_candidates, name="candidates_all"),
    path("vacancies/<int:pk>/upload/", views.upload, name="candidates_upload"),
    path("vacancies/<int:pk>/candidates/", views.candidates_table, name="candidates_table"),
    path("vacancies/<int:pk>/progress/", views.progress, name="candidates_progress"),
    path("vacancies/<int:pk>/export/", views.export, name="candidates_export"),
    path("candidates/<int:pk>/", views.detail, name="candidate_detail"),
    path("candidates/<int:pk>/decision/", views.set_decision, name="candidate_decision"),
    path("candidates/<int:pk>/notes/", views.save_notes, name="candidate_notes"),
    path("candidates/<int:pk>/retry/", views.retry, name="candidate_retry"),
    path("candidates/<int:pk>/delete/", views.delete, name="candidate_delete"),
]
