from django import forms
from ecommerce.models import Product
from ecommerce.safety.mhi import MATERIAL_RISK

class ProductForm(forms.ModelForm):
    materials = forms.MultipleChoiceField(
        choices=[(key, key.replace("_", " ").title()) for key in MATERIAL_RISK.keys() if key != "unknown"],
        required=False,
        widget=forms.CheckboxSelectMultiple,  # Use checkboxes for multi-selection
        label="Materials",
        help_text="Select all materials used for this product."
    )

    class Meta:
        model = Product
        fields = [
            'product_name', 'price', 'description', 'thumbnail_image', 
            'stock_quantity', 'min_age', 'max_age', 'product_type', 'materials'
        ]

    def clean(self):
        cleaned_data = super().clean()
        materials = cleaned_data.get('materials')

        # Ensure at least one material is selected
        if not materials:
            raise forms.ValidationError("You must select at least one material for the product.")

        min_age = cleaned_data.get('min_age')
        max_age = cleaned_data.get('max_age')

        if min_age is not None and max_age is not None:
            if min_age > max_age:
                raise forms.ValidationError("Minimum age cannot be greater than maximum age.")

        return cleaned_data