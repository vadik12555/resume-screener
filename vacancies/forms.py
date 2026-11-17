from django import forms

from core.forms import StyledFormMixin

from .models import Vacancy


class VacancyForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ["title", "description", "must_have", "nice_to_have"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Например, Python-разработчик (Middle)"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Задачи, команда, продукт…"}
            ),
            "must_have": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Python 3\nDjango\nPostgreSQL"}
            ),
            "nice_to_have": forms.Textarea(attrs={"rows": 5, "placeholder": "Docker\nCelery"}),
        }
