# tests/test_views.py

import pytest
import subprocess
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from model_bakery import baker
from unittest import mock
from apps.core.models import Order, OrderItem, Customer
from apps.inventory.models import InventoryItem
from common.models import SentSMS

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user():
    return baker.make(User, phone_number='+254712345678')

@pytest.fixture
def staff_user():
    return baker.make(User, is_staff=True, phone_number='+254712300000')

@pytest.fixture
def superuser():
    return baker.make(User, is_superuser=True, phone_number='+254799999999')

@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client

@pytest.fixture
def staff_client(client, staff_user):
    client.force_login(staff_user)
    return client

@pytest.fixture
def inventory_item():
    return baker.make(InventoryItem, on_hand=10, warn_limit=5)


def test_home_view(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert b"html" in response.content.lower()


def test_manual_login_success(client, user):
    user.set_password("pass123")
    user.save()
    response = client.post(reverse("manual_login"), {
        "username": user.username,
        "password": "pass123"
    })
    assert response.status_code == 302


def test_manual_login_failure(client):
    response = client.post(reverse("manual_login"), {
        "username": "nonexistent",
        "password": "wrong"
    })
    assert response.status_code == 200
    assert b"login_error" in response.content or b"Login" in response.content


def test_admin_dashboard_view_authenticated(staff_client):
    response = staff_client.get(reverse("admin_dashboard"))
    assert response.status_code == 200


def test_admin_dashboard_view_unauthorized(client):
    response = client.get(reverse("admin_dashboard"))
    assert response.status_code == 302  # redirects to login


def test_inventory_summary_view_permission(staff_client):
    response = staff_client.get(reverse("inventory_summary"))
    assert response.status_code == 200


def test_inventory_summary_view_forbidden(authenticated_client):
    response = authenticated_client.get(reverse("inventory_summary"))
    assert response.status_code in [302, 403]


def test_order_summary_view_permission(staff_client):
    response = staff_client.get(reverse("order_summary"))
    assert response.status_code == 200


def test_order_form_view_get(inventory_item):
    user = baker.make(User, phone_number="+254700000000")
    client = Client()
    client.force_login(user)

    # Ensure this user has a linked Customer (required by order_form_view)
    baker.make(Customer, user=user, phone_number="+254700000000")

    response = client.get(reverse("order_form"))
    assert response.status_code == 200

@mock.patch("apps.core.views.send_order_confirmation_sms")
@mock.patch("apps.core.views.notify_shop_employee_stock_low")
def test_order_form_view_post_valid(
    mock_notify, mock_sms, authenticated_client, inventory_item, user
):
    user.customer = baker.make("core.Customer", user=user, name="John Doe", phone_number="+254700000000")

    cart_data = [{"id": inventory_item.id, "qty": 2}]
    response = authenticated_client.post(
        reverse("order_form"),
        data={"cart_data": json.dumps(cart_data)},
        follow=True
    )

    assert response.status_code == 200
    assert Order.objects.count() == 1
    assert OrderItem.objects.count() == 1
    mock_sms.assert_called_once()


def test_order_form_view_post_invalid_cart(authenticated_client):
    response = authenticated_client.post(reverse("order_form"), data={"cart_data": "invalid"})
    assert response.status_code == 302
    assert Order.objects.count() == 0


def test_logout_view(authenticated_client):
    response = authenticated_client.get(reverse("logout"))
    assert response.status_code == 302
    assert response.url == reverse("home")


@mock.patch("weasyprint.HTML.write_pdf")
def test_order_receipt_pdf(mock_pdf, authenticated_client, user):
    customer = baker.make("core.Customer", user=user, phone_number="+254700000000")
    order = baker.make(Order, customer=customer)

    response = authenticated_client.get(reverse("order_receipt_pdf", args=[order.id]))
    assert response.status_code == 200
    mock_pdf.assert_called_once()

def test_login_redirect_view_with_customer(authenticated_client, user):
    customer = baker.make(Customer, user=user, phone_number="+254700000000")
    response = authenticated_client.get(reverse("login_redirect"))
    assert response.status_code == 302
    assert response.url == reverse("order_form")


def test_login_redirect_view_no_customer(authenticated_client):
    response = authenticated_client.get(reverse("login_redirect"))
    assert response.status_code == 302
    assert response.url == reverse("register_customer")


def test_register_customer_view_get_authenticated_user(authenticated_client, user):
    response = authenticated_client.get(reverse("register_customer"))
    assert response.status_code == 200
    assert b"<form" in response.content


def test_register_customer_view_get_already_registered(authenticated_client, user):
    baker.make(Customer, user=user, phone_number="+254711223344")
    response = authenticated_client.get(reverse("register_customer"))
    assert response.status_code == 302
    assert response.url == reverse("order_form")


@mock.patch("apps.core.views.send_order_confirmation_sms")
@mock.patch("apps.core.views.notify_shop_employee_stock_low")
def test_order_form_warn_limit_triggers(mock_notify, mock_sms, authenticated_client, user):
    inventory_item = baker.make(InventoryItem, on_hand=2, warn_limit=2)
    customer = baker.make(Customer, user=user, phone_number="+254700000000")
    cart_data = [{"id": inventory_item.id, "qty": 1}]

    response = authenticated_client.post(
        reverse("order_form"),
        data={"cart_data": json.dumps(cart_data)},
        follow=True,
    )

    assert response.status_code == 200
    mock_notify.assert_called_once()


def test_order_form_view_post_empty_cart(authenticated_client, user):
    baker.make(Customer, user=user, phone_number=user.phone_number)
    response = authenticated_client.post(
        reverse("order_form"), data={"cart_data": json.dumps([])}, follow=True
    )
    assert b"Please add at least one item to your order" in response.content



def test_order_form_view_post_nonexistent_item(authenticated_client, user):
    baker.make(Customer, user=user, phone_number=user.phone_number)
    cart_data = [{"id": 9999, "qty": 1}]
    response = authenticated_client.post(
        reverse("order_form"), data={"cart_data": json.dumps(cart_data)}, follow=True
    )
    assert b"Item ID 9999 not found" in response.content



def test_order_form_view_post_exceeds_stock(authenticated_client, inventory_item, user):
    baker.make(Customer, user=user, phone_number="+254722000000")
    cart_data = [{"id": inventory_item.id, "qty": inventory_item.on_hand + 5}]
    response = authenticated_client.post(
        reverse("order_form"), data={"cart_data": json.dumps(cart_data)}, follow=True
    )
    assert b"Not enough stock" in response.content


def test_order_form_view_post_all_items_fail(authenticated_client, inventory_item, user):
    baker.make(Customer, user=user, phone_number="+254722000000")
    inventory_item.on_hand = 0
    inventory_item.save()
    cart_data = [{"id": inventory_item.id, "qty": 1}]
    response = authenticated_client.post(
        reverse("order_form"), data={"cart_data": json.dumps(cart_data)}, follow=True
    )
    assert b"No items could be processed. Order cancelled." in response.content


def test_manual_login_view_get(client):
    response = client.get(reverse("manual_login"))
    assert response.status_code == 200
    assert b"Login" in response.content
