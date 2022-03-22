from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import SynrateUser


class UserForm(UserCreationForm):
    first_name = forms.CharField(max_length=300, required=False, help_text="Необязательное поле")
    last_name = forms.CharField(max_length=300, required=False, help_text="Необязательное поле")

    class Meta:
        model = SynrateUser
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        user.first_name = first_name
        user.last_name = last_name
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LogInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
