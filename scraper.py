# scraper.py
from __future__ import annotations
import json
import html as ihtml
from dataclasses import dataclass
from typing import Optional
import requests
from bs4 import BeautifulSoup


@dataclass
class ScrapeResult:
    status: str
    total: Optional[int] = None
    biddable: Optional[int] = None
    reason: str = ""


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


session = requests.Session()
session.headers.update(HEADERS)


def check_ticket(url: str) -> ScrapeResult:
    try:
        r = session.get(url, timeout=15)
    except requests.RequestException as e:
        return ScrapeResult("UNKNOWN", reason=str(e))

    if r.status_code in (403, 429):
        return ScrapeResult("UNKNOWN", reason=f"blocked_status_{r.status_code}")

    if r.status_code != 200:
        return ScrapeResult("UNKNOWN", reason=f"http_{r.status_code}")

    soup = BeautifulSoup(r.text, "html.parser")
    app = soup.find(id="app")

    if not app:
        return ScrapeResult("UNKNOWN", reason="missing_app")

    raw = app.get("data-page")
    if not raw:
        return ScrapeResult("UNKNOWN", reason="missing_data_page")

    try:
        payload = json.loads(ihtml.unescape(raw))
    except Exception as e:
        return ScrapeResult("UNKNOWN", reason=f"json_parse_error_{e}")

    listings = (
        payload.get("props", {})
        .get("listings", {})
        .get("data", [])
    )

    total = len(listings)
    biddable_count = sum(
        1 for item in listings if item.get("is_biddable") is True
    )

    if biddable_count > 0:
        return ScrapeResult("AVAILABLE", total, biddable_count)

    return ScrapeResult("SOLD_OUT", total, 0)