"""
Defining models for the database
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# For customers
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, blank=True)
    phone_number = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if not self.code:
            last_customer = Customer.objects.order_by('-id').first()
            if last_customer and last_customer.code.isdigit():
                next_code = str(int(last_customer.code) + 1).zfill(6)
            else:
                next_code = "000001"
            self.code = next_code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"
    
# For orders
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    item = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f"{self.item} - {self.amount} for {self.customer.name}"

"""

"""