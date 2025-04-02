from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import ForumPost, Comment
from .forms import ForumPostForm, CommentForm
from django.contrib.auth.decorators import login_required
from ecommerce.models import Product  # Import Product model
from django.db.models import Q

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
    # Get the product and forum post
    product = get_object_or_404(Product, product_id=product_id)
    post = get_object_or_404(ForumPost, id=post_id, product=product)  # Ensure the post belongs to the product
    comments = post.comments.filter(parent_comment__isnull=True).order_by('created_at')
    comment_form = CommentForm()
    
    return render(request, 'forums/forum_detail.html', {
        'product': product,
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
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
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.forum_post = post
            comment.save()
            # Redirect to the forum_detail page with both product_id and post_id
            return redirect('forum_detail', product_id=product_id, post_id=post_id)
    # Redirect back to the forum_detail page even if the form is invalid
    return redirect('forum_detail', product_id=product_id, post_id=post_id)
