import os
from dotenv import load_dotenv
import africastalking

# Load environment variables from .env
load_dotenv()

# Initialize Africa's Talking
africastalking.initialize(
    username=os.getenv("AT_USERNAME"),
    api_key=os.getenv("AT_API_KEY")
)

# SMS service
sms = africastalking.SMS

def send_sms(phone, message):
    try:
        response = sms.send(message, [phone])
        print(f"SMS sent: {response}")
    except Exception as e:
        print(f"Error sending SMS: {e}")
