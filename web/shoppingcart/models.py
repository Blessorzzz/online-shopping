from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from ecommerce.models import Product
from django.utils import timezone
import uuid

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} for {self.user.username}"

class Order(models.Model):
    STATUS_CHOICES_TANGIBLE = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
        ('hold', 'Hold'),
        ('delivered', 'Delivered')
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
    delivered_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = f'PO-{uuid.uuid4().hex[:10].upper()}'
        
        super().save(*args, **kwargs)

        product_type = self.items.first().product.product_type if self.items.exists() else 'tangible'
        if product_type == 'tangible':
            self._meta.get_field('status').choices = self.STATUS_CHOICES_TANGIBLE
        else:
            self._meta.get_field('status').choices = self.STATUS_CHOICES_VIRTUAL

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
                    'refunded': 'refund_date',
                    'delivered': 'delivered_date',
                }
                date_field = status_date_map.get(current_status)
                if date_field:
                    setattr(self, date_field, now)

    def can_be_reviewed(self):
        """Check if the order can be reviewed."""
        return self.status in ['complete', 'refunded', 'delivered']

    @property
    def verified_purchase(self):
        """Return True if the order is eligible for verified purchase."""
        return self.status in ['complete', 'delivered']

    @property
    def products(self):
        """Return all products in the order."""
        return [item.product for item in self.items.all()]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price