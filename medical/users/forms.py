from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from users.models import PatientProfile
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_('Пароль'),
        widget=(forms.PasswordInput(attrs={'class': 'form-control'})),
        help_text=_(
            '- Ваш пароль не должен быть слишком похож на другую вашу'
            ' личную информацию.<br>'
            '- Ваш пароль должен содержать не менее 8 символов.<br>'
            '- Ваш пароль не может быть часто используемым паролем.<br>'
            '- Ваш пароль не может быть полностью цифровым.<br>'
        ),
    )
    password2 = forms.CharField(
        label=_('Подтверждение пароля'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_('Просто введите тот же пароль для подтверждения'),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def save(self):
        user = super().save()
        PatientProfile.objects.create(user=user)
        return user
