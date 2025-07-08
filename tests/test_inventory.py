import pytest
from unittest.mock import patch
from apps.inventory.models import InventoryItem


@pytest.mark.django_db
@pytest.mark.parametrize(
    "on_hand, warn_limit, expected_state",
    [
        (0, 5, "OUT_OF_STOCK"),
        (3, 5, "FEW_REMAINING"),
        (10, 5, "AVAILABLE"),
    ],
)
def test_inventory_state_property(on_hand, warn_limit, expected_state):
    item = InventoryItem.objects.create(
        name="Test Item",
        price=100,
        on_hand=on_hand,
        warn_limit=warn_limit
    )
    assert item.state == expected_state


@pytest.mark.django_db
def test_inventory_str_includes_name_and_state():
    item = InventoryItem.objects.create(
        name="Test Product",
        price=200,
        on_hand=10,
        warn_limit=5
    )
    assert str(item) == "Test Product (AVAILABLE)"


@pytest.mark.django_db
@patch("apps.inventory.models.notify_shop_employee_stock_low")
def test_notify_on_stock_drop(mock_notify):
    # Create item with stock above warn limit
    item = InventoryItem.objects.create(
        name="Sugar",
        price=50,
        on_hand=10,
        warn_limit=5
    )

    # Drop stock below warn limit
    item.on_hand = 3
    item.save()

    mock_notify.assert_called_once_with("Sugar", 3)


@pytest.mark.django_db
@patch("apps.inventory.models.notify_shop_employee_stock_low")
def test_no_notify_if_stock_still_above_warn_limit(mock_notify):
    item = InventoryItem.objects.create(
        name="Milk",
        price=30,
        on_hand=10,
        warn_limit=5
    )

    # Update but stay above warn limit
    item.description = "Updated description"
    item.save()

    mock_notify.assert_not_called()
