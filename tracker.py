import requests
from bs4 import BeautifulSoup
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load config
with open("config.json") as f:
    config = json.load(f)

FROM = config["from_email"]
TO = config["to_email"]
SMTP_SERVER = config["smtp_server"]
SMTP_PORT = config["smtp_port"]
SMTP_USER = config["smtp_user"]
SMTP_PASS = config["smtp_pass"]

# Frontier search URL (example)
SEARCH_URL = f"https://www.flyfrontier.com/booking/search?from=LAS&to=SJC"

def get_price():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(SEARCH_URL, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # You'll need to inspect Frontier's HTML to adjust this selector
    prices = soup.find_all("span", class_="fare-price")  # Sample class
    prices = [int(p.text.replace("$", "")) for p in prices if "$" in p.text]
    return min(prices) if prices else None

def send_email(price):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔥 Flight Alert: ${price} from LAS to SJC"
    msg["From"] = FROM
    msg["To"] = TO

    html = f"<html><body><h2>New low fare!</h2><p>Only ${price} to fly LAS → SJC.</p></body></html>"
    part = MIMEText(html, "html")
    msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM, TO, msg.as_string())

def main():
    price = get_price()
    print(f"Current price: ${price}")
    if price and price < 40:
        send_email(price)

if __name__ == "__main__":
    main()
