from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm


class UserAdminCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=200)

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name']


class PasswordAdminResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=200)

    class Meta:
        model = get_user_model()
        fields = ['email']

