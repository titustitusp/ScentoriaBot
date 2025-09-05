import os
import time
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from keep_alive import keep_alive

# Twilio credentials (from Render Environment Variables)
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TO = os.getenv("WHATSAPP_TO")  # e.g. whatsapp:+91XXXXXXXXXX
FROM = "whatsapp:+14155238886"  # Twilio Sandbox number

client = Client(ACCOUNT_SID, AUTH_TOKEN)
URL = "https://scentoria.co.in"

seen_products = set()

def send_whatsapp(message):
    client.messages.create(
        body=message,
        from_=FROM,
        to=TO
    )

def check_site():
    global seen_products
    try:
        r = requests.get(URL, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        products = [p.get_text(strip=True) for p in soup.find_all("h2", class_="woo-loop-product__title")]
        new_found = []

        for product in products:
            if "partial" in product.lower() and product not in seen_products:
                new_found.append(product)
                seen_products.add(product)

        for p in new_found:
            send_whatsapp(f"New Partial Product Found: {p}")
            print(f"Sent WhatsApp: {p}")

    except Exception as e:
        print(f"Error: {e}")

def main():
    keep_alive()  # start Flask keep-alive server
    print("Bot started. Monitoring for 'partial' products...")
    while True:
        check_site()
        time.sleep(300)  # check every 5 minutes

if __name__ == "__main__":
    main()
