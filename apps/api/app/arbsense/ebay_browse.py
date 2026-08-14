"""
eBay Browse API Client (marketplace search)
Uses Auth'n'Auth token as Bearer token (unexpected but works)
- item_summary/search: keyword search with prices, seller info, shipping
- item/{item_id}: full item details
"""
import httpx
import os
from typing import Optional, List, Dict, Any

EBAY_AUTH_TOKEN = os.getenv(
    "EBAY_BROWSE_TOKEN",
    "v^1.1#i^1#r^0#p^1#f^0#I^3#t^H4sIAAAAAAAA/+VYa2wUVRTu9oE0pSgIFhto1uEVwZm9s7PdnQ7djVvawmLfu1SoYpnHnXbo7Mwwc7fbqiG1SonRAAEUEkHxB0ZFiEYSjCJoEQUl2sSoqFETJdEIIeAjCFjxzvbBthJAusQm7p/NPefcc8/5zuvOBR1jsud0Lew6m+u4KX17B+hIdzjoHJA9Jmvu+Iz0/Kw0kCTg2N4xoyOzM+OnYouPqgZXBy1D1yzobIuqmsUliH4iZmqczluKxWl8FFocErlwsLKCc1OAM0wd6aKuEs5QqZ/wAg/jEbw+VmBZWeYBpmoDOiO6nxCAzRaKeNbn80EaYr5lxWBIsxCvIT/hBm4vCViS9kQAzXkYjqEpt5tuIJz10LQUXcMiFCACCXO5xF4zydYrm8pbFjQRVkIEQsHycHUwVFpWFSl2JekK9OMQRjyKWUNX83UJOut5NQavfIyVkObCMVGElkW4An0nDFXKBQeMuQ7zE1AXSlAC3kK3DGQZ+Bg+JVCW62aUR1e2w6YoEiknRDmoIQW1Xw1RjIawAoqof1WFVYRKnfZfbYxXFVmBpp8oKwkuDdbUEIGyivpQVXB+LRk0hTDEqUPW1JWShTJbSHsBQ5O0jwYsX8j0H9SnrR/mYSfN1zVJsUGznFU6KoHYajgcGyYJGyxUrVWbQRnZFiXLMQMYAm+DHdS+KMZQs2bHFUYxEM7E8uoRGNyNkKkIMQQHNQxnJCDyE7xhKBIxnJnIxf70abP8RDNCBudyxeNxKs5QutnkcgNAu5ZUVoTFZhjFGdIWtWu9T165+gZSSbgi4jLF8hxqN7AtbThXsQFaExHw0gygB6Iw1KzAcOo/CEk+u4ZWRKoqRPAxjE+mRbdb4mk3K6eiQgL9Seqy7YAC305GebMFIkPlRUiKOM9iUWgqEscUym6GlSEpeYtk0lMky6RQKHlJWoYQQCgIYhH7fyqUa031MBRNiFKS6ynL89rWlSuD996zKNREWwuXSFqtvqBcKI8LkgvKlWUL6hrcqNW3JK4JRqX/Wqvhss7PVxWMTASfnwoA7FpPHQgLdQtBaUTuhUXdgDW6qojtoyvAjCnV8CZqD0NVxYQRORk0jFBqenXK3PuXbeL6/E7djPqP5tNlvbLslB1dXtn7LayANxTKnkCUqEdddq3rPL5+2OTGhNXOywoOE3JhGh5YIqTwXJIEXmyhTMhLuqa2jwg3Bd98RxVq2M8+EBSp78pKJZCgrFYRe2zpMYyBRVXbN7iI3gI1PA+RqasqNOvpEfeDaDSGeEGFo60xpKBAFH6UDWvax3q9PpqlRxY2MTGKG0dbS7NbeWang7/h7bwO8mp0dPlumLoUE+076g345HANfQAJpCV+dKejG3Q69qc7HKAYzKSngzvGZCzOzBiXbykIUgovU5bSpOHvehNSLbDd4BUz/da0Dz/7sqrgrUUvPn48r2P1DNeGtPFJ7y/bl4Epgy8w2Rl0TtJzDJh6iZNF35yX6/YClvYA2sMwdAOYfombSd+WOWnRw+9u29mdm77v3F0XPtmy3/P8mhdWgdxBIYcjKw0nS1rr6egvH7+8/ret30zrXCzUv3/i4Os/P0u+Nlbp2hTuKI5PiuwV/KI6adyDz5364/RFz8nlR/dufqOnYtPSXT1zXrr9h5qLy8duPPbV6a2H37m7aNvnUnNJ/v271jRXr51A9DwQObTglradc39nD8/afaSlseCVgi+mLZ31KdMoP9E1uWDy0YfWVX6fc6e/5IjzA2lL98kZvWdX9Dy2776pc99cNbvsxwmd7LHx+eTbW/M2ThQir64+M+9befLNOdWnHomdf3Ti+e4n030ZW+ovHtrTe+LgzJ0rdhxYO+/47Kc+ytuwz3tuSumZX5/+a+Z3cMfu9ZtL0DO1s9Zd6EUX1sZrPSvb5i0r2XPgvT+/NrN7N/v7Yvk37hC6vBkTAAA="
)

BROWSE_API_BASE = "https://api.ebay.com/buy/browse/v1"
DEFAULT_LIMIT = 50


async def search_items(
    keyword: str,
    limit: int = 20,
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: str = "-price",  # -price = highest first, price = lowest first
    buying_options: str = "FIXED_PRICE",
) -> List[Dict[str, Any]]:
    """Search eBay listings via Browse API item_summary/search."""
    url = f"{BROWSE_API_BASE}/item_summary/search"
    headers = {
        "Authorization": f"Bearer {EBAY_AUTH_TOKEN}",
        "Content-Type": "application/json",
    }
    params: Dict[str, Any] = {
        "q": keyword,
        "limit": str(limit),
        "sort": sort,
    }
    if category_id:
        params["category_ids"] = category_id
    if buying_options:
        params["filter"] = f"buyingOptions:{{{buying_options}}}"
    
    price_filters = []
    if min_price is not None:
        price_filters.append(f"price:[{min_price}..]")
    if max_price is not None:
        price_filters.append(f"price:[..{max_price}]")
    
    if price_filters:
        existing_filter = params.get("filter", "")
        pf = ",".join(price_filters)
        params["filter"] = f"{existing_filter},{pf}" if existing_filter else pf

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=headers, params=params)
        if r.status_code != 200:
            raise Exception(f"eBay Browse search failed: {r.status_code} {r.text[:200]}")
        data = r.json()
        return data.get("itemSummaries", [])


async def get_item(item_id: str) -> Dict[str, Any]:
    """Get full item details from Browse API."""
    url = f"{BROWSE_API_BASE}/item/{item_id}"
    headers = {
        "Authorization": f"Bearer {EBAY_AUTH_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception(f"eBay Browse get_item failed: {r.status_code} {r.text[:200]}")
        return r.json()


def extract_listing_price(item_summary: Dict) -> float:
    """Extract price from an item summary dict."""
    try:
        return float(item_summary.get("price", {}).get("value", 0))
    except (ValueError, TypeError):
        return 0.0


def extract_shipping(item_summary: Dict) -> float:
    """Extract shipping cost from an item summary."""
    try:
        shipping_options = item_summary.get("shippingOptions", [])
        if shipping_options:
            cost = shipping_options[0].get("shippingCost", {}).get("value", "0")
            return float(cost)
    except (ValueError, TypeError, IndexError):
        pass
    return 0.0


def get_lowest_price(items: List[Dict]) -> float:
    """Get the lowest fixed price from a list of item summaries."""
    prices = [extract_listing_price(i) for i in items if extract_listing_price(i) > 0]
    return min(prices) if prices else 0.0


def get_median_price(items: List[Dict]) -> float:
    """Get the median price from a list of item summaries."""
    prices = sorted([extract_listing_price(i) for i in items if extract_listing_price(i) > 0])
    if not prices:
        return 0.0
    n = len(prices)
    if n % 2 == 0:
        return (prices[n//2 - 1] + prices[n//2]) / 2
    return prices[n//2]
