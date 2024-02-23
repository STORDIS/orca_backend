from django.contrib.auth.models import User
from django import forms

# Create your models here.


class CreateUserForm(forms.ModelForm):
    """
    Form model to create user.
    """

    username = forms.CharField(max_length=60, required=True)
    email = forms.CharField(max_length=120, required=True)
    first_name = forms.CharField(max_length=60, required=True)
    last_name = forms.CharField(max_length=60, required=True)
    password = forms.CharField(max_length=120, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "last_name", "first_name", "password"]
