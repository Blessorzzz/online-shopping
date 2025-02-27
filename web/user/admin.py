from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

# 定义一个内联管理类，用于在 User 管理页面中编辑 UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'

# 自定义 UserAdmin 类，将 UserProfileInline 添加到 User 的管理页面
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

# 取消默认的 User 注册
admin.site.unregister(User)

# 使用自定义的 UserAdmin 重新注册 User
admin.site.register(User, CustomUserAdmin)
