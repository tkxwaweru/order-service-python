from rest_framework import serializers
from .models import Customer, Order, OrderItem
from apps.inventory.models import InventoryItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'code', 'phone_number']

class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'item_name', 'quantity', 'price_at_order', 'total_price']
        read_only_fields = ['total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'timestamp', 'items', 'total_price']