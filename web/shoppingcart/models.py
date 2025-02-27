from django.db import models
from django.contrib.auth.models import User
from ecommerce.models import Product  # 引用 Product 模型
from django.utils import timezone
import uuid  # 生成唯一 P.O. 号

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联到 User 模型
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # 关联到 Product 模型
    quantity = models.PositiveIntegerField(default=1)  # 默认购买数量为 1
    created_at = models.DateTimeField(auto_now_add=True)  # 自动记录创建时间（UTC）

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} for {self.user.username}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
        ('hold', 'Hold'),
        ('ticket-issued', 'Ticket Issued'),
        ('complete', 'Complete'),
        ('refunded', 'Refunded'),
    ]

    po_number = models.CharField(max_length=20, unique=True, editable=False, default='', null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders', default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    purchase_date = models.DateTimeField(default=timezone.now)  # 存储 UTC 时间
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()

    # 各种状态的时间字段
    shipment_date = models.DateTimeField(null=True, blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    ticket_issue_date = models.DateTimeField(null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    hold_date = models.DateTimeField(null=True, blank=True)
    complete_date = models.DateTimeField(null=True, blank=True)
    pending_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """ 在状态变更时更新相应的时间字段 """
        if not self.po_number:
            self.po_number = f'PO-{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price
