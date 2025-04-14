from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import ForumPost, Comment, Vote
from .forms import ForumPostForm, CommentForm
from django.contrib.auth.decorators import login_required
from ecommerce.models import Product  # Import Product model
from django.db.models import Q
from django.http import JsonResponse

@login_required
def forum_list(request, product_id):
    # Get the product by product_id
    product = get_object_or_404(Product, product_id=product_id)
    
    # Get the search query from the request
    query = request.GET.get('q', '')
    
    # Filter forum posts by the product
    posts = ForumPost.objects.filter(product=product).order_by('-created_at')
    
    # If a search query is provided, filter posts by title or author username
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(author__username__icontains=query)
        )
    
    # Render the forum_list template with the filtered posts and product
    return render(request, 'forums/forum_list.html', {
        'posts': posts,
        'query': query,
        'product': product,
    })

@login_required
def forum_detail(request, product_id, post_id):
    product = get_object_or_404(Product, product_id=product_id)
    post = get_object_or_404(ForumPost, id=post_id, product=product)
    comments = post.comments.filter(parent_comment__isnull=True).order_by('created_at')
    comment_form = CommentForm()

    # Check if the user has purchased the product
    user_has_purchased = Order.objects.filter(
        customer=request.user,
        status__in=['complete', 'refunded', 'delivered'],
        items__product=post.product
    ).exists()

    return render(request, 'forums/forum_detail.html', {
        'product': product,
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_purchased': user_has_purchased,
    })


@login_required
def create_forum_post(request, product_id):
    # Get the product by product_id
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.product = product
            post.save()
            # Redirect to the forum_detail page with both product_id and post_id
            return redirect("forum_detail", product_id=product.product_id, post_id=post.id)
    else:
        form = ForumPostForm()

    return render(request, "forums/create_forum_post.html", {
        "form": form,
        "product": product,
    })

@login_required
def add_comment(request, product_id, post_id):
    post = get_object_or_404(ForumPost, id=post_id, product__product_id=product_id)

    # Check if the user has purchased the product
    has_purchased = Order.objects.filter(
        customer=request.user,
        status__in=['complete', 'refunded', 'delivered'],
        items__product=post.product
    ).exists()

    if not has_purchased:
        # Redirect with an error message if the user has not purchased the product
        return redirect('forum_detail', product_id=product_id, post_id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.forum_post = post
            comment.save()
            return redirect('forum_detail', product_id=product_id, post_id=post.id)
    return redirect('forum_detail', product_id=product_id, post_id=post.id)

@login_required
def vote_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        vote_type = request.POST.get('vote_type') == 'true' 

        try:
            comment = get_object_or_404(id=comment_id)
            vote, created = Vote.objects.update_or_create(
                user=request.user,
                comment=comment,
                defaults={'vote_type': vote_type}
            )

            # Get fresh counts from the database
            like_count = Vote.objects.filter(comment=comment, vote_type=True).count()
            dislike_count = Vote.objects.filter(comment=comment, vote_type=False).count()

            return JsonResponse({
                'status': 'success',
                'like_count': like_count,
                'dislike_count': dislike_count,
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def report_comment(request, comment_id):
    """
    Allows users to report a comment with specific reasons.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        report_reasons = request.POST.getlist('reasons')  # Get the selected reasons
        if report_reasons:
            # Ensure the reports field is updated correctly
            comment.reports.extend(report_reasons)
            comment.reports = list(set(comment.reports))  # Remove duplicate reasons
            comment.save()
            return JsonResponse({'success': True, 'message': 'Report submitted successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'No reasons provided.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})