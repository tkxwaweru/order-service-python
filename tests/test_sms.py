import pytest
from model_bakery import baker
from unittest.mock import patch
from common.utils import (
    send_order_confirmation_sms,
    send_order_status_sms,
    notify_shop_employee_stock_low,
)
from common.models import SentSMS, CustomUser
from apps.core.models import Order

@pytest.mark.django_db
@patch("common.utils.sms")
def test_send_order_confirmation_sms_with_summary(mock_sms):
    mock_sms.send.return_value = {
        "SMSMessageData": {"Recipients": [{"status": "Success"}]}
    }

    customer = baker.make("core.Customer", phone_number="+254712345678")
    order = baker.make(Order, customer=customer, amount=3000.00)

    send_order_confirmation_sms(order, summary="Phone x1, Charger x2")

    sms_log = SentSMS.objects.latest("sent_at")
    assert sms_log.phone_number == order.customer.phone_number
    assert "Phone x1" in sms_log.message
    assert str(order.amount) in sms_log.message
    assert sms_log.status == "Success"

@pytest.mark.django_db
@patch("common.utils.sms")
def test_send_order_confirmation_sms_without_summary(mock_sms):
    mock_sms.send.return_value = {
        "SMSMessageData": {"Recipients": [{"status": "Success"}]}
    }

    customer = baker.make("core.Customer", phone_number="+254798765432")
    order = baker.make(Order, customer=customer, amount=1000.00)

    send_order_confirmation_sms(order)

    sms_log = SentSMS.objects.latest("sent_at")
    assert "Ksh 1000" in sms_log.message
    assert sms_log.status == "Success"

@pytest.mark.django_db
@patch("common.utils.sms")
def test_send_order_status_sms_delivered(mock_sms):
    mock_sms.send.return_value = {
        "SMSMessageData": {"Recipients": [{"status": "Success"}]}
    }

    admin = baker.make(CustomUser, is_superuser=True, phone_number="+254700000001")
    customer = baker.make("core.Customer", name="Test User", phone_number="+254712300001")
    order = baker.make(Order, customer=customer, status="DELIVERED")

    send_order_status_sms(order)

    sms_log = SentSMS.objects.latest("sent_at")
    assert "delivered" in sms_log.message.lower()
    assert "Test User" in sms_log.message
    assert admin.phone_number in sms_log.message

@pytest.mark.django_db
@patch("common.utils.sms")
def test_send_order_status_sms_pending(mock_sms):
    mock_sms.send.return_value = {
        "SMSMessageData": {"Recipients": [{"status": "Success"}]}
    }

    admin = baker.make(CustomUser, is_superuser=True, phone_number="+254799000000")
    customer = baker.make("core.Customer", name="Jane Doe", phone_number="+254755555555")
    order = baker.make(Order, customer=customer, status="PENDING")

    send_order_status_sms(order)

    sms_log = SentSMS.objects.latest("sent_at")
    assert "pending" in sms_log.message.lower()
    assert "Jane Doe" in sms_log.message
    assert admin.phone_number in sms_log.message

@pytest.mark.django_db
@patch("common.utils.sms")
def test_notify_shop_employee_stock_low(mock_sms):
    mock_sms.send.return_value = {
        "SMSMessageData": {"Recipients": [{"status": "Success"}]}
    }

    staff_1 = baker.make(CustomUser, is_staff=True, phone_number="+254701111111")
    staff_2 = baker.make(CustomUser, is_staff=True, phone_number="+254702222222")
    baker.make(CustomUser, is_staff=True, phone_number=None)  # should be skipped

    notify_shop_employee_stock_low("Laptop", 3)

    assert SentSMS.objects.count() == 2
    messages = SentSMS.objects.values_list("message", flat=True)
    for msg in messages:
        assert "Laptop" in msg
        assert "3 left" in msg

@pytest.mark.django_db
@patch("common.utils.sms", None)
def test_sms_fails_gracefully_when_not_initialized():
    customer = baker.make("core.Customer", phone_number="+254700000000")
    order = baker.make(Order, customer=customer, amount=5000)

    # Should not raise exception even if sms client is None
    send_order_confirmation_sms(order, summary="Item X x1")
    assert SentSMS.objects.count() == 0
