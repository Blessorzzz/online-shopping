from django.shortcuts import render, get_object_or_404, redirect
from .models import ForumPost, Comment
from .forms import ForumPostForm, CommentForm
from django.contrib.auth.decorators import login_required
from ecommerce.models import Product  # Import Product model

def forum_list(request):
    posts = ForumPost.objects.all().order_by('-created_at')
    return render(request, 'forums/forum_list.html', {'posts': posts})

def forum_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    comments = post.comments.filter(parent_comment__isnull=True).order_by('created_at')
    comment_form = CommentForm()
    return render(request, 'forums/forum_detail.html', {
        'post': post, 'comments': comments, 'comment_form': comment_form
    })

@login_required
def select_product_for_forum(request):
    products = Product.objects.all()
    return render(request, 'forums/select_product.html', {'products': products})

@login_required
def create_forum_post(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            forum_post = form.save(commit=False)
            forum_post.author = request.user
            forum_post.product = product
            forum_post.save()
            return redirect('forum_detail', post_id=forum_post.id)
    else:
        form = ForumPostForm()
    return render(request, 'forums/create_forum_post.html', {'form': form, 'product': product})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.forum_post = post
            comment.save()
            return redirect('forum_detail', post_id=post.id)
    return redirect('forum_detail', post_id=post.id)
