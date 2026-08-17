"""
Walmart product search and price scraper.
Much less aggressive bot detection than Amazon.
"""
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Optional

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

WALMART_BASE = "https://www.walmart.com"
SEARCH_URL = WALMART_BASE + "/search?q={query}"


def _parse_price(text: str) -> Optional[float]:
    if not text:
        return None
    cleaned = text.replace("$", "").replace(",", "").strip()
    m = re.search(r"(\d+\.\d{2})", cleaned)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    m = re.search(r"(\d+)", cleaned)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def search_products(query: str, max_results: int = 5, timeout: int = 15) -> list[dict]:
    """
    Search Walmart.com for products.
    Returns list of {title, price, url, rating}.
    """
    url = SEARCH_URL.format(query=urllib.parse.quote(query))
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"[walmart] search failed for '{query}': {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # Walmart uses data-item-id on product cards
    cards = soup.select('[data-item-id]')
    if not cards:
        # Try alternative selectors
        cards = soup.select('.flex.flex-col.pb-0.relative')

    for card in cards[:max_results * 3]:
        # Title
        title_el = card.select_one('span[data-automation-id="product-title"], .sans-serif.mid-gray, h3 a')
        if not title_el:
            # Try link text
            title_el = card.select_one('a')
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title or len(title) < 10:
            continue

        # URL
        link_el = card.select_one('a[href*="/ip/"]') or card.select_one('a')
        href = link_el.get("href", "") if link_el else ""
        if href.startswith("/"):
            product_url = WALMART_BASE + href.split("?")[0]
        elif href.startswith("http"):
            product_url = href
        else:
            continue

        # Price
        price = None
        price_el = card.select_one('[data-automation-id="product-price"], .f6.f5-l.dark-gray')
        if price_el:
            price = _parse_price(price_el.get_text())
        if price is None:
            price_el = card.select_one(".w_iUH7, .b.black, [itemprop='price']")
            if price_el:
                price = _parse_price(price_el.get_text())
        if price is None or price <= 0 or price > 9999:
            continue

        results.append({
            "title": title,
            "price": price,
            "url": product_url,
            "rating": None,
            "reviews": None,
        })

        if len(results) >= max_results:
            break

    return results


def find_best_multipack_price(
    product_name: str,
    target_count: int,
    timeout: int = 15,
) -> dict:
    """
    Search Walmart for best multipack price.
    """
    queries = [
        f"{product_name} {target_count} count",
        f"{product_name} pack of {target_count}",
        f"{product_name} {target_count} pack",
        f"{product_name} multipack",
        product_name,
    ]

    best_result = None
    best_ppu = float("inf")

    for query in queries:
        results = search_products(query, max_results=5, timeout=timeout)
        for r in results:
            title_lower = r["title"].lower()
            price = r["price"]
            if not price:
                continue

            # Detect pack size from title
            pack_size = 1
            for pattern in [
                r"pack of (\d+)",
                r"(\d+)\s*-?\s*pack",
                r"(\d+)\s*count",
                r"(\d+)\s*ct",
                r"(\d+)\s*pieces?",
                r"(\d+)\s*packs?",
            ]:
                m = re.search(pattern, title_lower)
                if m:
                    pack_size = int(m.group(1))
                    break

            if pack_size <= 1:
                pack_size = 1

            ppu = price / pack_size

            if ppu < best_ppu:
                best_ppu = ppu
                best_result = {
                    "price": price,
                    "url": r["url"],
                    "title": r["title"],
                    "pack_size": pack_size,
                    "price_per_unit": ppu,
                    "source": "walmart",
                    "query_used": query,
                }

    if best_result:
        return best_result

    return {
        "price": None,
        "url": None,
        "title": None,
        "pack_size": 0,
        "price_per_unit": None,
        "source": "walmart",
        "query_used": None,
    }
