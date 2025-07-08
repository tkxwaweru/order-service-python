import pytest
from django.urls import reverse
from model_bakery import baker
from django.contrib.auth.models import AnonymousUser
from django.test import Client
from weasyprint import HTML
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from apps.core.models import Order, OrderItem
from apps.inventory.models import InventoryItem

pytestmark = pytest.mark.django_db


@override_settings(ROOT_URLCONF="config.urls")  # Adjust if using custom URLs
def test_order_receipt_pdf_authenticated_user(client):
    # Create user and log them in
    user = baker.make(get_user_model(), phone_number="+254712345678")
    client.force_login(user)

    # Create customer tied to user
    customer = baker.make("core.Customer", user=user, phone_number="+254712345678")

    # Create inventory items
    item1 = baker.make(InventoryItem, name="Item A", price=100, on_hand=10)
    item2 = baker.make(InventoryItem, name="Item B", price=50, on_hand=10)

    # Create order and order items
    order = baker.make(Order, customer=customer)
    baker.make(OrderItem, order=order, item=item1, quantity=2, price_at_order=item1.price)
    baker.make(OrderItem, order=order, item=item2, quantity=3, price_at_order=item2.price)

    url = reverse("order_receipt_pdf", kwargs={"order_id": order.id})
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert f'filename="order_{order.id}_receipt.pdf"' in response["Content-Disposition"]
    assert isinstance(response.content, bytes)
    assert len(response.content) > 1000  # Ensure PDF was rendered


def test_order_receipt_pdf_unauthenticated_redirect(client):
    # Create order with valid customer
    customer = baker.make("core.Customer", phone_number="+254700000000")
    order = baker.make(Order, customer=customer)

    response = client.get(reverse("order_receipt_pdf", args=[order.id]))
    assert response.status_code == 302
    assert "/accounts/login/" in response.url