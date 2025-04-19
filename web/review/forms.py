from django import forms
from decimal import Decimal
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image', 'video']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 
                'max': 5, 
                'step': 0.1,  # Allow more precise decimal input
                'class': 'form-control rating-input'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': "Write your review here..."
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

    # You can also apply custom validation if needed
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        try:
            rating = Decimal(rating)  # Ensure it's a Decimal
        except:
            raise forms.ValidationError("Invalid rating format.")
        
        if not (Decimal('1.0') <= rating <= Decimal('5.0')):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        
        return rating