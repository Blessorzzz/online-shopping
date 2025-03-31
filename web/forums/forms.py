from django import forms
from .models import ForumPost, Comment
from better_profanity import profanity

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['title']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        # Censor offensive words in the title
        return profanity.censor(title)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get('content')
        # Censor offensive words in the content
        return profanity.censor(content)