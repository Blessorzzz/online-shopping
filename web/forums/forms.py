from django import forms
from .models import ForumPost, Comment

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['title']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
