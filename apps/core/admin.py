from django.contrib import admin
from .models import Customer, Order, OrderItem
from apps.inventory.models import InventoryItem  

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'timestamp']
    list_filter = ['status']
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        """
        Ensure custom save logic runs (including SMS notification).
        """
        obj.save()  # This triggers overridden save() with status check

admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(InventoryItem)
