import pytest
from decimal import Decimal
from model_bakery import baker
from django.core.exceptions import ValidationError
from unittest.mock import patch

from apps.core.models import Order, OrderItem, Customer
from apps.inventory.models import InventoryItem


@pytest.mark.django_db
def test_orderitem_total_price_calculation():
    item = baker.make(InventoryItem, price=Decimal("100.00"))
    customer = baker.make(Customer, phone_number="+254711111111")
    order = baker.make(Order, customer=customer)
    order_item = baker.make(OrderItem, order=order, item=item, quantity=3, price_at_order=item.price)
    assert order_item.total_price == Decimal("300.00")


@pytest.mark.django_db
def test_order_total_price_aggregates_items():
    customer = baker.make(Customer, phone_number="+254722222222")
    order = baker.make(Order, customer=customer)
    item1 = baker.make(InventoryItem, price=Decimal("50.00"))
    item2 = baker.make(InventoryItem, price=Decimal("25.00"))

    baker.make(OrderItem, order=order, item=item1, quantity=2, price_at_order=item1.price)
    baker.make(OrderItem, order=order, item=item2, quantity=4, price_at_order=item2.price)

    expected_total = (2 * Decimal("50.00")) + (4 * Decimal("25.00"))
    assert order.total_price == expected_total


@pytest.mark.django_db
def test_order_str_representation():
    customer = baker.make(Customer, name="Test Customer", phone_number="+254733333333")
    order = baker.make(Order, customer=customer, status=Order.Status.APPROVED)
    assert str(order) == "Test Customer | APPROVED"


@pytest.mark.django_db
def test_orderitem_str_representation():
    inventory_item = baker.make(InventoryItem, name="Monitor", price=Decimal("20000.00"))
    customer = baker.make(Customer, phone_number="+254744444444")
    order = baker.make(Order, customer=customer)
    order_item = baker.make(OrderItem, order=order, item=inventory_item, quantity=2, price_at_order=inventory_item.price)
    assert str(order_item) == "Monitor x 2"


@pytest.mark.django_db
@patch("common.utils.send_order_status_sms")
def test_order_status_change_triggers_sms(mock_send_sms):
    customer = baker.make(Customer, phone_number="+254755555555")
    order = baker.make(Order, status=Order.Status.CREATED, customer=customer)
    order.status = Order.Status.APPROVED
    order.save()

    mock_send_sms.assert_called_once_with(order)


@pytest.mark.django_db
@patch("common.utils.send_order_status_sms")
def test_order_status_no_change_does_not_trigger_sms(mock_send_sms):
    customer = baker.make(Customer, phone_number="+254766666666")
    order = baker.make(Order, status=Order.Status.CREATED, customer=customer)
    order.status = Order.Status.CREATED  # No change
    order.save()

    mock_send_sms.assert_not_called()


@pytest.mark.django_db
def test_order_total_price_empty_returns_zero():
    customer = baker.make(Customer, phone_number="+254777777777")
    order = baker.make(Order, customer=customer)
    assert order.total_price == 0


@pytest.mark.django_db
def test_order_item_quantity_and_price_tracking():
    inventory_item = baker.make(InventoryItem, price=Decimal("123.45"))
    customer = baker.make(Customer, phone_number="+254788888888")
    order = baker.make(Order, customer=customer)
    order_item = baker.make(OrderItem, order=order, item=inventory_item, quantity=5, price_at_order=Decimal("123.45"))

    assert order_item.quantity == 5
    assert order_item.price_at_order == Decimal("123.45")
    assert order_item.total_price == Decimal("617.25")


@pytest.mark.django_db
def test_order_deprecated_amount_field_preserved():
    customer = baker.make(Customer, phone_number="+254799999999")
    order = baker.make(Order, amount=Decimal("9999.99"), customer=customer)
    assert order.amount == Decimal("9999.99")
