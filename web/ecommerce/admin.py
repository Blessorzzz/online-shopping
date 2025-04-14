from django.contrib import admin
from .models import Product, ProductPhoto, ProductVideo
from shoppingcart.models import Order, OrderItem  # Import Order and OrderItem models

class ProductPhotoInline(admin.TabularInline):
    model = ProductPhoto
    extra = 3  # 显示3个空表单项
    max_num = 10
    # 明确指定外键字段（重要！）
    fk_name = 'product'  # 新增此行

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductPhotoInline]
    list_display = (
        'product_name',
        'product_type',
        'price',
        'vendor'
        )  # 显示产品名称、类型、价格和供应商
    list_filter = ('product_type', 'vendor')  # 添加过滤器
    search_fields = ('product_name', 'vendor__username')  # 添加搜索字段
    readonly_fields = (
        'get_mhi_score',
        'get_acr_score',
        'get_vhd_score',
        'get_ics_score',
        'safety_score',
    )
    exclude = ('sharpness_category_score',)

    def get_mhi_score(self, obj):
        return obj.get_mhi_score()
    get_mhi_score.short_description = "MHI Score"

    def get_acr_score(self, obj):
        return obj.get_acr_score()
    get_acr_score.short_description = "ACR Score"

    def get_vhd_score(self, obj):
        return obj.get_vhd_score()
    get_vhd_score.short_description = "VHD Score"

    def get_ics_score(self, obj):
        return obj.get_ics_score()
    get_ics_score.short_description = "ICS Score"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # 不显示额外的空表单项

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('po_number', 'customer', 'total_amount', 'status', 'purchase_date')  # 显示订单号、客户、总金额、状态和购买日期
    list_filter = ('status', 'purchase_date')  # 添加过滤器
    search_fields = ('po_number', 'customer__username')  # 添加搜索字段

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            product_type = obj.items.first().product.product_type if obj.items.exists() else 'tangible'
            if product_type == 'tangible':
                form.base_fields['status'].choices = Order.STATUS_CHOICES_TANGIBLE
            else:
                form.base_fields['status'].choices = Order.STATUS_CHOICES_VIRTUAL
        return form

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductPhoto)
admin.site.register(ProductVideo)
admin.site.register(Order, OrderAdmin)  # Register Order model with custom admin
admin.site.register(OrderItem)  # Register OrderItem model
