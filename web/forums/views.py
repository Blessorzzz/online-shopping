from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import ForumPost, Comment
from .forms import ForumPostForm, CommentForm
from django.contrib.auth.decorators import login_required
from ecommerce.models import Product  # Import Product model
from django.db.models import Q

@login_required
def forum_list(request):
    query = request.GET.get('q', '')  # Get search query
    product_id = request.GET.get('product_id')  # Get product_id if provided
    posts = ForumPost.objects.all().order_by('-created_at')  # Get all forum posts
    
    if query:
        # Filter posts by title or author username
        posts = posts.filter(Q(title__icontains=query) | Q(author__username__icontains=query))

    product = None
    if product_id:
        product = get_object_or_404(Product, product_id=product_id)  # Get the related product
    
    return render(request, 'forums/forum_list.html', {
        'posts': posts,
        'query': query,
        'product': product,  # Pass the product to template
    })

@login_required
def forum_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    comments = post.comments.filter(parent_comment__isnull=True).order_by('created_at')
    comment_form = CommentForm()
    return render(request, 'forums/forum_detail.html', {
        'post': post, 'comments': comments, 'comment_form': comment_form
    })
@login_required
def select_product_for_forum(request):
    # Get search term from query parameters
    search_query = request.GET.get('search', '')
    products = Product.objects.all()

    if search_query:
        # Filter products based on the search term
        products = products.filter(Q(product_name__icontains=search_query))

    # Pagination
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    return render(request, 'forums/select_product.html', {  # Corrected template name
        'products': products_page,
        'search_query': search_query,
    })

@login_required
def create_forum_post(request, product_id=None):
    if product_id:
        product = get_object_or_404(Product, product_id=product_id)
    else:
        product = None  # Let the user select a product if none was provided

    if request.method == "POST":
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.product = product
            post.save()
            return redirect("forum_detail", post.id)
    else:
        form = ForumPostForm(initial={"product": product})
    
    return render(request, "forums/create_forum_post.html", {"form": form, "product": product})

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

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        comment.dislikes.remove(request.user)  # Ensure a user can't like and dislike at the same time
        liked = True
    return JsonResponse({'liked': liked, 'like_count': comment.like_count(), 'dislike_count': comment.dislike_count()})

@login_required
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.dislikes.all():
        comment.dislikes.remove(request.user)
        disliked = False
    else:
        comment.dislikes.add(request.user)
        comment.likes.remove(request.user)  # Ensure a user can't like and dislike at the same time
        disliked = True
    return JsonResponse({'disliked': disliked, 'like_count': comment.like_count(), 'dislike_count': comment.dislike_count()})

@login_required
@csrf_exempt
def report_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        report_reasons = request.POST.getlist('reasons[]')  # Get the selected reasons
        if report_reasons:
            comment.reports.extend(report_reasons)  # Add the reasons to the reports field
            comment.save()
            return JsonResponse({'success': True, 'message': 'Report submitted successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})