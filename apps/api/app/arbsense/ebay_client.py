"""
eBay API client for ArbSense
Uses eBay Finding API (App ID auth) for search + sold listing data
"""
import httpx
from typing import Optional, List, Dict, Any

EBAY_FINDING_API_URL = "https://svcs.ebay.com/services/search/FindingService/v1"
EBAY_APP_ID = "ELVINACQ-ArbSens-PRD-5f8516031-l7108a53"
EBAY_GLOBAL_ID = "EBAY_US"

# Categories with strong multipack potential
HIGH_POTENTIAL_CATEGORIES = {
    "vitamins_supplements": "184634",
    "skin_care": "1085632",
    "hair_care": "1085666",
    "air_filters": "144972",
    "light_bulbs": "20695",
    "batteries": "98082",
    "printer_ink": "163542",
    "coffee_pods": "184423",
    "baby_diapers": "169329",
    "cleaning_supplies": "176866",
}


class EbaySearchItem:
    def __init__(self, data: dict):
        self.item_id = data.get("itemId", [None])[0]
        self.title = data.get("title", [""])[0]
        price_info = data.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0]
        self.price = float(price_info.get("__value__", 0))
        self.currency = price_info.get("@currencyId", "USD")
        self.condition = data.get("condition", [{}])[0].get("conditionDisplayName", ["Unknown"])[0]
        self.listing_type = data.get("listingInfo", [{}])[0].get("listingType", ["Unknown"])[0]
        self.gallery_url = data.get("galleryURL", [""])[0]
        self.view_item_url = data.get("viewItemURL", [""])[0]
        self.selling_state = data.get("sellingStatus", [{}])[0].get("sellingState", [""])[0]
        self.start_time = data.get("listingInfo", [{}])[0].get("startTime", [None])[0]
        self.end_time = data.get("listingInfo", [{}])[0].get("endTime", [None])[0]
        self.seller = data.get("sellerInfo", [{}])[0].get("sellerUserName", [""])[0]

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "price": self.price,
            "currency": self.currency,
            "condition": self.condition,
            "listing_type": self.listing_type,
            "gallery_url": self.gallery_url,
            "view_item_url": self.view_item_url,
            "selling_state": self.selling_state,
            "end_time": self.end_time,
            "seller": self.seller,
        }


async def ebay_search(
    keywords: str,
    category_id: Optional[str] = None,
    condition: Optional[str] = None,
    sold_only: bool = False,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    entries_per_page: int = 50,
    sort_order: str = "BestMatch",
) -> dict:
    """Search eBay using the Finding API."""
    params = {
        "OPERATION-NAME": "findItemsAdvanced",
        "SERVICE-VERSION": "1.13.0",
        "SECURITY-APPNAME": EBAY_APP_ID,
        "GLOBAL-ID": EBAY_GLOBAL_ID,
        "keywords": keywords,
        "RESPONSE-DATA-FORMAT": "JSON",
        "paginationInput.entriesPerPage": str(entries_per_page),
        "sortOrder": sort_order,
        "outputSelector(0)": "SellerInfo",
        "outputSelector(1)": "PictureURLSuperSize",
        "outputSelector(2)": "ConditionDisplayName",
    }

    if category_id:
        params["categoryId(0)"] = category_id

    filter_idx = 0

    if condition:
        params[f"itemFilter({filter_idx}).name"] = "Condition"
        params[f"itemFilter({filter_idx}).value(0)"] = condition
        filter_idx += 1

    if sold_only:
        params[f"itemFilter({filter_idx}).name"] = "SoldItemsOnly"
        params[f"itemFilter({filter_idx}).value(0)"] = "true"
        filter_idx += 1

    if min_price is not None:
        params[f"itemFilter({filter_idx}).name"] = "MinPrice"
        params[f"itemFilter({filter_idx}).value(0)"] = str(min_price)
        params[f"itemFilter({filter_idx}).param(0).name"] = "Currency"
        params[f"itemFilter({filter_idx}).param(0).value"] = "USD"
        filter_idx += 1

    if max_price is not None:
        params[f"itemFilter({filter_idx}).name"] = "MaxPrice"
        params[f"itemFilter({filter_idx}).value(0)"] = str(max_price)
        params[f"itemFilter({filter_idx}).param(0).name"] = "Currency"
        params[f"itemFilter({filter_idx}).param(0).value"] = "USD"
        filter_idx += 1

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            EBAY_FINDING_API_URL,
            params=params,
            headers={
                "User-Agent": "ArbSense/1.0 (Fly.io server)",
                "Accept": "application/json",
            },
        )

    if response.status_code != 200:
        raise Exception(f"eBay API error: {response.status_code} - {response.text[:200]}")

    data = response.json()
    items: List[EbaySearchItem] = []

    search_result = (
        data.get("findItemsAdvancedResponse", [{}])[0]
        .get("searchResult", [{}])[0]
    )

    if search_result.get("item"):
        items = [EbaySearchItem(item) for item in search_result["item"]]

    pagination = (
        data.get("findItemsAdvancedResponse", [{}])[0]
        .get("paginationOutput", [{}])[0]
    )
    total = int(pagination.get("totalEntries", [0])[0])

    # Estimate velocity
    sold_items = [i for i in items if i.selling_state == "EndedWithSales"]
    velocity = estimate_velocity(sold_items)

    return {
        "success": True,
        "keywords": keywords,
        "total": total,
        "count": len(items),
        "velocity": velocity,
        "items": [i.to_dict() for i in items],
    }


def estimate_velocity(sold_items: List[EbaySearchItem]) -> dict:
    """Estimate monthly sales velocity from sold listing dates."""
    if not sold_items:
        return {
            "estimated_monthly_sales": 0,
            "confidence": "low",
            "sold_items_count": 0,
        }

    end_dates = [
        i.end_time for i in sold_items
        if i.end_time
    ]

    if len(end_dates) < 3:
        return {
            "estimated_monthly_sales": len(sold_items),
            "confidence": "low",
            "sold_items_count": len(sold_items),
        }

    from datetime import datetime, timezone
    dates = []
    for d in end_dates:
        try:
            dates.append(datetime.fromisoformat(d.replace("Z", "+00:00")))
        except Exception:
            pass

    if len(dates) < 3:
        return {
            "estimated_monthly_sales": len(sold_items),
            "confidence": "low",
            "sold_items_count": len(sold_items),
        }

    newest = max(dates)
    oldest = min(dates)
    days_span = max(1, (newest - oldest).days)
    estimated_monthly = round((len(sold_items) / days_span) * 30)

    confidence = "low"
    if len(sold_items) >= 20 and days_span >= 10:
        confidence = "high"
    elif len(sold_items) >= 10 and days_span >= 5:
        confidence = "medium"

    return {
        "estimated_monthly_sales": estimated_monthly,
        "confidence": confidence,
        "sold_items_count": len(sold_items),
    }
