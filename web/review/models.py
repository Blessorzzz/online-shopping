from django.db import models
from django.contrib.auth.models import User
from ecommerce.models import Product
from shoppingcart.models import Order
from better_profanity import profanity  # Import the better_profanity library
from django.utils import timezone

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    video = models.FileField(upload_to='review_videos/', blank=True, null=True)
    last_edited = models.DateTimeField(null=True, blank=True)

    # Vendor response field
    vendor_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.product_name}"

    def is_verified_purchase(self):
        """Return whether the review is a verified purchase based on the order status."""
        return self.order.status in ['complete', 'refunded', 'delivered']
    
    def liked_users_ids(self):
        return list(self.votes.filter(vote_type=True).values_list('user__id', flat=True))
    
    def disliked_users_ids(self):
        return list(self.votes.filter(vote_type=False).values_list('user__id', flat=True))

    def save(self, *args, **kwargs):
        """Override save method to censor offensive language in comment and vendor_response."""
        if self.comment:
            self.comment = profanity.censor(self.comment)  # Automatically censor offensive language in the comment
        if self.vendor_response:
            self.vendor_response = profanity.censor(self.vendor_response)  # Automatically censor offensive language in the vendor response
        if self.pk:
            self.last_edited = timezone.now()
            
        super().save(*args, **kwargs)  # Call the original save method

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
        related_name='review_votes'  # Unique related_name for review app
    )
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.BooleanField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')  # Prevent duplicate votes

    def __str__(self):
        return f"{self.user} voted {self.get_vote_type_display()} on {self.review}"