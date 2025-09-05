import requests
import time
import os
import re
from datetime import datetime, timedelta
from twilio.rest import Client
from keep_alive import keep_alive

URL = "https://scentoria.co.in/collections/all"  # page to monitor
CHECK_KEYWORD = "partial"  # keyword to search for (case-insensitive)
CHECK_INTERVAL = 300  # seconds between checks (5 minutes)

# Store already seen product titles to avoid duplicate alerts
seen_products = set()

# Track next time to send daily alive message
next_alive_time = datetime.now() + timedelta(days=1)


def send_whatsapp_message(body):
    """Send a WhatsApp message using Twilio API"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_to = os.getenv("WHATSAPP_TO")  # e.g., whatsapp:+91XXXXXXXXXX
    whatsapp_from = "whatsapp:+14155238886"  # Twilio Sandbox number

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=whatsapp_from,
        to=whatsapp_to
    )
    print("Message sent:", message.sid)


def check_products():
    """Scrape the site and look for new products with keyword"""
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        html = response.text.lower()

        titles = re.findall(r'alt="([^"]+)"', html)

        for title in titles:
            if CHECK_KEYWORD.lower() in title.lower() and title not in seen_products:
                seen_products.add(title)
                msg = f"🆕 New product found: {title}"
                print(msg)
                send_whatsapp_message(msg)

    except Exception as e:
        print("Error during check:", e)


def send_startup_test_message():
    """Send a one-time test message when bot starts"""
    send_whatsapp_message("✅ Test message from your Scentoria bot (startup check).")


def send_daily_alive_message():
    """Send daily 'I’m alive' status update"""
    global next_alive_time
    now = datetime.now()
    if now >= next_alive_time:
        send_whatsapp_message("🤖 Daily check-in: your Scentoria bot is alive and monitoring.")
        next_alive_time = now + timedelta(days=1)


def main():
    keep_alive()  # start keep-alive server
    print("Bot started. Monitoring for 'partial' products...")

    # Send test WhatsApp message at startup
    send_startup_test_message()

    # Continuous monitoring
    while True:
        check_products()
        send_daily_alive_message()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
