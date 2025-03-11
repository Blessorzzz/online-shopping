from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from ecommerce.models import Product
from shoppingcart.models import Order
from .forms import ReviewForm
import uuid

@login_required
def add_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if not order.can_be_reviewed():
        messages.error(request, "You can only review completed, refunded, or delivered orders.")
        return redirect("order_list")

    products = order.items.all()

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            product_id = request.POST.get("product")
            try:
                product_uuid = uuid.UUID(product_id)
            except ValueError:
                messages.error(request, "Invalid product selection.")
                return redirect("add_review", order_id=order.id)

            product = get_object_or_404(Product, product_id=product_uuid)
            if product not in [item.product for item in products]:
                messages.error(request, "Invalid product selection.")
                return redirect("add_review", order_id=order.id)

            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.order = order  # Set the order field
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect("my_reviews")
    else:
        form = ReviewForm()

    return render(request, "review/add_review.html", {"form": form, "products": products})

@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "review/my_reviews.html", {"reviews": reviews})
