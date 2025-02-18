# shoppingcart/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('view_cart/', views.view_cart, name='view_cart'),  # 查看购物车
    path('add_to_cart/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),  # 添加商品到购物车
    path('update_cart/<int:cart_item_id>/', views.update_cart, name='update_cart'),  # 更新购物车商品数量
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),  # 删除购物车商品
    path('cart/', views.view_cart, name='shopping_cart'),
    path('checkout/', views.checkout, name='checkout'),  # 结算 URL
    path('orders/', views.order_list, name='order_list'),  # 订单列表
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]