# filepath: /c:/Users/Josh/django_projects/online-shopping-1/web/user/form.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text='Please enter a valid email address.'
    )
    full_name = forms.CharField(
        max_length=100,
        help_text='Please enter your full name.'
    )
    shipping_address = forms.CharField(
        max_length=255,
        help_text='Please enter your shipping address.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'full_name', 'shipping_address')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.userprofile.shipping_address = self.cleaned_data["shipping_address"]
            user.userprofile.save()
        return user