from django.contrib import admin
from .models import Customer, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'timestamp']
    list_filter = ['status']
    inlines = [OrderItemInline]

admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)