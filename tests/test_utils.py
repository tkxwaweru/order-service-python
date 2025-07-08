# tests/test_utils.py

import pytest
from unittest.mock import patch, MagicMock
from django.utils.timezone import now
from common.utils import (
    send_order_sms,
    send_order_confirmation_sms,
    send_order_status_sms,
    notify_shop_employee_stock_low,
    generate_order_summary_sms
)
from model_bakery import baker
from common.models import SentSMS
from apps.core.models import Order, Customer
from django.contrib.auth import get_user_model


@pytest.mark.django_db
@patch("common.utils.sms")
@patch("common.utils.SentSMS.objects.create")
def test_send_order_sms_success(mock_create, mock_sms):
    mock_response = {
        "SMSMessageData": {
            "Recipients": [
                {"status": "Success"}
            ]
        }
    }
    mock_sms.send.return_value = mock_response

    send_order_sms("+254712345678", "Hello test")
    mock_sms.send.assert_called_once()
    mock_create.assert_called_once()


@pytest.mark.django_db
@patch("common.utils.sms", None)
@patch("common.utils.SentSMS.objects.create")
def test_send_order_sms_with_missing_credentials(mock_create):
    # Should gracefully skip without raising
    send_order_sms("+254712345678", "No creds test")
    mock_create.assert_not_called()


@pytest.mark.django_db
@patch("common.utils.sms")
@patch("common.utils.SentSMS.objects.create")
def test_send_order_sms_failure(mock_create, mock_sms):
    mock_sms.send.side_effect = Exception("API error")
    from common.utils import send_order_sms
    send_order_sms("+254712345678", "Failing message")

    mock_sms.send.assert_called_once()
    mock_create.assert_called_once()
    args, kwargs = mock_create.call_args
    assert kwargs["status"] == "failed"



@pytest.mark.django_db
@patch("common.utils.send_order_sms")
def test_send_order_confirmation_sms_with_summary(mock_send):
    customer = baker.make("core.Customer", phone_number="+254712345678")
    order = baker.make("core.Order", customer=customer, amount=1200)

    send_order_confirmation_sms(order, summary="Laptop x1, Mouse x2")
    mock_send.assert_called_once()
    assert "Laptop x1, Mouse x2" in mock_send.call_args[0][1]


@pytest.mark.django_db
@patch("common.utils.send_order_sms")
def test_send_order_confirmation_sms_without_summary(mock_send):
    customer = baker.make("core.Customer", phone_number="+254712345678")
    order = baker.make("core.Order", customer=customer, amount=850)

    send_order_confirmation_sms(order)
    mock_send.assert_called_once()
    assert f"Ksh {order.amount}" in mock_send.call_args[0][1]


@pytest.mark.django_db
@patch("common.utils.send_order_sms")
def test_send_order_confirmation_sms_missing_phone(mock_send):
    customer = baker.make("core.Customer", phone_number="+254700000000")
    order = baker.make(Order, customer=customer, amount=5000)

    # Simulate a missing phone number without saving to DB
    order.customer.phone_number = None

    from common.utils import send_order_confirmation_sms

    send_order_confirmation_sms(order)

    mock_send.assert_not_called()


@pytest.mark.django_db
@patch("common.utils.send_order_sms")
def test_send_order_status_sms_delivered(mock_send):
    admin = baker.make(get_user_model(), is_superuser=True, phone_number="+254799999999")
    customer = baker.make("core.Customer", phone_number="+254712345678")
    order = baker.make("core.Order", customer=customer, status="DELIVERED")

    send_order_status_sms(order)
    mock_send.assert_called_once()
    assert "delivered" in mock_send.call_args[0][1].lower()


@pytest.mark.django_db
@patch("common.utils.send_order_sms")
def test_send_order_status_sms_other_status(mock_send):
    admin = baker.make(get_user_model(), is_superuser=True, phone_number="+254799999999")
    customer = baker.make("core.Customer", phone_number="+254712345678")
    order = baker.make("core.Order", customer=customer, status="PENDING")

    send_order_status_sms(order)
    mock_send.assert_called_once()
    assert "status is now: Pending" in mock_send.call_args[0][1]


@pytest.mark.django_db
@patch("common.utils.send_order_sms")
def test_notify_shop_employee_stock_low(mock_send):
    staff1 = baker.make(get_user_model(), is_staff=True, phone_number="+254700000001")
    staff2 = baker.make(get_user_model(), is_staff=True, phone_number="+254700000002")

    notify_shop_employee_stock_low("Laptop", 3)

    assert mock_send.call_count == 2
    for call in mock_send.call_args_list:
        assert "Laptop is low" in call[0][1]


def test_generate_order_summary_sms():
    summary = generate_order_summary_sms(["Laptop x2", "Mouse x1"])
    assert summary == "Order Summary: Laptop x2, Mouse x1"
