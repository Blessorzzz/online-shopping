from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Product, ProductPhoto, ProductVideo

class ProductPhotoInline(admin.TabularInline):
    model = ProductPhoto
    extra = 3  # 显示3个空表单项
    max_num = 10
    # 明确指定外键字段（重要！）
    fk_name = 'product'  # 新增此行

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductPhotoInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductPhoto)
