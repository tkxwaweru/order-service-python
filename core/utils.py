import africastalking
import os

username = "sandbox" 
api_key = os.getenv("AT_API_KEY")

africastalking.initialize(username, api_key)
sms = africastalking.SMS

def send_order_sms(phone_number, message):
    try:
        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        return {"error": str(e)}
