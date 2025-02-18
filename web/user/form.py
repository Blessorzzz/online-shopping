from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from user.models import UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text='Please enter a valid email address.'
    )
    address = forms.CharField(
        max_length=255,
        required=True,
        help_text='Please enter your shipping address.',
        widget=forms.Textarea(attrs={'rows': 2})  # 让地址输入框稍大一点
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
        fields = ('username', 'email', 'password1', 'password2', 'address')  # 添加 address 字段

    def save(self, commit=True):
        user = super().save(commit=False)  # 先不提交到数据库
        if commit:
          user.save()  # 先保存 User
          user.userprofile.address = self.cleaned_data["address"]  # 直接更新地址
          user.userprofile.save()  # 保存更新后的 UserProfile
        return user


