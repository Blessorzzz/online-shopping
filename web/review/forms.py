from django import forms
from .models import Review
from better_profanity import profanity

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'image', 'video']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.5, 'class': 'form-control rating-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if profanity.contains_profanity(comment):
            raise forms.ValidationError("Your review contains inappropriate language. Please edit and try again.")
        return comment

class ReviewAdminForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'

    # You can also apply custom validation if needed
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not (1 <= rating <= 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating