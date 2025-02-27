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
    list_display = ('product_name', 'product_type', 'price', 'vendor')  # 显示产品名称、类型、价格和供应商
    list_filter = ('product_type', 'vendor')  # 添加过滤器
    search_fields = ('product_name', 'vendor__username')  # 添加搜索字段

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductPhoto)
admin.site.register(ProductVideo)