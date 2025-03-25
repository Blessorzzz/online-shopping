from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from ecommerce.models import Product
from shoppingcart.models import Order
from .forms import ReviewForm
import uuid

@login_required
def add_review(request, order_id, product_id):
    # Get the order and product
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    product = get_object_or_404(order.items.all(), product__product_id=product_id).product

    if not order.can_be_reviewed():
        messages.error(request, "You can only review completed, refunded, or delivered orders.")
        return redirect("order_detail", order_id=order_id)

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.order = order
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect("order_detail", order_id=order_id)
    else:
        form = ReviewForm()

    return render(request, "review/add_review.html", {"form": form, "product": product, "order": order})

@login_required
def my_reviews(request):
    # Fetch all reviews for the logged-in user
    reviews = Review.objects.filter(user=request.user).select_related("order", "product").order_by("-created_at")
    
    # Group reviews by order and product
    orders_with_reviews = {}
    
    for review in reviews:
        # Check if the order already exists in the dictionary
        if review.order.id not in orders_with_reviews:
            orders_with_reviews[review.order.id] = {
                "order": review.order,
                "products": review.order.products,  # No .all() here since products is already a list
                "reviews": []  # Initialize an empty list to store reviews for this order
            }
        
        # Append the review to the 'reviews' list for the specific order
        orders_with_reviews[review.order.id]["reviews"].append({
            "product": review.product,
            "review": review,
        })
    
    return render(request, "review/my_reviews.html", {"orders_with_reviews": orders_with_reviews})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully!")
            return redirect("order_detail", order_id=review.order.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, "review/edit_review.html", {"form": form, "product": review.product, "order": review.order})