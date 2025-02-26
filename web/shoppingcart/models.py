from django.db import models
from django.contrib.auth.models import User
from ecommerce.models import Product  # 引用 Product 模型
from django.utils import timezone
import uuid  # 生成唯一 P.O. 号
from django.shortcuts import render

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联到 User 模型
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # 关联到 Product 模型
    quantity = models.PositiveIntegerField(default=1)  # 默认购买数量为 1
    created_at = models.DateTimeField(auto_now_add=True)  # 自动记录创建时间

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
    purchase_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    shipment_date = models.DateTimeField(null=True, blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    ticket_issue_date = models.DateTimeField(null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    hold_date = models.DateTimeField(null=True, blank=True)  # 新增hold状态对应的时间字段
    complete_date = models.DateTimeField(null=True, blank=True)  # 新增complete状态对应的时间字段
    pending_date = models.DateTimeField(null=True, blank=True)  # 新增pending状态对应的时间字段

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
    purchase_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    shipment_date = models.DateTimeField(null=True, blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    ticket_issue_date = models.DateTimeField(null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
<<<<<<< HEAD
    hold_date = models.DateTimeField(null=True, blank=True)
    complete_date = models.DateTimeField(null=True, blank=True)
    pending_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # 生成PO号（仅创建时）
        if not self.po_number:
            self.po_number = f'PO-{uuid.uuid4().hex[:10].upper()}'
            # 首次保存生成 id 和 po_number
            super().save(*args, **kwargs)
        else:
            # 后续更新时，仅在状态变更时更新时间字段
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
            # 保存更新
            super().save(*args, **kwargs)
=======
    hold_date = models.DateTimeField(null=True, blank=True)  # 新增hold状态对应的时间字段
    complete_date = models.DateTimeField(null=True, blank=True)  # 新增complete状态对应的时间字段
    pending_date = models.DateTimeField(null=True, blank=True)  # 新增pending状态对应的时间字段

    # shoppingcart/models.py (Order类)
    def save(self, *args, **kwargs):
        # 生成PO号（仅创建时）
        if not self.po_number:  
            self.po_number = f'PO-{uuid.uuid4().hex[:10].upper()}'
            super().save(*args, **kwargs) 
        
        # 获取原始状态（必须放在首次保存之后）
        if self.pk:
            original = Order.objects.get(pk=self.pk)
            current_status = self.status
            
            # 仅在状态变更时记录时间
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
        
        # 最终保存更新
        super().save(*args, **kwargs)
<<<<<<< HEAD
>>>>>>> 80523284 (11)
=======
    hold_date = models.DateTimeField(null=True, blank=True)
    complete_date = models.DateTimeField(null=True, blank=True)
    pending_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # 生成PO号（仅创建时）
        if not self.po_number:
            self.po_number = f'PO-{uuid.uuid4().hex[:10].upper()}'
            # 首次保存生成 id 和 po_number
            super().save(*args, **kwargs)
        else:
            # 后续更新时，仅在状态变更时更新时间字段
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
            # 保存更新
            super().save(*args, **kwargs)
>>>>>>> 9fb70b71 (1)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price