# ecommerce/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product

class HomePageView(ListView):
    model= Product
    template_name='home.html'
    context_object_name = 'products'
    paginate_by = 5  # Number of products per page
    ordering = ['product_name']  # Order by product name

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(product_name__icontains=query).order_by('product_name')
        return Product.objects.all().order_by('product_name')
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'