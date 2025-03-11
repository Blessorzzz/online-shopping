# ecommerce/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Q
from .models import Product
from shoppingcart.models import ShoppingCart  # 引用购物车模型
from review.models import Review

# 首页视图，显示商品列表
class HomePageView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'
    paginate_by = 8  # 每页显示的商品数


    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(product_name__icontains=query)
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"Total products: {self.get_queryset().count()}")
        print(f"Number of pages: {context['paginator'].num_pages}")
        return context

# 商品详情页视图
# ecommerce/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.db.models import Q
from .models import Product
from shoppingcart.models import ShoppingCart  # 引用购物车模型
from review.models import Review

# 首页视图，显示商品列表
class HomePageView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'
    paginate_by = 8  # 每页显示的商品数

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(product_name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"Total products: {self.get_queryset().count()}")
        print(f"Number of pages: {context['paginator'].num_pages}")
        return context

# 商品详情页视图
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        reviews = Review.objects.filter(product=product, is_approved=True).order_by("-created_at")
        print(f"Product: {product}")
        print(f"Reviews: {reviews}")
        context['reviews'] = reviews
        return context

# 购物车页面视图
class CartView(ListView):
    model = ShoppingCart
    template_name = 'view_cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        # 获取当前用户的购物车项
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 计算购物车总金额
        cart_items = context['cart_items']
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        context['total_amount'] = total_amount
        return context

# 更新购物车商品数量视图
class UpdateCartView(UpdateView):
    model = ShoppingCart
    fields = ['quantity']
    template_name = 'update_cart.html'

    def form_valid(self, form):
        cart_item = form.save(commit=False)
        cart_item.user = self.request.user  # 确保是当前用户的购物车项
        cart_item.save()
        return redirect('view_cart')  # 更新成功后重定向到购物车页面

# 删除购物车商品视图
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(ShoppingCart, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')  # 删除后重定向到购物车页面

# filter products by query
def product_list(request):
    query = request.GET.get('q', '')
    
    # Ensure the product query only includes active products
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(product_name__icontains=query) | Q(product_id__icontains=query)
        )
    
    return render(request, 'product_list.html', {'products': products})