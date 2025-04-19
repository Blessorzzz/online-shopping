from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from .models import Review
from ecommerce.models import Product
from shoppingcart.models import Order
from .forms import ReviewForm
from django.http import JsonResponse
from review.models import Vote
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
            review.save()  # Offensive language will be censored automatically in the save method.
            messages.success(request, "Review submitted successfully!")
            return redirect("my_reviews")
    else:
        form = ReviewForm()

    return render(request, "review/add_review.html", {"form": form, "product": product, "order": order})

@login_required
def my_reviews(request):
    # Get all orders that the user has made
    orders = Order.objects.filter(customer=request.user).prefetch_related("items__product")

    # Dictionaries to store pending and done reviews
    pending_reviews = {}
    done_reviews = {}

    for order in orders:
        order_products = order.items.all()
        
        # Fetch existing reviews for this order
        reviews = Review.objects.filter(user=request.user, order=order).select_related("product")

        # Dictionary to check if a product has been reviewed
        reviewed_products = {review.product.product_id for review in reviews}

        # If order is eligible for review (Completed, Delivered, Refunded)
        if order.status in ['complete', 'delivered', 'refunded']:
            for item in order_products:
                product = item.product

                if product.product_id not in reviewed_products:
                    # Pending Review
                    if order.id not in pending_reviews:
                        pending_reviews[order.id] = {
                            "order": order,
                            "products": [],
                        }
                    pending_reviews[order.id]["products"].append(product)
                else:
                    # Completed Review
                    if order.id not in done_reviews:
                        done_reviews[order.id] = {
                            "order": order,
                            "reviews": [],
                        }
                    done_reviews[order.id]["reviews"].append({
                        "product": product,
                        "review": next(review for review in reviews if review.product == product),
                    })

    return render(request, "review/my_reviews.html", {
        "pending_reviews": pending_reviews,
        "done_reviews": done_reviews,
    })

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            updated_review = form.save(commit=False)
            updated_review.save()  # Offensive language will be censored automatically in the save method.
            messages.success(request, "Review updated successfully!")
            return redirect("my_reviews")
    else:
        form = ReviewForm(instance=review)

    return render(request, "review/edit_review.html", {"form": form, "product": review.product, "order": review.order})

@login_required
def vote_review(request):
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        vote_type = request.POST.get('vote_type') == 'true'
        
        try:
            review = Review.objects.get(id=review_id)
            vote, created = Vote.objects.update_or_create(
                user=request.user,
                review=review,
                defaults={'vote_type': vote_type}
            )
            
            # Get fresh counts from database
            like_count = Vote.objects.filter(review=review, vote_type=True).count()
            dislike_count = Vote.objects.filter(review=review, vote_type=False).count()
            
            return JsonResponse({
                'status': 'success',
                'like_count': like_count,
                'dislike_count': dislike_count
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})