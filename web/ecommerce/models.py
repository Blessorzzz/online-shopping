from django.db import models
import uuid
class Product(models.Model):
    STATUS_CHOICES = [
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    ]

    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
    help_text='Unique ID for this product across whole shopping mall')
    product_name = models.CharField(max_length=255, default="Unnamed Product")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(default="No description available.")
    thumbnail_image = models.URLField(default="https://via.placeholder.com/150")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,default='enabled')

    def __str__(self):
        return self.product_name

class ProductPhoto(models.Model):
    photo_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos')
    photo_url = models.URLField(default="https://via.placeholder.com/150")

    def __str__(self):
        return f"Photo for {self.product.product_name}"
