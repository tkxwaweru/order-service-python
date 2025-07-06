# apps/inventory/tests.py
from django.test import TestCase
from .models import InventoryItem

class InventoryItemModelTest(TestCase):
    def test_create_inventory_item(self):
        item = InventoryItem.objects.create(
            name="Test Widget",
            description="A sample widget",
            on_hand=10,
            warn_limit=5
        )
        self.assertEqual(item.name, "Test Widget")
        self.assertEqual(item.state, "AVAILABLE")

    def test_state_few_remaining(self):
        item = InventoryItem.objects.create(
            name="Low Stock Item",
            description="Nearly out of stock",
            on_hand=3,
            warn_limit=5
        )
        self.assertEqual(item.state, "FEW_REMAINING")

    def test_state_out_of_stock(self):
        item = InventoryItem.objects.create(
            name="Out of Stock Item",
            description="None left",
            on_hand=0,
            warn_limit=5
        )
        self.assertEqual(item.state, "OUT_OF_STOCK")
