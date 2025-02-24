from django.urls import path
from . import views
from .views import edit_product, toggle_product_status, order_detail

urlpatterns = [
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('add_product/', views.add_product, name='add_product'),
    path('products/edit/<uuid:product_id>/', views.edit_product, name='edit_product'),
    path('products/toggle/<uuid:product_id>/', toggle_product_status, name='toggle_product_status'),
    path('vendor_orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/order_detail/<int:order_id>/', order_detail, name='order_detail'),
    path('vendor/product/<uuid:product_id>/', views.vendor_product_detail, name='vendor_product_detail'),
]