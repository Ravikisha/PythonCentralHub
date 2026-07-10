"""Web-to-Excel Data Scraper (Intermediate)

Fetch a web page, extract a simple table-like dataset, and write it to an Excel file.

This is intentionally a "template" project:
- you adjust SELECTOR to match a real page you have permission to scrape.

SAFETY / ETHICS:
- Respect robots.txt and terms.
- Prefer public APIs.
- Use rate limits.

Requirements:
- requests
- beautifulsoup4
- openpyxl

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook


@dataclass
class Row:
    cols: list[str]


def fetch_html(url: str, timeout: int = 15) -> str:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text


def parse_rows(html: str, selector: str) -> list[Row]:
    soup = BeautifulSoup(html, "html.parser")

    rows: list[Row] = []
    for el in soup.select(selector):
        text = " ".join(el.get_text(" ", strip=True).split())
        if text:
            rows.append(Row(cols=[text]))

    return rows


def write_excel(rows: Iterable[Row], out_path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    ws.append(["Value"])
    for r in rows:
        ws.append(r.cols)

    wb.save(out_path)


def main() -> None:
    url = "https://example.com"

    # Change this selector to match the page you scrape.
    # Example selectors: "h2", ".price", "table tr", "ul.items li"
    selector = "h1"

    html = fetch_html(url)
    rows = parse_rows(html, selector=selector)
    write_excel(rows, out_path="scraped.xlsx")

    print(f"Wrote {len(rows)} rows to scraped.xlsx")


if __name__ == "__main__":
    main()
