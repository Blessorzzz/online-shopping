from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _  # ✅ 添加国际化支持

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        label=_("Email"),  # ✅ 让 Email 支持翻译
        help_text=_("Please enter a valid email address.")  # ✅ 让帮助文本支持翻译
    )
    full_name = forms.CharField(
        max_length=100,
        label=_("Full name"),  # ✅ 让 Full name 支持翻译
        help_text=_("Please enter your full name.")  # ✅ 让帮助文本支持翻译
    )
    shipping_address = forms.CharField(
        max_length=255,
        label=_("Shipping address"),  # ✅ 让 Shipping address 支持翻译
        help_text=_("Please enter your shipping address.")  # ✅ 让帮助文本支持翻译
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

