import africastalking
import os

username = os.getenv("AFRICASTALKING_USERNAME")
api_key = os.getenv("AFRICASTALKING_API_KEY")

sms = None
if username and api_key:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
else:
    print("⚠️ Skipping Africa's Talking SMS: missing credentials.")

def send_order_sms(phone_number, message):
    if not sms:
        print("SMS not sent: SMS client not initialized.")
        return

    try:
        response = sms.send(message, [phone_number])
        print("SMS sent:", response)
    except Exception as e:
        print("SMS failed:", e)
