from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _  # ✅ 添加国际化支持
import pytz

from user.models import UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, label=_("Email"), help_text=_("Please enter a valid email address."))
    full_name = forms.CharField(max_length=100, label=_("Full name"), help_text=_("Please enter your full name."))
    shipping_address = forms.CharField(max_length=255, label=_("Shipping address"), help_text=_("Please enter your shipping address."))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'full_name', 'shipping_address')

    def save(self, commit=True):
        user = super().save(commit=False)  # 先创建 User 对象但不保存
        user.email = self.cleaned_data['email']
        full_name = self.cleaned_data.get('full_name', '').split()
        user.first_name = full_name[0] if full_name else ''
        user.last_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''
        
        if commit:
            # 先保存 UserProfile，避免信号干扰
            user.save()  # 保存 User，触发信号创建 UserProfile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.address = self.cleaned_data["shipping_address"]
            user_profile.save()
            print(f"Saving address: {self.cleaned_data['shipping_address']}")
        return user
class TimeZoneForm(forms.Form):
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.common_timezones])
