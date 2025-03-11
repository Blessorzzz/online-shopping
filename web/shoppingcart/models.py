from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from ecommerce.models import Product  # 引用 Product 模型
from django.utils import timezone
import uuid  # 生成唯一 P.O. 号

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联到 User 模型
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # 关联到 Product 模型
    quantity = models.PositiveIntegerField(default=1)  # 默认购买数量为 1
    created_at = models.DateTimeField(auto_now_add=True)  # 自动记录创建时间

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} for {self.user.username}"

class Order(models.Model):
    STATUS_CHOICES_TANGIBLE = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
        ('hold', 'Hold'),
    ]

    STATUS_CHOICES_VIRTUAL = [
        ('pending', 'Pending'),
        ('ticket-issued', 'Ticket Issued'),
        ('complete', 'Complete'),
        ('refunded', 'Refunded'),
    ]

    po_number = models.CharField(max_length=20, unique=True, editable=False, default='', null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders', default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    purchase_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES_TANGIBLE, default='pending')
    shipping_address = models.TextField()
    shipment_date = models.DateTimeField(null=True, blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    ticket_issue_date = models.DateTimeField(null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    hold_date = models.DateTimeField(null=True, blank=True)
    complete_date = models.DateTimeField(null=True, blank=True)
    pending_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Save the order first to get the primary key
        if not self.po_number:
            self.po_number = f'PO-{uuid.uuid4().hex[:10].upper()}'
        
        super().save(*args, **kwargs)

        # Determine the product type
        product_type = self.items.first().product.product_type if self.items.exists() else 'tangible'
        if product_type == 'tangible':
            self._meta.get_field('status').choices = self.STATUS_CHOICES_TANGIBLE
        else:
            self._meta.get_field('status').choices = self.STATUS_CHOICES_VIRTUAL

        # Update status dates on status change
        if self.pk:
            original = Order.objects.get(pk=self.pk)
            current_status = self.status
            if original.status != current_status:
                now = timezone.now()
                status_date_map = {
                    'pending': 'pending_date',
                    'shipped': 'shipment_date',
                    'cancelled': 'cancel_date',
                    'hold': 'hold_date',
                    'ticket-issued': 'ticket_issue_date',
                    'complete': 'complete_date',
                    'refunded': 'refund_date'
                }
                date_field = status_date_map.get(current_status)
                if date_field:
                    setattr(self, date_field, now)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price