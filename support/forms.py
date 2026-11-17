from django import forms

from core.forms import StyledFormMixin

from .models import Ticket


class TicketForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["category", "subject", "message"]
        widgets = {
            "subject": forms.TextInput(attrs={"placeholder": "Например, не загружается PDF"}),
            "message": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Опишите, что произошло и что вы ожидали увидеть"}
            ),
        }
