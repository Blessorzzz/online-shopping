from django.db import transaction, IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from ecommerce.models import Product
from .models import ShoppingCart, Order, OrderItem
from django.contrib import messages
from user.models import UserProfile
from django.utils.timezone import now
from review.models import Review
import logging

logger = logging.getLogger(__name__)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    cart_item, created = ShoppingCart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, "Item has been added to cart.")
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = ShoppingCart.objects.filter(user=request.user)
    total_amount = 0

    for item in cart_items:
        item.total_price = item.product.price * item.quantity
        total_amount += item.total_price

    return render(request, 'view_cart.html', {'cart_items': cart_items, 'total_amount': total_amount})

@login_required
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(ShoppingCart, id=cart_item_id, user=request.user)
    
    quantity = int(request.POST.get('quantity', cart_item.quantity))

    action = request.POST.get('action')
    if action == 'decrease' and quantity > 1:
        quantity -= 1
    elif action == 'increase':
        quantity += 1

    cart_item.quantity = quantity
    cart_item.save()
    
    return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(ShoppingCart, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item has been removed from cart.")
    return redirect('view_cart')

@login_required
def checkout(request):
    logger.info("✅ Checkout view triggered!")
    print("✅ Checkout view triggered!")

    cart_items = ShoppingCart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your shopping cart is empty.")
        logger.warning("❌ Checkout failed: Cart is empty.")
        return redirect('view_cart')

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if not user_profile.address:
        messages.error(request, "Please enter a valid shipping address in 'My Profile'.")
        logger.warning("❌ Checkout failed: Missing shipping address.")
        return redirect('view_cart')

    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    try:
        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user,
                total_amount=total_amount,
                shipping_address=user_profile.address,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

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
    orders = Order.objects.filter(customer=request.user)

    if status_filter:
        orders = Order.objects.filter(status=status_filter, customer=request.user).order_by('-purchase_date')
    else:
        orders = Order.objects.filter(customer=request.user).order_by('-purchase_date')
    return render(request, 'order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Generate status timeline data
    status_date_map = {
        'pending': order.pending_date,
        'shipped': order.shipment_date,
        'cancelled': order.cancel_date,
        'hold': order.hold_date,
        'ticket-issued': order.ticket_issue_date,
        'complete': order.complete_date,
        'refunded': order.refund_date,
        'delivered': order.delivered_date,
    }

    sorted_status_dates = sorted(
        [(status, date) for status, date in status_date_map.items() if date],
        key=lambda x: x[1]
    )

    # Fetch reviews for the current order and user
    reviews = Review.objects.filter(user=request.user, order=order)
    product_reviews = {str(review.product.product_id): review for review in reviews}  # Ensure keys are strings


    return render(request, 'order_detail.html', {
        'order': order,
        'sorted_status_dates': sorted_status_dates,
        'product_reviews': product_reviews,  # Pass reviews to the template
    })

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
