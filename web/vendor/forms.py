from django import forms
from ecommerce.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'price', 'description', 'thumbnail_image', 'stock_quantity']