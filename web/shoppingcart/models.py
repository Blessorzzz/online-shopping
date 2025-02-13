# shoppingcart/models.py

from django.db import models
from django.contrib.auth.models import User
from ecommerce.models import Product  # 引用 Product 模型
import uuid  # 生成唯一 P.O. 号

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联到 User 模型
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # 关联到 Product 模型
    quantity = models.PositiveIntegerField(default=1)  # 默认购买数量为 1
    created_at = models.DateTimeField(auto_now_add=True)  # 自动记录创建时间

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} for {self.user.username}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    po_number = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False, 
        default='',  # 先允许为空
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()

    def save(self, *args, **kwargs):
        if not self.po_number:  # **确保 P.O. 号只在创建时生成**
            self.po_number = f'PO-{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.po_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price
