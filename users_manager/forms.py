from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')