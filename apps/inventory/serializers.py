from rest_framework import serializers
from apps.inventory.models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    availability = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'description', 'on_hand', 'warn_limit', 'availability', 'created_at', 'updated_at']
