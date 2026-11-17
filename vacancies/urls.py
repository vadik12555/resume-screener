from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("new/", views.create, name="vacancy_create"),
    path("<int:pk>/", views.detail, name="vacancy_detail"),
    path("<int:pk>/edit/", views.edit, name="vacancy_edit"),
    path("<int:pk>/delete/", views.delete, name="vacancy_delete"),
]
