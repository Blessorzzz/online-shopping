from django.urls import path
from . import views
from .views import toggle_product_status, vendor_order_detail

urlpatterns = [
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('add_product/', views.add_product, name='add_product'),
    path('products/edit/<uuid:product_id>/', views.edit_product, name='edit_product'),
    path('products/toggle/<uuid:product_id>/', toggle_product_status, name='toggle_product_status'),
    path('vendor_orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/order_detail/<int:order_id>/', vendor_order_detail, name='vendor_order_detail'),
    path('vendor/product/<uuid:product_id>/', views.vendor_product_detail, name='vendor_product_detail'),
    path('vendor_login/', views.vendor_login, name='vendor_login'),
    path('product/photo/<int:photo_id>/delete/', views.delete_product_photo, name='delete_product_photo'),  # New path for deleting product photos
    path('vendor/product/review/<int:review_id>/respond/', views.vendor_respond_review, name='vendor_respond_review'),
]