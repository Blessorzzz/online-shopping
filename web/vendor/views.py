from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vendor
from shoppingcart.models import Order
from ecommerce.models import Product
from .forms import ProductForm
from django.http import HttpResponseForbidden
from django.shortcuts import HttpResponse

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if hasattr(user, 'vendor'):
                return redirect('vendor_dashboard')
            else:
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'vendor'):
        return render(request, 'vendor/not_a_vendor.html')

    vendor = request.user.vendor
    products = Product.objects.filter(vendor=vendor)
    return render(request, 'vendor/dashboard.html', {'vendor': vendor, 'products': products})

    vendor = request.user.vendor
    query = request.GET.get('q', '').strip()  # Get search query from URL
    products = Product.objects.filter(vendor=vendor)  # Get all products for this vendor

    if query:
        products = products.filter(
            product_name__icontains=query  # Search by product name (case-insensitive)
        ) | products.filter(
            product_id__icontains=query  # Search by product ID (case-insensitive)
        )

    return render(request, 'vendor/dashboard.html', {'vendor': vendor, 'products': products, 'query': query})

@login_required
def vendor_orders(request):
    if not hasattr(request.user, 'vendor'):
        return HttpResponseForbidden("You are not a vendor.")
    vendor = request.user.vendor
    orders = Order.objects.filter(user=request.user)
    return render(request, 'vendor/vendor_orders.html', {'orders': orders})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
    return render(request, 'vendor/add_product.html', {'form': form})

def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'vendor/edit_product.html', {'form': form, 'product': product})

# Toggle the status of a product between active and inactive
def toggle_product_status(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    product.is_active = not product.is_active
    product.save()
    return redirect('vendor_dashboard')

# Display the details of an order
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()  # Assuming 'items' is a related field in Order

    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items})
