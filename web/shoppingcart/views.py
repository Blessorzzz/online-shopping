# shoppingcart/views.py

from django.shortcuts import render
from ecommerce.models import Product
from .models import ShoppingCart, CartItem
from django.contrib.auth.decorators import login_required

@login_required
def view_cart(request):
    cart = ShoppingCart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.subtotal for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    cart, created = ShoppingCart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('cart')
