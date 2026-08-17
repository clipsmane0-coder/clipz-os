"""
eBay product search and price data via Parse.bot API.

eBay's official APIs are blocked from datacenter IPs, so we use
Parse.bot as a proxy service. The same API key works for both
Temu and eBay endpoints.

Endpoints:
- search_listings: active listings (10 credits/call)
- get_completed_sold_listings: sold/completed listings (5 credits/call)
- get_item_details: single item details (2 credits/call)
"""
import re
import urllib.parse
import requests
import os
from typing import Optional, List, Dict, Any

PARSE_BOT_API_KEY = os.environ.get("PARSE_BOT_API_KEY", "")
EBAY_API_BASE = "https://api.parse.bot/scraper/caa8e1ad-f5a8-41c1-9bd2-54a8e19b6c35"

DEFAULT_HEADERS = {
    "X-API-Key": PARSE_BOT_API_KEY,
    "Content-Type": "application/json",
}


def _parse_price(value) -> Optional[float]:
    """Extract price float from various formats ($29.99, '29.99', etc.)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("$", "").replace("USD", "").replace(",", "").strip()
    # Handle ranges like "$19.99 to $29.99"
    if "to" in text.lower():
        parts = re.split(r"\s+to\s+", text, flags=re.IGNORECASE)
        text = parts[0]  # use lower bound
    m = re.search(r"(\d+\.?\d*)", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def _normalize_listing(data: dict) -> Optional[Dict[str, Any]]:
    """Normalize a listing from Parse.bot into standard format."""
    title = (
        data.get("title")
        or data.get("item_title")
        or ""
    )

    price = (
        data.get("price")
        or data.get("current_price")
        or data.get("item_price")
    )

    item_id = (
        data.get("item_id")
        or data.get("id")
    )

    url = (
        data.get("url")
        or data.get("item_url")
        or data.get("ebay_item_url")
    )
    if not url and item_id:
        url = f"https://www.ebay.com/itm/{item_id}"

    condition = (
        data.get("condition")
        or ""
    )

    shipping = (
        data.get("shipping")
        or data.get("shipping_price")
        or data.get("shipping_price_ebay")
    )

    image = (
        data.get("image")
        or data.get("thumbnail")
        or data.get("img")
    )

    sold_date = data.get("date_sold") or data.get("sold_date")

    price_val = _parse_price(price)
    if not price_val:
        return None

    return {
        "item_id": str(item_id) if item_id else None,
        "title": title,
        "price": price_val,
        "condition": condition,
        "url": url or "",
        "image": image or "",
        "shipping": _parse_price(shipping),
        "sold_date": sold_date,
        "source": "ebay",
    }


def search_listings(
    query: str,
    max_results: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category_id: Optional[str] = None,
    sold: bool = False,
    sort: Optional[str] = None,
    timeout: int = 20,
) -> List[Dict[str, Any]]:
    """
    Search eBay listings via Parse.bot API.

    Args:
        query: search keywords
        max_results: number of results to return
        min_price: minimum price filter
        max_price: maximum price filter
        category_id: eBay category ID
        sold: if True, search sold/completed listings only
        sort: sort order (e.g. 'price_low_to_high')

    Returns:
        List of normalized listing dicts
    """
    if not PARSE_BOT_API_KEY:
        print("[ebay] PARSE_BOT_API_KEY not set, skipping Parse.bot search")
        return []

    if sold:
        endpoint = f"{EBAY_API_BASE}/get_completed_sold_listings"
    else:
        endpoint = f"{EBAY_API_BASE}/search_listings"

    params = {
        "query": query,
        "page": 1,
    }
    if category_id:
        params["category_id"] = category_id
    if sort:
        params["sort"] = sort

    # Price filters for search_listings
    if not sold:
        if min_price is not None:
            params["min_price"] = str(min_price)
        if max_price is not None:
            params["max_price"] = str(max_price)

    url = endpoint + "?" + urllib.parse.urlencode(params)

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ebay] Parse.bot search failed: {e}")
        return []

    # Navigate response structure
    listings = (
        data.get("listings")
        or data.get("data", {}).get("listings")
        or data.get("items")
        or data.get("data", {}).get("items")
        or []
    )

    results = []
    for item in listings:
        norm = _normalize_listing(item)
        if norm:
            # Apply price filters for sold listings (no server-side filter)
            if sold:
                if min_price is not None and norm["price"] < min_price:
                    continue
                if max_price is not None and norm["price"] > max_price:
                    continue
            results.append(norm)
            if len(results) >= max_results:
                break

    return results


def get_item_details(item_id: str, timeout: int = 20) -> Optional[Dict[str, Any]]:
    """
    Get detailed info for a single eBay listing via Parse.bot.
    2 credits per call.
    """
    if not PARSE_BOT_API_KEY:
        return None

    url = f"{EBAY_API_BASE}/get_item_details?item_id={item_id}"

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ebay] Parse.bot item detail failed: {e}")
        return None

    item = data.get("item", data) if isinstance(data, dict) else {}
    return _normalize_listing(item)


def get_median_price(
    query: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sold: bool = False,
    sample_size: int = 20,
) -> Optional[float]:
    """
    Get the median price for a query from eBay listings.
    Returns None if no valid prices found.
    """
    listings = search_listings(
        query=query,
        max_results=sample_size,
        min_price=min_price,
        max_price=max_price,
        sold=sold,
    )

    prices = [l["price"] for l in listings if l.get("price")]
    if not prices:
        return None

    prices.sort()
    return prices[len(prices) // 2]


def get_price_range(
    query: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sold: bool = False,
    sample_size: int = 20,
) -> Dict[str, Optional[float]]:
    """Get min, median, max price for a query."""
    listings = search_listings(
        query=query,
        max_results=sample_size,
        min_price=min_price,
        max_price=max_price,
        sold=sold,
    )

    prices = [l["price"] for l in listings if l.get("price")]
    if not prices:
        return {"min": None, "median": None, "max": None, "sample_size": 0}

    prices.sort()
    return {
        "min": prices[0],
        "median": prices[len(prices) // 2],
        "max": prices[-1],
        "sample_size": len(prices),
    }


def get_market_metrics(
    query: str,
    sample_size: int = 30,
) -> Dict[str, Any]:
    """
    Get market metrics: active price range, sold price range, volume estimate.
    Uses 2 API calls (active + sold).
    """
    active = search_listings(query, max_results=sample_size)
    sold = search_listings(query, max_results=sample_size, sold=True)

    active_prices = [l["price"] for l in active if l.get("price")]
    sold_prices = [l["price"] for l in sold if l.get("price")]

    active_prices.sort() if active_prices else None
    sold_prices.sort() if sold_prices else None

    return {
        "query": query,
        "active_count": len(active_prices),
        "active_min": active_prices[0] if active_prices else None,
        "active_median": active_prices[len(active_prices) // 2] if active_prices else None,
        "active_max": active_prices[-1] if active_prices else None,
        "sold_count": len(sold_prices),
        "sold_min": sold_prices[0] if sold_prices else None,
        "sold_median": sold_prices[len(sold_prices) // 2] if sold_prices else None,
        "sold_max": sold_prices[-1] if sold_prices else None,
    }


def is_available() -> bool:
    """Check if eBay data source is configured."""
    return bool(PARSE_BOT_API_KEY)
