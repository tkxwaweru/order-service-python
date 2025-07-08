import pytest
from model_bakery import baker
from decimal import Decimal
from django.core.exceptions import ValidationError
from unittest.mock import patch

from apps.core.models import Customer, Order, OrderItem
from apps.inventory.models import InventoryItem

# CUSTOMER MODEL TESTS
@pytest.mark.django_db
def test_customer_str_representation():
    customer = baker.make(Customer, name="Jane Doe", phone_number="+254712345678")
    assert str(customer) == f"{customer.name} ({customer.code})"

@pytest.mark.django_db
def test_customer_phone_number_validation():
    customer = Customer(name="Invalid", phone_number="0712345678")
    with pytest.raises(ValidationError) as exc:
        customer.full_clean()
    assert "Phone number must start with +254." in str(exc.value)

@pytest.mark.django_db
def test_customer_code_auto_generation():
    c1 = baker.make(Customer, phone_number="+254711111111", code="000099")
    c2 = baker.make(Customer, phone_number="+254722222222", code="000100")
    c3 = Customer(name="New", phone_number="+254733333333")
    c3.save()
    assert c3.code == "000101"

# ORDER MODEL TESTS
@pytest.mark.django_db
def test_order_str_representation():
    customer = baker.make(Customer, name="John", phone_number="+254712345678")
    order = baker.make(Order, customer=customer, status=Order.Status.APPROVED)
    assert str(order) == "John | APPROVED"

@pytest.mark.django_db
def test_order_total_price_computation():
    customer = baker.make(Customer, phone_number="+254700000000")
    order = baker.make(Order, customer=customer)
    item1 = baker.make(InventoryItem, price=Decimal("100.00"))
    item2 = baker.make(InventoryItem, price=Decimal("50.00"))

    baker.make(OrderItem, order=order, item=item1, quantity=2, price_at_order=item1.price)
    baker.make(OrderItem, order=order, item=item2, quantity=1, price_at_order=item2.price)

    assert order.total_price == Decimal("250.00")

@pytest.mark.django_db
@patch("common.utils.send_order_status_sms")
def test_order_sms_triggered_on_status_change(mock_sms):
    customer = baker.make(Customer, phone_number="+254711111111")
    order = baker.make(Order, customer=customer, status=Order.Status.CREATED)
    order.status = Order.Status.DELIVERED
    order.save()
    mock_sms.assert_called_once_with(order)

@pytest.mark.django_db
@patch("common.utils.send_order_status_sms")
def test_order_sms_not_triggered_if_status_unchanged(mock_sms):
    customer = baker.make(Customer, phone_number="+254700000000")
    order = baker.make(Order, customer=customer, status=Order.Status.PENDING)
    order.amount = Decimal("500.00")  # Change unrelated field
    order.save()
    mock_sms.assert_not_called()

# ORDER ITEM TESTS
@pytest.mark.django_db
def test_order_item_str_representation():
    customer = baker.make(Customer, phone_number="+254722000000")
    order = baker.make(Order, customer=customer)
    item = baker.make(InventoryItem, name="Sugar")
    order_item = baker.make(OrderItem, order=order, item=item, quantity=2)
    assert str(order_item) == "Sugar x 2"

@pytest.mark.django_db
def test_order_item_total_price():
    customer = baker.make(Customer, phone_number="+254733000000")
    order = baker.make(Order, customer=customer)
    item = baker.make(InventoryItem, price=Decimal("100.00"))
    order_item = baker.make(OrderItem, order=order, item=item, quantity=3, price_at_order=Decimal("100.00"))
    assert order_item.total_price == Decimal("300.00")
