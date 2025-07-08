import africastalking
import os
from django.utils.timezone import now
from common.models import SentSMS, CustomUser

# Initialize Africa's Talking
username = os.getenv("AFRICASTALKING_USERNAME")
api_key = os.getenv("AFRICASTALKING_API_KEY")

sms = None
if username and api_key:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
else:
    print("Skipping Africa's Talking SMS: missing credentials.")


def send_order_sms(phone_number, message):
    """
    Core SMS sending logic using Africa's Talking.
    Also stores the message in the database.
    """
    if not sms:
        print("SMS not sent: SMS client not initialized.")
        return

    try:
        response = sms.send(message, [phone_number])
        print("SMS sent:", response)

        # Extract status from API response
        status = response['SMSMessageData']['Recipients'][0].get('status', 'unknown') \
            if response.get('SMSMessageData', {}).get('Recipients') else 'unknown'

        SentSMS.objects.create(
            phone_number=phone_number,
            message=message,
            status=status,
            sent_at=now()
        )

    except Exception as e:
        print("SMS failed:", e)

        SentSMS.objects.create(
            phone_number=phone_number,
            message=message,
            status="failed",
            sent_at=now()
        )

def send_order_status_sms(order):
    if not order.customer.phone_number:
        print("No customer phone number available.")
        return

    # Get superuser phone number
    admin_user = CustomUser.objects.filter(is_superuser=True).first()
    admin_phone = admin_user.phone_number if admin_user and admin_user.phone_number else "our office"

    if order.status == "DELIVERED":
        message = (
            f"Hi {order.customer.name}, your order #{order.id} has been delivered. "
            f"We'd love to hear your feedback! Feel free to let us know via {admin_phone}. "
            "Thank you for using Order Service!"
        )
    else:
        message = (
            f"Hi {order.customer.name}, your order #{order.id} status is now: {order.status.capitalize()}. "
            f"Feel free to reach out via {admin_phone} for any inquiries."
        )

    send_order_sms(order.customer.phone_number, message)

def send_order_confirmation_sms(order, summary=None):
    """
    Sends SMS to customer when an order is placed.
    """
    if not order.customer.phone_number:
        print("No phone number provided.")
        return

    if summary:
        message = f"Hi {order.customer.name}, your order has been received: {summary}. Total: Ksh {order.amount}."
    else:
        message = f"Hi {order.customer.name}, your order for Ksh {order.amount} has been received."

    send_order_sms(order.customer.phone_number, message)


def notify_shop_employee_stock_low(item_name, remaining_qty):
    message = f"Stock alert: {item_name} is low. Only {remaining_qty} left!"

    staff_users = CustomUser.objects.filter(is_staff=True).exclude(phone_number__isnull=True)
    for user in staff_users:
        send_order_sms(user.phone_number, message)

def generate_order_summary_sms(summary_list):
    """
    Takes a list like ["Item A x2", "Item B x1"] and returns a single summary string.
    """
    return "Order Summary: " + ", ".join(summary_list)
