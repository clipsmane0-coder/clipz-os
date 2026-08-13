"""
eBay Trading API Client (works from Fly.io, bypasses Akamai)
Uses Auth'n'Auth token with Trading API XML endpoint
"""
import httpx
import re
from typing import Optional, List, Dict, Any
import xml.etree.ElementTree as ET

EBAY_APP_ID = "ELVINACQ-ArbSens-PRD-5f8516031-l7108a53"
EBAY_CERT_ID = "PRD-f851603le984-0a58-4b00-9cef-08fa"
EBAY_DEV_ID = "83d5b459-94bd-4963-a899-e694003ecde4"
EBAY_AUTH_TOKEN = "v^1.1#i^1#p^3#I^3#r^1#f^0#t^Ul4xMF84OjVFNEVEMkM3OTk5NTUxRUI0MkJGN0VERDFEOTBBNzUzXzJfMSNFXjI2MA=="

EBAY_TRADING_API = "https://api.ebay.com/ws/api.dll"
API_COMPATIBILITY_LEVEL = "1201"
SITE_ID = "0"  # US


def _strip_ns(tag: str) -> str:
    """Remove XML namespace from tag name."""
    return tag.split('}')[-1] if '}' in tag else tag


def _xml_to_dict(elem) -> Dict:
    """Convert XML element to a nested dict."""
    result = {}
    children = list(elem)
    if not children:
        return elem.text if elem.text else ""

    # Check if children are all same tag (array)
    tag_counts = {}
    for child in children:
        tag = _strip_ns(child.tag)
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    for child in children:
        tag = _strip_ns(child.tag)
        val = _xml_to_dict(child)

        if tag_counts[tag] > 1:
            # This is an array element
            if tag not in result:
                result[tag] = []
            if isinstance(result[tag], list):
                result[tag].append(val)
        else:
            result[tag] = val

    return result


async def _call_trading_api(call_name: str, request_xml_body: str) -> Dict:
    """Make a call to the eBay Trading API."""
    headers = {
        "X-EBAY-API-CALL-NAME": call_name,
        "X-EBAY-API-SITEID": SITE_ID,
        "X-EBAY-API-COMPATIBILITY-LEVEL": API_COMPATIBILITY_LEVEL,
        "X-EBAY-API-APP-ID": EBAY_APP_ID,
        "X-EBAY-API-DEV-ID": EBAY_DEV_ID,
        "X-EBAY-API-CERT-ID": EBAY_CERT_ID,
        "Content-Type": "text/xml; charset=utf-8",
    }

    xml_full = f"""<?xml version="1.0" encoding="utf-8"?>
<{call_name}Request xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{EBAY_AUTH_TOKEN}</eBayAuthToken>
  </RequesterCredentials>
{request_xml_body}
</{call_name}Request>"""

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            EBAY_TRADING_API,
            content=xml_full,
            headers=headers,
        )

    if response.status_code != 200:
        raise Exception(f"eBay Trading API error {response.status_code}: {response.text[:200]}")

    root = ET.fromstring(response.text)
    result = _xml_to_dict(root)

    ack = result.get("Ack", "Unknown")
    if ack not in ("Success", "Warning"):
        errors = result.get("Errors", [])
        if isinstance(errors, dict):
            errors = [errors]
        raise Exception(
            f"eBay API {call_name} failed: {ack}. "
            f"Errors: {[e.get('ShortMessage', 'unknown') for e in errors[:3]]}"
        )

    return result


async def get_categories(category_parent: str = "-1", level_limit: int = 1) -> List[Dict]:
    """Get eBay categories under a parent category."""
    body = f"""
  <CategorySiteID>0</CategorySiteID>
  <DetailLevel>ReturnAll</DetailLevel>
  <LevelLimit>{level_limit}</LevelLimit>
  <CategoryParent>{category_parent}</CategoryParent>
  <ViewAllNodes>true</ViewAllNodes>
"""
    result = await _call_trading_api("GetCategories", body)
    cats = result.get("CategoryArray", {}).get("Category", [])
    if isinstance(cats, dict):
        cats = [cats]
    return cats


async def get_category_listings(
    category_id: str,
    max_items: int = 10,
    page: int = 1,
    item_type: str = "FixedPriceItem",
) -> Dict:
    """Get active listings from a category."""
    body = f"""
  <CategoryID>{category_id}</CategoryID>
  <MaxItems>{max_items}</MaxItems>
  <PageNumber>{page}</PageNumber>
  <ItemTypeFilter>{item_type}</ItemTypeFilter>
  <IncludeWatchCount>true</IncludeWatchCount>
"""
    result = await _call_trading_api("GetCategoryListings", body)
    items = result.get("ItemArray", {}).get("Item", [])
    if isinstance(items, dict):
        items = [items]
    result["_items_list"] = items
    return result


async def get_item(item_id: str, include_description: bool = False) -> Dict:
    """Get details for a specific item."""
    detail = "ItemReturnDescription" if include_description else "ReturnAll"
    body = f"""
  <ItemID>{item_id}</ItemID>
  <DetailLevel>{detail}</DetailLevel>
  <IncludeItemSpecifics>true</IncludeItemSpecifics>
  <IncludeWatchCount>true</IncludeWatchCount>
"""
    result = await _call_trading_api("GetItem", body)
    return result.get("Item", {})


# --- High potential categories (manually verified eBay category IDs) ---
# These are real eBay category IDs for common multipack-friendly categories
MULTIPACK_CATEGORIES = {
    "vitamins_supplements": "184634",
    "skin_care": "22083",
    "hair_care": "1085666",
    "over_counter": "162931",
    "oral_care": "162953",
    "shaving": "162948",
    "protein_supplements": "60083",
    "dietary_supplements": "74951",
}

# Discovery flow:
# 1. Get top-level categories (ParentCategoryID=-1, LevelLimit=1)
# 2. Navigate down to Health & Beauty > Vitamins & Supplements
# 3. Get category listings
# 4. For high-velocity items, get full item details
# 5. Cross-reference with Amazon pricing
