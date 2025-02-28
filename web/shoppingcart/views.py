from django.db import transaction, IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from ecommerce.models import Product  # 引用 Product 模型
from .models import ShoppingCart, Order, OrderItem
from django.contrib import messages
from user.models import UserProfile

import logging

logger = logging.getLogger(__name__)

@login_required  # 确保用户已经登录才能添加商品到购物车
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)  # 根据商品 ID 获取商品
    cart_item, created = ShoppingCart.objects.get_or_create(user=request.user, product=product)  # 如果购物车已有该商品，获取它，否则创建新的购物车项
    if not created:  # 如果商品已存在购物车，增加数量
        cart_item.quantity += 1
    cart_item.save()  # 保存购物车项
    messages.success(request, "Item has been added to cart.")
    return redirect('view_cart')  # 添加后重定向到购物车页面

@login_required  # 确保用户已经登录
def view_cart(request):
    cart_items = ShoppingCart.objects.filter(user=request.user)  # 获取当前用户的购物车项
    total_amount = 0  # 初始化总金额

    # 计算每个商品的总金额并将其加入总金额
    for item in cart_items:
        item.total_price = item.product.price * item.quantity  # 计算每个商品的总金额
        total_amount += item.total_price  # 将该商品的总金额加入总金额

    # 将购物车项和总金额传递到模板
    return render(request, 'view_cart.html', {'cart_items': cart_items, 'total_amount': total_amount})

@login_required  # 确保用户已登录
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(ShoppingCart, id=cart_item_id, user=request.user)
    
    # 获取提交的数量
    quantity = int(request.POST.get('quantity', cart_item.quantity))

    # 判断是否是增加或减少操作
    action = request.POST.get('action')
    if action == 'decrease' and quantity > 1:
        quantity -= 1  # 减少数量
    elif action == 'increase':
        quantity += 1  # 增加数量

    # 更新购物车项
    cart_item.quantity = quantity
    cart_item.save()
    
    return redirect('view_cart')  # 更新后重定向回购物车页面

@login_required  # 确保用户已登录
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(ShoppingCart, id=cart_item_id, user=request.user)
    cart_item.delete()  # 从购物车中删除该商品
    messages.success(request, "Item has been removed from cart.")
    return redirect('view_cart')

@login_required
def checkout(request):
    logger.info("✅ Checkout view triggered!")
    print("✅ Checkout view triggered!")  # 终端调试

    cart_items = ShoppingCart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your shopping cart is empty.")
        logger.warning("❌ Checkout failed: Cart is empty.")
        return redirect('view_cart')

    # **确保 UserProfile 存在**
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # **检查收货地址**
    if not user_profile.address:
        messages.error(request, "Please enter a valid shipping address in 'My Profile'.")
        logger.warning("❌ Checkout failed: Missing shipping address.")
        return redirect('view_cart')

    # **计算订单总金额**
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    try:
        with transaction.atomic():
            # 创建订单（自动生成 id）
            order = Order.objects.create(
                customer=request.user,
                total_amount=total_amount,
                shipping_address=user_profile.address,
            )

            # 创建订单项
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # 清空购物车
            cart_items.delete()
            messages.success(request, "Order placed successfully!")

    except IntegrityError as e:
        logger.error(f"IntegrityError: {str(e)}")
        messages.error(request, "Failed to create order. Please try again.")
        return redirect('view_cart')

    return redirect('order_list')

@login_required
def order_list(request):
    status_filter = request.GET.get('status')
    if status_filter:
        orders = Order.objects.filter(status=status_filter, customer=request.user).order_by('-purchase_date')
    else:
        orders = Order.objects.filter(customer=request.user).order_by('-purchase_date')
    return render(request, 'order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if order.status in ['pending', 'hold']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, "Your order has been cancelled.")
    else:
        messages.error(request, "You can only cancel pending or on hold orders.")
    return redirect('order_list')
