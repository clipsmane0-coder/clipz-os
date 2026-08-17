"""
Temu product search and price scraper.

Sources (in order of preference):
1. Parse.bot Temu API (third-party, 200 free calls/month)
2. Manual URL input with detail page scraping
3. Direct Temu HTML page parsing (often blocked by Cloudflare)

Note: Temu prices frequently exclude shipping and vary by promotion/coupon.
Prices returned are the displayed list price and should be treated as estimates.
"""
import re
import json
import urllib.parse
import requests
import os
from typing import Optional, List, Dict, Any

PARSE_BOT_API_BASE = "https://api.parse.bot/scraper/19417d13-c955-4a31-bfb8-d40635cf048d"
PARSE_BOT_API_KEY = os.environ.get("PARSE_BOT_API_KEY", "")

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

TEMU_BASE = "https://www.temu.com"


def _parse_price(value) -> Optional[float]:
    """Extract price float from various formats."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("$", "").replace("USD", "").replace(",", "").strip()
    m = re.search(r"(\d+\.?\d*)", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def _extract_pack_size(title: str) -> int:
    """
    Try to determine pack size / unit count from product title.
    Returns estimated number of units, defaults to 1.
    """
    if not title:
        return 1
    title_lower = title.lower()
    patterns = [
        r"pack of (\d+)",
        r"(\d+)\s*-?\s*pack",
        r"(\d+)\s*pcs?\b",
        r"(\d+)\s*pieces?\b",
        r"(\d+)\s*count",
        r"(\d+)\s*ct\b",
        r"set of (\d+)",
        r"(\d+)\s*pair",
        r"(\d+)\s*sets?",
        r"(\d+)\s*packs?",
    ]
    for pattern in patterns:
        m = re.search(pattern, title_lower)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                pass
    return 1


def _normalize_product(data: dict, source: str = "temu") -> Optional[Dict[str, Any]]:
    """Normalize product data from various sources into standard format."""
    title = (
        data.get("title")
        or data.get("goods_name")
        or data.get("goodsName")
        or data.get("name")
    )

    price = (
        data.get("price")
        or data.get("sale_price")
        or data.get("goods_price")
        or data.get("current_price")
        or data.get("min_price")
        or data.get("minPrice")
    )

    original_price = (
        data.get("market_price")
        or data.get("marketPrice")
        or data.get("original_price")
        or data.get("list_price")
        or data.get("retailPrice")
    )

    product_id = (
        data.get("product_id")
        or data.get("goods_id")
        or data.get("goodsId")
        or data.get("id")
    )

    image = (
        data.get("thumbnail")
        or data.get("image")
        or data.get("thumb")
        or data.get("img")
    )

    sales = (
        data.get("sold_count")
        or data.get("sales_count")
        or data.get("sales")
        or data.get("sold")
    )

    url = data.get("url") or data.get("product_url")
    if not url and product_id:
        url = f"{TEMU_BASE}/goods.html?goods_id={product_id}"

    price_val = _parse_price(price)
    original_price_val = _parse_price(original_price)

    if not price_val:
        return None

    return {
        "id": str(product_id) if product_id else None,
        "title": title or "",
        "price": price_val,
        "original_price": original_price_val,
        "url": url or "",
        "image": image or "",
        "sales_count": sales,
        "pack_size_est": _extract_pack_size(title or ""),
        "source": source,
    }


def search_products_parsebot(
    query: str,
    max_results: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    locale: str = "en",
    timeout: int = 20,
) -> List[Dict[str, Any]]:
    """
    Search Temu via Parse.bot API.
    Requires PARSE_BOT_API_KEY environment variable.
    Free tier: 200 calls/month.
    """
    if not PARSE_BOT_API_KEY:
        print("[temu] PARSE_BOT_API_KEY not set, skipping Parse.bot search")
        return []

    url = f"{PARSE_BOT_API_BASE}/search_products"
    headers = {
        "X-API-Key": PARSE_BOT_API_KEY,
        "Content-Type": "application/json",
    }
    body = {
        "query": query,
        "limit": max_results,
        "locale": locale,
    }
    if min_price is not None:
        body["price_min"] = min_price
    if max_price is not None:
        body["price_max"] = max_price

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[temu] Parse.bot search failed: {e}")
        return []

    products = data.get("products", []) or data.get("data", {}).get("products", []) or []
    results = []
    for p in products:
        norm = _normalize_product(p, source="temu")
        if norm:
            results.append(norm)

    return results[:max_results]


def get_product_detail_parsebot(
    product_id: str,
    locale: str = "en",
    timeout: int = 20,
) -> Optional[Dict[str, Any]]:
    """
    Get detailed product info via Parse.bot API.
    1 credit per call.
    """
    if not PARSE_BOT_API_KEY:
        return None

    url = f"{PARSE_BOT_API_BASE}/get_product_details"
    headers = {
        "X-API-Key": PARSE_BOT_API_KEY,
        "Content-Type": "application/json",
    }
    body = {"product_id": product_id, "locale": locale}

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[temu] Parse.bot detail failed: {e}")
        return None

    product = data.get("product", {}) or data
    return _normalize_product(product, source="temu")


def search_products(
    query: str,
    max_results: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    timeout: int = 20,
) -> List[Dict[str, Any]]:
    """
    Search Temu for products matching a query.
    Tries Parse.bot first, then falls back to direct scraping (often blocked).
    Returns list of {id, title, price, original_price, url, image, sales_count, pack_size_est}.
    """
    # Try Parse.bot API
    results = search_products_parsebot(
        query, max_results=max_results,
        min_price=min_price, max_price=max_price,
        timeout=timeout,
    )
    if results:
        return results

    # Fallback: direct HTML scraping (often blocked by Cloudflare)
    try:
        results = _search_html(query, max_results, timeout)
        if results:
            return results
    except Exception as e:
        print(f"[temu] HTML search failed: {e}")

    return []


def _search_html(query: str, max_results: int, timeout: int) -> List[Dict[str, Any]]:
    """Fallback: try to scrape Temu HTML search page."""
    search_url = TEMU_BASE + "/search_result.html?" + urllib.parse.urlencode({
        "search_key": query,
    })
    try:
        resp = requests.get(search_url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"[temu] HTML search request failed: {e}")
        return []

    html = resp.text
    results = []

    # Try to find embedded JSON data
    patterns = [
        r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;',
        r'<script id="__NEXT_DATA__"[^>]*>(\{.*?\})</script>',
    ]

    for pattern in patterns:
        m = re.search(pattern, html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                # Navigate the nested data structure to find product list
                results = _extract_from_nested(data, max_results)
                if results:
                    break
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    return results[:max_results]


def _extract_from_nested(data: dict, max_results: int) -> List[Dict[str, Any]]:
    """Try to extract products from nested JSON structures."""
    results = []

    def _search_dict(d):
        if isinstance(d, dict):
            for key in ["goodsList", "goods_list", "products", "items", "searchResult"]:
                if key in d and isinstance(d[key], list):
                    for item in d[key]:
                        norm = _normalize_product(item)
                        if norm:
                            results.append(norm)
                            if len(results) >= max_results:
                                return True
            for v in d.values():
                if _search_dict(v):
                    return True
        elif isinstance(d, list):
            for item in d:
                if _search_dict(item):
                    return True
        return False

    _search_dict(data)
    return results


def get_product_detail(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    """
    Get product detail from a Temu URL.
    Tries Parse.bot if we have a product_id, else tries direct scraping.
    """
    # Try to extract product ID from URL
    m = re.search(r"goods_id=(\d+)", url)
    product_id = m.group(1) if m else None

    if product_id and PARSE_BOT_API_KEY:
        detail = get_product_detail_parsebot(product_id)
        if detail:
            return detail

    # Fallback: try direct page scraping
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"[temu] detail page failed: {e}")
        return None

    html = resp.text

    # Try embedded JSON data
    patterns = [
        r'window\.goodsInfo\s*=\s*(\{.*?\});',
        r'"goodsInfo":(\{.*?\}),',
    ]
    for pattern in patterns:
        m = re.search(pattern, html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                product = _normalize_product(data)
                if product:
                    return product
            except (json.JSONDecodeError, KeyError):
                continue

    return None


def find_multipack_products(
    keywords: str,
    target_pack_size: int = 4,
    max_results: int = 5,
    timeout: int = 20,
) -> List[Dict[str, Any]]:
    """
    Search Temu for multi-pack products matching keywords.
    Returns products sorted by estimated pack size match.
    """
    query = f"{keywords} {target_pack_size} pack"
    results = search_products(query, max_results=max_results * 3, timeout=timeout)

    if not results:
        # Try broader search
        results = search_products(keywords, max_results=max_results * 5, timeout=timeout)

    # Score by pack size match
    scored = []
    for r in results:
        ps = r.get("pack_size_est", 1)
        score = abs(ps - target_pack_size)
        scored.append((score, r))

    scored.sort(key=lambda x: x[0])
    return [item[1] for item in scored[:max_results]]


def get_source_availability() -> dict:
    """Report which Temu data sources are available."""
    return {
        "parsebot_available": bool(PARSE_BOT_API_KEY),
        "parsebot_free_tier": "200 calls/month",
        "direct_scraping": "unreliable (Cloudflare-protected)",
        "manual_entry_fallback": True,
    }
