from django.db import models
from django.contrib.auth import get_user_model
from common.utils import notify_shop_employee_stock_low


class InventoryItem(models.Model):
    STATE_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('FEW_REMAINING', 'Few Remaining'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    on_hand = models.PositiveIntegerField(default=0)
    warn_limit = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Alert if on_hand drops below warn_limit
        if self.pk:  # only check if updating
            previous = InventoryItem.objects.get(pk=self.pk)
            if previous.on_hand > self.warn_limit and self.on_hand <= self.warn_limit:
                notify_shop_employee_stock_low(self.name, self.on_hand)

        super().save(*args, **kwargs)

    @property
    def state(self):
        if self.on_hand == 0:
            return 'OUT_OF_STOCK'
        elif self.on_hand <= self.warn_limit:
            return 'FEW_REMAINING'
        return 'AVAILABLE'

    def __str__(self):
        return f"{self.name} ({self.state})"


