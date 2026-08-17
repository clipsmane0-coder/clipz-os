"""
Amazon product price scraper — direct HTTP + HTML parsing.
No official API needed. Uses custom User-Agent and basic
request spoofing to get product search results and detail pages.
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
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

AMAZON_BASE = "https://www.amazon.com"
SEARCH_URL = AMAZON_BASE + "/s?k={query}&ref=nb_sb_noss"


def _parse_price(text: str) -> Optional[float]:
    """Extract a price float from text like '$19.99', '19,99 $', etc."""
    if not text:
        return None
    # Remove currency symbols and commas
    cleaned = text.replace("$", "").replace("USD", "").replace(",", "").strip()
    # Extract first float-like number
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
    Search Amazon for products matching a query.
    Returns list of {title, price, url, rating, reviews}.
    """
    url = SEARCH_URL.format(query=urllib.parse.quote(query))
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"[amazon] search failed for '{query}': {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # Amazon search results have data-component-type="s-search-result"
    cards = soup.select('div[data-component-type="s-search-result"]')

    for card in cards[:max_results * 2]:
        # Title
        title_el = card.select_one("h2 a span, h2 a")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title:
            continue

        # URL
        link_el = card.select_one("h2 a") or card.select_one("a.a-link-normal")
        href = link_el.get("href", "") if link_el else ""
        if href.startswith("/"):
            product_url = AMAZON_BASE + href.split("?")[0]
        else:
            product_url = href

        # Price — look for a-price / a-offscreen / price
        price = None
        # First try: whole price + fraction
        whole = card.select_one(".a-price .a-price-whole")
        fraction = card.select_one(".a-price .a-price-fraction")
        if whole and fraction:
            whole_text = whole.get_text(strip=True).replace(",", "")
            frac_text = fraction.get_text(strip=True)
            try:
                price = float(f"{whole_text}.{frac_text}")
            except ValueError:
                price = None
        if price is None:
            offscreen = card.select_one(".a-price .a-offscreen")
            if offscreen:
                price = _parse_price(offscreen.get_text())
        if price is None:
            # Fallback: any a-price
            any_price = card.select_one(".a-price")
            if any_price:
                price = _parse_price(any_price.get_text())

        if price is None or price <= 0:
            continue

        # Rating
        rating = None
        rating_el = card.select_one(".a-icon-alt")
        if rating_el:
            rating_text = rating_el.get_text(strip=True)
            m = re.search(r"([\d.]+)", rating_text)
            if m:
                try:
                    rating = float(m.group(1))
                except ValueError:
                    pass

        # Reviews
        reviews = None
        reviews_el = card.select_one(".a-size-base.s-underline-text")
        if not reviews_el:
            reviews_el = card.select_one('span[aria-label*="ratings"]')
        if reviews_el:
            rev_text = reviews_el.get("aria-label") or reviews_el.get_text()
            rev_clean = rev_text.replace(",", "").replace(".", "")
            m = re.search(r"(\d+)", rev_clean)
            if m:
                reviews = int(m.group(1))

        results.append({
            "title": title,
            "price": price,
            "url": product_url,
            "rating": rating,
            "reviews": reviews,
        })

        if len(results) >= max_results:
            break

    return results


def get_product_price(url: str, timeout: int = 15) -> Optional[float]:
    """
    Get the current price from an Amazon product detail page.
    Returns the price as float, or None on failure.
    """
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"[amazon] detail page failed: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try multiple price selectors
    price_selectors = [
        ".a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#priceblock_saleprice",
        ".a-price-whole",
        "#corePriceDisplay_desktop_feature_div .a-price-whole",
    ]

    for sel in price_selectors:
        el = soup.select_one(sel)
        if el:
            if "a-price-whole" in sel:
                # Need whole + fraction
                whole = el.get_text(strip=True).replace(",", "")
                frac_el = soup.select_one(sel.replace("whole", "fraction"))
                frac = frac_el.get_text(strip=True) if frac_el else "00"
                try:
                    return float(f"{whole}.{frac}")
                except ValueError:
                    continue
            price = _parse_price(el.get_text())
            if price:
                return price

    return None


def find_best_multipack_price(
    product_name: str,
    target_count: int,
    timeout: int = 15,
) -> dict:
    """
    Search Amazon for a product and try to find the best multipack price
    for the given target pack size.
    Returns {price, url, title, pack_size_found, price_per_unit}
    """
    # Try direct search with pack size
    queries = [
        f"{product_name} {target_count} count",
        f"{product_name} pack of {target_count}",
        f"{product_name} bulk",
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

            # Try to figure out pack size from title
            pack_size = 1
            # Look for patterns like "Pack of 6", "6 Pack", "6 Count", "216 ct"
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

            if pack_size <= 1 and target_count == 1:
                ppu = price
            else:
                ppu = price / max(pack_size, 1)

            if ppu < best_ppu:
                best_ppu = ppu
                best_result = {
                    "price": price,
                    "url": r["url"],
                    "title": r["title"],
                    "pack_size": pack_size,
                    "price_per_unit": ppu,
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
        "query_used": None,
    }
