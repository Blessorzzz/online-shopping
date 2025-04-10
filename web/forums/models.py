from django.db import models
from django.contrib.auth.models import User
import uuid
from ecommerce.models import Product  # Import Product model from eCommerce app

class ForumPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='forum_posts')
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    forum_post = models.ForeignKey('ForumPost', related_name='comments', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    reports = models.JSONField(default=list, blank=True)

    def liked_users_ids(self):
        return list(self.votes.filter(vote_type=True).values_list('user__id', flat=True))

    def disliked_users_ids(self):
        return list(self.votes.filter(vote_type=False).values_list('user__id', flat=True))

    def __str__(self):
        return f'Comment by {self.author.username if self.author else "Anonymous"}'

# Proxy model for reported comments
class ReportedComment(Comment):
    class Meta:
        proxy = True
        verbose_name = "Reported Comment"
        verbose_name_plural = "Reported Comments"

class Vote(models.Model):
    LIKE = True
    DISLIKE = False
    VOTE_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='forum_votes'  # Unique related_name for forums app
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.BooleanField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')  # Prevent duplicate votes

    def __str__(self):
        return f"{self.user} voted {self.get_vote_type_display()} on {self.comment}"