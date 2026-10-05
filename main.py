"""Amazon price tracker — scrapes a product page and emails when price is at/below target."""
import os
import re
import smtplib
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
EMAIL_2 = os.getenv("EMAIL_2")
PRODUCT_URL = os.getenv(
    "PRODUCT_URL",
    "https://www.amazon.co.uk/Instant-Pot-Nova-Multi-Use-Stainless/dp/B08V5KCDXC",
)
BUY_PRICE = float(os.getenv("BUY_PRICE", "100"))
CURRENCY_HINT = os.getenv("CURRENCY_HINT", "GBP")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/132.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}

PRICE_RE = re.compile(r"(\d+(?:\.\d+)?)")


def parse_price(soup: BeautifulSoup):
    candidates = []
    off = soup.find("span", class_="aok-offscreen")
    if off and off.get_text(strip=True):
        candidates.append(off.get_text(" ", strip=True))
    for sel in (
        "span.a-price span.a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#corePrice_feature_div span.a-offscreen",
    ):
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            candidates.append(el.get_text(" ", strip=True))
    for text in candidates:
        cleaned = text.replace(",", "")
        m = PRICE_RE.search(cleaned)
        if m:
            return float(m.group(1))
    return None


response = requests.get(PRODUCT_URL, headers=headers, timeout=30)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")
number = parse_price(soup)
if number is None:
    raise SystemExit("Could not parse a price from the Amazon page. Page layout may have changed.")

print(f"Current price: {number} {CURRENCY_HINT}")

if number <= BUY_PRICE:
    if not all([EMAIL, PASSWORD, EMAIL_2]):
        raise SystemExit("EMAIL, PASSWORD, and EMAIL_2 must be set in .env to send alerts.")
    body = (
        f"Price drop!\n{PRODUCT_URL}\n"
        f"Current price: {number} {CURRENCY_HINT} (target <= {BUY_PRICE})"
    )
    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = f"Amazon alert: at or below {BUY_PRICE} {CURRENCY_HINT}"
    msg["From"] = EMAIL
    msg["To"] = EMAIL_2
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=PASSWORD)
        connection.sendmail(from_addr=EMAIL, to_addrs=EMAIL_2, msg=msg.as_string())
    print("Alert email sent.")
else:
    print(f"Still above target ({BUY_PRICE} {CURRENCY_HINT}). No email sent.")
