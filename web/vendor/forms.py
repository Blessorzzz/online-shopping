from django import forms
from ecommerce.models import Product, ProductPhoto

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'price', 'description', 'thumbnail_image', 'stock_quantity', 'min_age', 'max_age', 'product_type']  # Include product_type

    def clean(self):
        cleaned_data = super().clean()
        min_age = cleaned_data.get('min_age')
        max_age = cleaned_data.get('max_age')

        if min_age is not None and max_age is not None:
            if min_age > max_age:
                raise forms.ValidationError("Minimum age cannot be greater than maximum age.")
        return cleaned_data
