"""Amazon Price Drop Email Notifier (Intermediate)

Template project: fetch a product page (or API), extract price, compare with threshold,
and send an email alert.

Important:
- Many sites (including Amazon) actively block scraping and may prohibit it by ToS.
- Prefer official APIs or allowed data sources.
- This file focuses on structure and safety, not bypassing protections.

"""

from __future__ import annotations

import csv
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class PricePoint:
    ts: str
    price_text: str


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PythonCentralHubBot/1.0)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text


def extract_price(html: str, selector: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one(selector)
    if not el:
        return None
    return el.get_text(" ", strip=True)


def append_history(csv_path: Path, price_text: str) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not csv_path.exists()

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["timestamp", "price_text"])
        w.writerow([datetime.now().isoformat(), price_text])


def send_email(to: str, subject: str, body: str) -> None:
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)


def main() -> None:
    url = "https://example.com/product"

    # Update this to a selector that matches your allowed data source.
    selector = ".price"

    html = fetch_html(url)
    price_text = extract_price(html, selector)

    if not price_text:
        raise SystemExit("Could not find price element. Update the CSS selector.")

    append_history(Path("price_history.csv"), price_text)

    # Replace with your own logic for parsing numeric price and threshold check.
    notify = True

    if notify:
        send_email(
            to="to@example.com",
            subject="Price update",
            body=f"Current price: {price_text}\nURL: {url}",
        )


if __name__ == "__main__":
    main()
