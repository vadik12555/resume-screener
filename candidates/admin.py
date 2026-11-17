from django.contrib import admin

from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("display_name", "vacancy", "score", "processing", "decision")
    list_filter = ("processing", "decision")
