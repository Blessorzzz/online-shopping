from django.db import models
import uuid
from vendor.models import Vendor

class Product(models.Model):
    STATUS_CHOICES = [
        ('stock', 'Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]

    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  help_text='Unique ID for this product across whole shopping mall')
    product_name = models.CharField(max_length=255, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default="")
    is_active = models.BooleanField(default=True)
    description = models.TextField(default="")
    thumbnail_image = models.ImageField(upload_to='product_thumbnails/', default="https://via.placeholder.com/150")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products', default=1)
    stock_quantity = models.PositiveIntegerField(default="")
    min_age = models.PositiveIntegerField(default="", help_text="Minimum age suitable for the product")
    max_age = models.PositiveIntegerField(default="", help_text="Maximum age suitable for the product")

    def __str__(self):
        return self.product_name
    
    def stock_status(self):
        return 'Out of Stock' if self.stock_quantity == 0 else f'{self.stock_quantity} Available'

    def age_range(self):
        return f'{self.min_age}-{self.max_age} years old'

class ProductPhoto(models.Model):
    photo_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos')
    photo_url = models.URLField(default="https://via.placeholder.com/150")

    def __str__(self):
        return f"Photo for {self.product.product_name}"