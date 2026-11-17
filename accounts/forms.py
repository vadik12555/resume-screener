from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from core.forms import StyledFormMixin


class LoginForm(StyledFormMixin, AuthenticationForm):
    pass


class SignUpForm(StyledFormMixin, UserCreationForm):
    pass
