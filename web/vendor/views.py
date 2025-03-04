from django import forms
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from shoppingcart.models import Order, OrderItem
from ecommerce.models import Product, ProductPhoto, ProductPhoto
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
    ProductPhotoFormSet = inlineformset_factory(
        Product, ProductPhoto, 
        fields=('photo',), 
        extra=3,
        can_delete=True,
        widgets={'photo': forms.FileInput(attrs={'accept': 'image/*'}) } # 添加文件类型限制
    )
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()

            # 实例化表单集时传入 product 实例
            formset = ProductPhotoFormSet(request.POST, request.FILES, instance=product)
            if formset.is_valid():
                # 保存图片表单集
                for photo_form in formset:
                    if photo_form.cleaned_data.get('photo'):
                        photo = photo_form.save(commit=False)
                        photo.product = product
                        photo.save()
                
                # 处理标记删除的图片
                for obj in formset.deleted_forms:  # 修改为 deleted_forms
                    if obj.instance.pk:
                        obj.instance.delete()
                        
                return redirect('vendor_dashboard')
    else:
        form = ProductForm()
        formset = ProductPhotoFormSet()
    return render(request, 'vendor/add_product.html', {
        'form': form,
        'formset': formset
    })

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    ProductPhotoFormSet = inlineformset_factory(
        Product, ProductPhoto, 
        fields=('photo',), 
        extra=3,
        can_delete=True,
        validate_min=False,
        widgets={'photo': forms.FileInput(attrs={'accept': 'image/*'})}
    )

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductPhotoFormSet(request.POST, request.FILES, instance=product)
        
        if form.is_valid() and formset.is_valid():
            # 保存主产品
            product = form.save()
            
            # 处理图片表单集
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.photo and not instance.pk:  # 新增且无文件则跳过
                continue
            if not instance.pk:
                instance.product = product
            instance.save()
            
            # 显式删除标记删除的实例
            for deleted_form in formset.deleted_objects:
                deleted_form.delete()
            
            messages.success(request, "产品更新成功！")
            return redirect('vendor_dashboard')
        else:
            # 调试输出错误信息
            print("表单错误:", form.errors)
            print("表单集错误:", formset.errors)
            messages.error(request, "请检查表单中的错误。")
    else:
        form = ProductForm(instance=product)
        formset = ProductPhotoFormSet(instance=product)

    return render(request, 'vendor/edit_product.html', {
        'form': form,
        'formset': formset,
        'product': product
    })
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
                'shipped': ['cancelled', 'hold'],
                'cancelled': [],
                'hold': ['shipped', 'cancelled']
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
                'refunded': 'refund_date'
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
        'refunded': order.refund_date
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