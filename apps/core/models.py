"""
Defining models for the database
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.inventory.models import InventoryItem
from django.core.exceptions import ValidationError

# For customers
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)

    def clean(self):
        if not self.phone_number.startswith('+254'):
            raise ValidationError("Phone number must start with +254.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Calls clean()
        if not self.code:
            last_customer = Customer.objects.order_by('-id').first()
            next_code = str(int(last_customer.code) + 1).zfill(6) if last_customer and last_customer.code.isdigit() else "000001"
            self.code = next_code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"
    
# For orders
class Order(models.Model):

    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='orders')
    item = models.CharField(max_length=100)  # To be deprecated after adding OrderItem
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # To be deprecated too
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.customer.name} | {self.status}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
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