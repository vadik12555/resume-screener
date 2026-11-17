from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "category", "status", "created_at")
    list_filter = ("status", "category")
    readonly_fields = ("user", "category", "subject", "message", "created_at")
    fields = ("user", "category", "subject", "message", "created_at", "answer", "status")

    def save_model(self, request, obj, form, change):
        # Writing an answer marks the ticket as answered automatically.
        if obj.answer and obj.status == Ticket.Status.OPEN:
            obj.status = Ticket.Status.ANSWERED
        super().save_model(request, obj, form, change)
