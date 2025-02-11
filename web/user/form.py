# user/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text='please input valid email address'
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
        fields = ('username', 'email', 'password1', 'password2')  # 必填字段
