from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from shoppingcart.models import Order, OrderItem
from ecommerce.models import Product, ProductPhoto
from .forms import ProductForm
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.utils.timezone import now

def vendor_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if hasattr(user, 'vendor'):
                auth_login(request, user)
                return redirect('vendor_dashboard')
            else:
                messages.error(request, "You are not a vendor.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/vendor_login.html', {'form': form})

# vendor search function
@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'vendor'):
        return render(request, 'vendor/not_a_vendor.html')
    
    vendor = request.user.vendor
    query = request.GET.get('q', '').strip()  # Get search query from URL
    products = Product.objects.filter(vendor=vendor)  # Get all products for this vendor

    if query:
        products = products.filter(
            Q(product_name__icontains=query) |  # Search by product name (case-insensitive)
            Q(product_id__icontains=query)  # Search by product ID (case-insensitive)
        )

    return render(request, 'vendor/dashboard.html', {'vendor': vendor, 'products': products, 'query': query})

@login_required
def vendor_orders(request):
    if not hasattr(request.user, 'vendor'):
        return HttpResponseForbidden("You are not a vendor.")
    
    vendor = request.user.vendor
    # Query all orders that include products from the vendor
    orders = Order.objects.filter(items__product__vendor=vendor).distinct().order_by('-purchase_date')
    
    return render(request, 'vendor/vendor_orders.html', {'orders': orders})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            
            # Handle additional images
            for file in request.FILES.getlist('additional_images'):
                ProductPhoto.objects.create(product=product, photo=file)
            
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
    return render(request, 'vendor/add_product.html', {'form': form})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        # Debugging: Check if stock_quantity is being received in POST data
        print("Stock Quantity in POST data:", request.POST.get("stock_quantity"))

        if form.is_valid():
            product = form.save()

            # Debugging: Check if stock_quantity is saved correctly
            print("Saved product stock_quantity:", product.stock_quantity)

            for file in request.FILES.getlist('additional_images'):
                ProductPhoto.objects.create(product=product, photo=file)

            return redirect('vendor_dashboard')
        else:
            # Debugging: Print form errors if the form is not valid
            print("Form errors:", form.errors)
            print("Form cleaned data:", form.cleaned_data)  # Check what data is being processed

    else:
        form = ProductForm(instance=product)

    return render(request, 'vendor/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product_photo(request, photo_id):
    if request.method == 'POST':
        photo = get_object_or_404(ProductPhoto, pk=photo_id)
        photo.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

# Toggle the status of a product between active and inactive
@login_required
def toggle_product_status(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    product.is_active = not product.is_active
    product.save()
    return redirect('vendor_dashboard')

# Display the details of an order
@login_required
def vendor_order_detail(request, order_id):
    if not hasattr(request.user, 'vendor'):
        return HttpResponseForbidden("You are not a vendor.")

    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()

    if request.method == 'POST':
        new_status = request.POST.get('status')
        product_type = order.items.first().product.product_type if order.items.exists() else 'tangible'

        # Define allowed status transitions
        allowed_transitions = {
            'tangible': {
                'pending': ['shipped', 'cancelled', 'hold'],
                'shipped': ['cancelled', 'hold', 'delivered'],
                'cancelled': [],
                'hold': ['shipped', 'cancelled'],
                'delivered': []
            },
            'virtual': {
                'pending': ['ticket-issued', 'complete', 'refunded'],
                'ticket-issued': ['complete', 'refunded'],
                'complete': [],
                'refunded': []
            }
        }

        current_status = order.status
        if new_status in allowed_transitions[product_type].get(current_status, []):
            order.status = new_status
            # Update the timestamp for the corresponding status
            status_date_map = {
                'pending': 'pending_date',
                'shipped': 'shipment_date',
                'cancelled': 'cancel_date',
                'hold': 'hold_date',
                'ticket-issued': 'ticket_issue_date',
                'complete': 'complete_date',
                'refunded': 'refund_date',
                'delivered': 'delivered_date',
            }
            
            if new_status in status_date_map:
                setattr(order, status_date_map[new_status], now())
                print(f"Updated {status_date_map[new_status]} timestamp for status: {new_status}")

            order.save()
            messages.success(request, "Order status updated successfully.")
        else:
            messages.error(request, "Invalid status change.")
        return redirect('vendor_order_detail', order_id=order.id)

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

    print("Sorted status dates:", sorted_status_dates)  # Debugging output

    return render(request, 'vendor/vendor_order_detail.html', {
        'order': order,
        'order_items': order_items,
        'sorted_status_dates': sorted_status_dates
    })

@login_required
def vendor_product_detail(request, product_id):
    if not hasattr(request.user, 'vendor'):
        return HttpResponseForbidden("You are not a vendor.")
    
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'vendor/vendor_product_detail.html', {'product': product})