"""
Defining models for the database
"""

from django.db import models
from common.models import CustomUser
from django.utils import timezone
from apps.inventory.models import InventoryItem
from django.core.exceptions import ValidationError
from django.conf import settings

# For customers
class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)

    def clean(self):
        if not self.phone_number:
            raise ValidationError("Phone number is required.")
        if not self.phone_number.startswith('+254'):
            raise ValidationError("Phone number must start with +254.")

    def save(self, *args, **kwargs):
        validate = kwargs.pop("validate", True)
        if validate:
            self.full_clean()

        if not self.code:
            last = Customer.objects.order_by("-id").first()
            last_code = int(last.code or "000000") if last else 0
            self.code = f"{last_code + 1:06d}"

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} ({self.code})"

# For orders
class Order(models.Model):

    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        DELIVERED = 'DELIVERED', 'Delivered'   
        CANCELLED = 'CANCELLED', 'Cancelled'   

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='orders')
    item = models.CharField(max_length=100, blank=True, null=True)  # deprecated
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # deprecated
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.name} | {self.status}"

    @property
    def total_price(self):
        return sum(item.quantity * item.price_at_order for item in self.items.all())

    def save(self, *args, **kwargs):
        status_changed = False

        if self.pk:
            previous = Order.objects.filter(pk=self.pk).first()
            if previous and previous.status != self.status:
                status_changed = True

        super().save(*args, **kwargs)

        if status_changed:
            from common.utils import send_order_status_sms  
            send_order_status_sms(self)

# Ordered items
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.price_at_order
