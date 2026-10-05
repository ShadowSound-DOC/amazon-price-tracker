# Amazon Price Tracker

Scrapes an Amazon product page and sends a Gmail SMTP alert when the price is at or below your target.

## Setup

1. Copy `.env.example` to `.env` and fill in:
   - `EMAIL` / `PASSWORD` — Gmail address and app password
   - `EMAIL_2` — alert recipient
   - `PRODUCT_URL` — Amazon product URL
   - `BUY_PRICE` — numeric target price
2. Install deps (preferably in the project `.venv`):
   ```
   pip install requests beautifulsoup4 python-dotenv
   ```

## Run

```
python main.py
```

Amazon HTML changes often; if parsing fails, update the selectors in `parse_price()`.
