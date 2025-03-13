from django.db import models
from django.contrib.auth.models import User
from ecommerce.models import Product
from shoppingcart.models import Order
from django.conf import settings
from decimal import Decimal

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    video = models.FileField(upload_to='review_videos/', blank=True, null=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.product_name}"

    def is_verified_purchase(self):
        """Check if the review is from a verified purchase"""
        return self.order.status in ['Completed', 'Delivered', 'Refunded']
