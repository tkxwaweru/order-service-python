import africastalking
import os

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
    """
    if not sms:
        print("SMS not sent: SMS client not initialized.")
        return

    try:
        response = sms.send(message, [phone_number])
        print("SMS sent:", response)
    except Exception as e:
        print("SMS failed:", e)


def send_order_confirmation_sms(order, summary=None):
    """
    High-level order SMS interface.
    """
    if not order.customer.phone_number:
        print("No phone number provided.")
        return

    if summary:
        message = f"Hi {order.customer.name}, your order has been received: {summary}. Total: Ksh {order.amount}."
    else:
        message = f"Hi {order.customer.name}, your order for '{order.item}' (Ksh {order.amount}) has been received."

    send_order_sms(order.customer.phone_number, message)


def notify_shop_employee_stock_low(item_name, remaining_qty):
    """
    Future logic: notify shop employee when stock is low.
    """
    print(f"Stock alert: {item_name} has only {remaining_qty} items left!")
