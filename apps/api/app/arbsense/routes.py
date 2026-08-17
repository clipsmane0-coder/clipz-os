"""
ArbSense API Routes
eBay multipack arbitrage discovery and analysis
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

from .ebay_client import ebay_search, HIGH_POTENTIAL_CATEGORIES
from .ebay_test import test_all_endpoints
from .ebay_trading import get_categories, get_category_listings, get_item, MULTIPACK_CATEGORIES
from .ebay_browse import (
    search_items,
    get_item as browse_get_item,
    extract_listing_price,
    extract_shipping,
    get_lowest_price,
    get_median_price,
)
from .engine import (
    analyze_all_configs,
    generate_listing,
    score_opportunity,
    format_analysis_report,
)

router = APIRouter(prefix="/arbsense", tags=["arbsense"])


@router.get("/ebay/search")
async def api_ebay_search(
    q: str = Query(..., description="Search keywords"),
    category_id: Optional[str] = None,
    condition: Optional[str] = None,
    sold: bool = False,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 25,
):
    """Search eBay and return results with velocity estimates."""
    try:
        result = await ebay_search(
            keywords=q,
            category_id=category_id,
            condition=condition,
            sold_only=sold,
            min_price=min_price,
            max_price=max_price,
            entries_per_page=limit,
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze")
async def api_analyze(
    product: str = Query(..., description="Product name"),
    brand: str = Query("Generic", description="Brand name"),
    source_price: float = Query(..., description="Source pack price"),
    source_size: int = Query(..., description="Source pack size (units)"),
    ebay1: Optional[float] = None,
    ebay2: Optional[float] = None,
    ebay3: Optional[float] = None,
    ebay4: Optional[float] = None,
    ebay6: Optional[float] = None,
    ebay8: Optional[float] = None,
    ebay12: Optional[float] = None,
    shipping: Optional[float] = None,
    monthly_sales: int = 0,
    velocity_confidence: str = "low",
):
    """Run full multipack profit analysis on a product."""
    ebay_prices: Dict[int, float] = {}
    for size, price in [
        (1, ebay1), (2, ebay2), (3, ebay3), (4, ebay4),
        (6, ebay6), (8, ebay8), (12, ebay12),
    ]:
        if price is not None and price > 0:
            ebay_prices[size] = price

    if not ebay_prices:
        raise HTTPException(
            status_code=400,
            detail="No eBay prices provided. Use ebay1, ebay2, ebay3, etc.",
        )

    configs, best = analyze_all_configs(
        source_price, source_size, ebay_prices, shipping_cost=shipping
    )

    listing = generate_listing(
        product, brand, best.sell_units,
        best.total_revenue / best.number_of_listings if best.number_of_listings > 0 else 0,
    )

    score, risk_factors = score_opportunity(best, {
        "estimated_monthly_sales": monthly_sales,
        "confidence": velocity_confidence,
    })

    report = format_analysis_report(
        product, brand, source_price, source_size,
        best, configs,
        {"estimated_monthly_sales": monthly_sales, "confidence": velocity_confidence,
         "sold_items_count": monthly_sales},
        score, risk_factors,
    )

    return {
        "success": True,
        "meets_threshold": best.net_profit >= 40,
        "score": score,
        "source": {
            "price": source_price,
            "size": source_size,
            "cost_per_unit": source_price / source_size,
        },
        "best_config": {
            "sell_size": best.sell_units,
            "sell_price": best.total_revenue / best.number_of_listings if best.number_of_listings > 0 else 0,
            "listings_per_pack": best.number_of_listings,
            "leftover_units": best.leftover_units,
            "net_profit": best.net_profit,
            "profit_per_listing": best.profit_per_listing,
            "roi": best.roi,
            "margin": best.margin,
            "break_even": best.break_even_sell_price,
        },
        "all_configs": [
            {
                "sell_size": c.sell_units,
                "sell_price": c.total_revenue / c.number_of_listings if c.number_of_listings > 0 else 0,
                "net_profit": c.net_profit,
                "roi": c.roi,
                "margin": c.margin,
            }
            for c in configs
        ],
        "risk_factors": risk_factors,
        "listing": {
            "title": listing.title,
            "description": listing.description,
            "price": listing.price,
            "category": listing.category,
            "condition": listing.condition,
            "item_specifics": listing.item_specifics,
            "shipping": listing.shipping,
            "handling_time": listing.handling_time,
            "image_requirements": listing.image_requirements,
        },
        "report": report,
    }


@router.get("/categories")
async def api_categories():
    """List high-potential categories for multipack arbitrage."""
    return {
        "success": True,
        "categories": [
            {"name": name, "ebay_category_id": cat_id}
            for name, cat_id in HIGH_POTENTIAL_CATEGORIES.items()
        ],
    }


@router.get("/test-ebay-apis")
async def api_test_ebay_apis():
    """Test all eBay API endpoints from this server to find which ones work."""
    try:
        results = await test_all_endpoints()
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/tree")
async def api_categories_tree(
    parent: str = "-1",
    level: int = 1,
):
    """Browse eBay category tree via Trading API (works from Fly.io)."""
    try:
        categories = await get_categories(category_parent=parent, level_limit=level)
        return {"success": True, "count": len(categories), "categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/listings")
async def api_category_listings(
    category_id: str = "184634",
    max_items: int = 10,
    page: int = 1,
):
    """Get active listings from an eBay category via Trading API."""
    try:
        result = await get_category_listings(category_id, max_items, page)
        items = result.get("_items_list", [])
        total = result.get("PaginationResult", {}).get("TotalNumberOfEntries", 0)
        has_more = result.get("HasMoreItems", "false") == "true"

        formatted = []
        for item in items:
            if not isinstance(item, dict):
                continue
            formatted.append({
                "item_id": item.get("ItemID", ""),
                "title": item.get("Title", ""),
                "price": float(item.get("BuyItNowPrice", {}).get("value", 0))
                       if isinstance(item.get("BuyItNowPrice"), dict)
                       else float(item.get("CurrentPrice", {}).get("value", 0))
                       if isinstance(item.get("CurrentPrice"), dict)
                       else 0,
                "quantity": item.get("Quantity", 0),
                "seller": item.get("Seller", {}).get("UserID", "")
                        if isinstance(item.get("Seller"), dict) else "",
                "watch_count": item.get("WatchCount", 0),
                "category_id": item.get("PrimaryCategory", {}).get("CategoryID", "")
                              if isinstance(item.get("PrimaryCategory"), dict) else "",
                "category_name": item.get("PrimaryCategory", {}).get("CategoryName", "")
                                if isinstance(item.get("PrimaryCategory"), dict) else "",
            })

        return {
            "success": True,
            "category_id": category_id,
            "total": total,
            "count": len(formatted),
            "has_more": has_more,
            "items": formatted,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item/{item_id}")
async def api_item_detail(item_id: str):
    """Get full details for a specific eBay item via Trading API."""
    try:
        item = await get_item(item_id, include_description=False)
        return {"success": True, "item": item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/browse/search")
async def api_browse_search(
    q: str = Query(..., description="Search keywords"),
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 20,
    sort: str = "-price",
):
    """Search eBay marketplace via Browse API (bypasses Akamai)."""
    try:
        items = await search_items(
            keyword=q,
            limit=limit,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
        )
        prices = [extract_listing_price(i) for i in items if extract_listing_price(i) > 0]
        return {
            "success": True,
            "total_found": len(items),
            "lowest_price": min(prices) if prices else 0,
            "median_price": sorted(prices)[len(prices)//2] if prices else 0,
            "items": items,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discover")
async def api_discover(
    keyword: str = Query(..., description="Product to analyze (eBay side)"),
    source_price: float = Query(..., description="Source multipack price"),
    source_size: int = Query(..., description="Source pack size (number of units)"),
    brand: str = "Generic",
    min_profit: float = 40.0,
):
    """
    Full discovery + analysis for a product:
    1. Search eBay for the product (Browse API)
    2. Get median market price
    3. Run multipack analysis against source price
    4. Return whether it meets the profit threshold
    """
    try:
        # Step 1: Search eBay for market price data
        items = await search_items(keyword=keyword, limit=30, sort="price")
        if not items:
            return {
                "success": False,
                "keyword": keyword,
                "error": "No eBay listings found for this keyword",
            }

        # Step 2: Compute market price metrics
        prices = sorted([extract_listing_price(i) for i in items if extract_listing_price(i) > 0])
        if not prices:
            return {"success": False, "error": "No valid prices found"}

        shipping_costs = [extract_shipping(i) for i in items if extract_listing_price(i) > 0]
        avg_shipping = sum(shipping_costs) / len(shipping_costs) if shipping_costs else 0.0

        # Use median price as market price (robust against outliers)
        median_price = prices[len(prices)//2]
        low_price = prices[0]
        high_price = prices[-1]

        # Step 3: Analyze against source pack
        # For eBay side, we test multiple single-unit resale scenarios
        ebay_prices = {1: median_price}

        configs, best = analyze_all_configs(
            source_price, source_size, ebay_prices, shipping_cost=avg_shipping
        )

        score, risk_factors = score_opportunity(best, {
            "estimated_monthly_sales": 0,
            "confidence": "medium",
        })

        # Generate listing
        listing = generate_listing(
            keyword, brand, best.sell_units,
            best.total_revenue / best.number_of_listings if best.number_of_listings > 0 else 0,
        )

        report = format_analysis_report(
            keyword, brand, source_price, source_size,
            best, configs,
            {
                "estimated_monthly_sales": 0,
                "confidence": "medium",
                "sold_items_count": len(prices),
                "ebay_listings_found": len(items),
                "ebay_low_price": low_price,
                "ebay_median_price": median_price,
                "ebay_high_price": high_price,
            },
            score, risk_factors,
        )

        return {
            "success": True,
            "meets_threshold": best.net_profit >= min_profit,
            "keyword": keyword,
            "ebay_market": {
                "listings_found": len(items),
                "lowest_price": low_price,
                "median_price": median_price,
                "highest_price": high_price,
                "avg_shipping": avg_shipping,
            },
            "source": {
                "price": source_price,
                "size": source_size,
                "cost_per_unit": source_price / source_size,
            },
            "best_config": {
                "sell_size": best.sell_units,
                "sell_price": best.total_revenue / best.number_of_listings if best.number_of_listings > 0 else 0,
                "listings_per_pack": best.number_of_listings,
                "leftover_units": best.leftover_units,
                "net_profit": best.net_profit,
                "profit_per_listing": best.profit_per_listing,
                "roi": best.roi,
                "margin": best.margin,
            },
            "risk_factors": risk_factors,
            "listing": {
                "title": listing.title,
                "description": listing.description,
                "price": listing.price,
                "category": listing.category,
                "condition": listing.condition,
            },
            "report": report,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Curated arbitrage candidates — higher-ticket, $40+ net profit target.
#
# HARD RULE: multipack analysis only applies to TRUE MULTIPACKS — products
# containing multiple physically separate, individually packaged retail units.
#
# HARD RULE: minimum $40 estimated net profit to appear in qualified results.
#
# Source prices are realistic estimates from typical Amazon/Costco pricing.
# All prices are marked UNVERIFIED — verify via the product link before acting.
# eBay prices are realistic market estimates — verify via eBay search link.
CURATED_OPPORTUNITIES = [
    {
        "id": "ARB-001",
        "product": "Apple AirTag 4 Pack",
        "brand": "Apple",
        "category": "Electronics / Smart Home",
        "source_price": 79.99,
        "source_size": 4,
        "source_url": "https://www.amazon.com/dp/B0932BSQ7W",
        "source_status": "unverified",
        "ebay_price": 129.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Apple+AirTag+4+Pack+New",
        "ebay_listings_est": 120,
        "multipack_status": "true_multipack",
        "unit_description": "4 individually sealed AirTags in retail box",
        "strategy": "Buy 4-pack on Amazon, resell as 4-pack on eBay. Price spread from Amazon discount vs. eBay retail.",
        "demand_level": "very high",
        "notes": "High demand, fast turnover. Apple brand sells itself. Verify current Amazon price — often on sale for $79.",
    },
    {
        "id": "ARB-002",
        "product": "Bose QuietComfort Earbuds II",
        "brand": "Bose",
        "category": "Electronics / Audio",
        "source_price": 169.00,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B0BC6Y8NQ8",
        "source_status": "unverified",
        "ebay_price": 249.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Bose+QuietComfort+Earbuds+II+New",
        "ebay_listings_est": 45,
        "multipack_status": "single_product",
        "unit_description": "1 pair of earbuds in retail packaging",
        "strategy": "Buy on Amazon sale/certified-refurb (~$169), resell new/sealed on eBay at $249. Premium audio with strong resale.",
        "demand_level": "high",
        "notes": "Bose regularly discounts QC Earbuds II to $169-199. eBay holds $249-279 for new. Certified refurbished units can source even cheaper. Verify condition and warranty.",
    },
    {
        "id": "ARB-003",
        "product": "Sony WH-1000XM5 Wireless Headphones",
        "brand": "Sony",
        "category": "Electronics / Audio",
        "source_price": 248.00,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B0B9NVMGVH",
        "source_status": "unverified",
        "ebay_price": 349.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Sony+WH-1000XM5+Wireless+Headphones+New",
        "ebay_listings_est": 60,
        "multipack_status": "single_product",
        "unit_description": "1 pair headphones in retail box",
        "strategy": "Buy on Amazon sale (~$248), resell at eBay retail ($349). Flagship ANC headphones with massive demand.",
        "demand_level": "very high",
        "notes": "Regularly drops to $248-279 on Amazon. eBay retail holds at $349-379. One of the highest-demand premium electronics. Strong, consistent sales velocity.",
    },
    {
        "id": "ARB-004",
        "product": "Dyson V8 Cordless Vacuum (Refurbished)",
        "brand": "Dyson",
        "category": "Home / Appliances",
        "source_price": 199.99,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B07P46L62S",
        "source_status": "unverified",
        "ebay_price": 299.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Dyson+V8+cordless+vacuum+refurbished",
        "ebay_listings_est": 35,
        "multipack_status": "single_product",
        "unit_description": "1 refurbished vacuum + attachments",
        "strategy": "Buy refurbished Dyson on Amazon, resell as manufacturer-refurbished on eBay. People pay premium for Dyson.",
        "demand_level": "high",
        "notes": "Dyson brand commands strong resale. Verify refurb warranty. Higher shipping cost due to weight.",
    },
    {
        "id": "ARB-005",
        "product": "Philips Hue White & Color Ambiance 4 Pack",
        "brand": "Philips Hue",
        "category": "Smart Home / Lighting",
        "source_price": 39.99,
        "source_size": 4,
        "source_url": "https://www.amazon.com/dp/B07R3WLZ1Q",
        "source_status": "unverified",
        "ebay_price": 89.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Philips+Hue+White+Color+Ambiance+4+Pack+A19",
        "ebay_listings_est": 80,
        "multipack_status": "true_multipack",
        "unit_description": "4 individually boxed smart bulbs in 4-pack",
        "strategy": "Buy 4-pack on Amazon sale, resell as individual bulbs or 2-packs on eBay for combined higher total.",
        "demand_level": "high",
        "notes": "Smart lighting is hot. Can split into singles or 2-packs for better total return. Frequently on sale.",
    },
    {
        "id": "ARB-006",
        "product": "KitchenAid Artisan Stand Mixer (Refurb)",
        "brand": "KitchenAid",
        "category": "Kitchen / Appliances",
        "source_price": 259.99,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B00005UP2P",
        "source_status": "unverified",
        "ebay_price": 379.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=KitchenAid+Artisan+Stand+Mixer+refurbished",
        "ebay_listings_est": 25,
        "multipack_status": "single_product",
        "unit_description": "1 refurbished mixer in box",
        "strategy": "Buy certified-refurbished KitchenAid on Amazon, resell as refurbished on eBay. Iconic brand with cult following.",
        "demand_level": "medium-high",
        "notes": "Very heavy — shipping is $20-30. Higher ticket means higher absolute profit even with higher costs. Brand is king.",
    },
    {
        "id": "ARB-007",
        "product": "Instant Pot Duo 7-in-1 6 Quart",
        "brand": "Instant Pot",
        "category": "Kitchen / Appliances",
        "source_price": 49.99,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B00FLYWNYQ",
        "source_status": "unverified",
        "ebay_price": 99.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Instant+Pot+Duo+7-in-1+6+Quart+New",
        "ebay_listings_est": 50,
        "multipack_status": "single_product",
        "unit_description": "1 pressure cooker in retail box",
        "strategy": "Buy on deep discount/Prime Day, resell at regular retail on eBay. Large price spread when on sale.",
        "demand_level": "high",
        "notes": "Frequently drops to $49-59 on sale. Strong steady demand. Bulky but standard shipping.",
    },
    {
        "id": "ARB-008",
        "product": "Ninja AF101 Air Fryer 4 Quart",
        "brand": "Ninja",
        "category": "Kitchen / Appliances",
        "source_price": 69.99,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B07G5JV2B5",
        "source_status": "unverified",
        "ebay_price": 129.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Ninja+AF101+Air+Fryer+4+Quart+New",
        "ebay_listings_est": 40,
        "multipack_status": "single_product",
        "unit_description": "1 air fryer in retail box",
        "strategy": "Buy on Amazon sale/coupon, resell on eBay at market price. Popular category with strong demand.",
        "demand_level": "very high",
        "notes": "Top-selling air fryer. Regularly discounted. High demand year-round.",
    },
    {
        "id": "ARB-009",
        "product": "Ring Video Doorbell 4",
        "brand": "Ring",
        "category": "Smart Home / Security",
        "source_price": 129.99,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B08WNQJM6Y",
        "source_status": "unverified",
        "ebay_price": 189.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Ring+Video+Doorbell+4+New",
        "ebay_listings_est": 55,
        "multipack_status": "single_product",
        "unit_description": "1 video doorbell in retail box",
        "strategy": "Buy on Amazon sale (~$129), resell on eBay at $189. Amazon-owned brand with frequent discounts.",
        "demand_level": "high",
        "notes": "Ring regularly drops to $129-149 on Amazon. eBay holds $179-199. High demand smart home security. Lightweight, cheap to ship.",
    },
    {
        "id": "ARB-010",
        "product": "Arlo Pro 4 Spotlight Camera 3 Pack",
        "brand": "Arlo",
        "category": "Smart Home / Security",
        "source_price": 299.99,
        "source_size": 3,
        "source_url": "https://www.amazon.com/dp/B08CJQ27S9",
        "source_status": "unverified",
        "ebay_price": 429.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Arlo+Pro+4+Spotlight+Camera+3+Pack",
        "ebay_listings_est": 20,
        "multipack_status": "true_multipack",
        "unit_description": "3 individually packaged cameras + base station",
        "strategy": "Buy 3-pack on Amazon sale, resell whole kit on eBay. Can also split into individual cameras for potentially higher total.",
        "demand_level": "medium-high",
        "notes": "Higher-ticket security bundle. Check if individual camera resale beats selling as bundle.",
    },
    {
        "id": "ARB-011",
        "product": "Apple Pencil (2nd Generation)",
        "brand": "Apple",
        "category": "Electronics / Accessories",
        "source_price": 89.00,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B08PF9V9CM",
        "source_status": "unverified",
        "ebay_price": 139.00,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Apple+Pencil+2nd+Generation+New",
        "ebay_listings_est": 150,
        "multipack_status": "single_product",
        "unit_description": "1 Apple Pencil in retail box",
        "strategy": "Buy on Amazon sale/back-to-school, resell on eBay. High demand Apple accessory.",
        "demand_level": "very high",
        "notes": "Highly desirable. Small, lightweight — cheap to ship. Tons of listings but also tons of demand.",
    },
    {
        "id": "ARB-012",
        "product": "Logitech MX Master 3S Mouse",
        "brand": "Logitech",
        "category": "Electronics / Peripherals",
        "source_price": 79.99,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B09HM94VDS",
        "source_status": "unverified",
        "ebay_price": 129.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Logitech+MX+Master+3S+Mouse+New",
        "ebay_listings_est": 45,
        "multipack_status": "single_product",
        "unit_description": "1 mouse in retail box",
        "strategy": "Buy on Amazon sale, resell on eBay at market price. Premium productivity mouse.",
        "demand_level": "high",
        "notes": "Top-tier productivity mouse. Regularly on sale. Strong demand from professionals.",
    },
    {
        "id": "ARB-013",
        "product": "TP-Link Kasa Smart Plug HS103 4-Pack",
        "brand": "TP-Link",
        "category": "Smart Home",
        "source_price": 24.99,
        "source_size": 4,
        "source_url": "https://www.amazon.com/dp/B07RCNB2L3",
        "source_status": "unverified",
        "ebay_price": 54.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=TP-Link+Kasa+Smart+Plug+HS103+4+Pack",
        "ebay_listings_est": 35,
        "multipack_status": "true_multipack",
        "unit_description": "4 individually boxed smart plugs",
        "strategy": "Buy 4-pack on sale, resell as 2-packs or individual plugs on eBay. Small, lightweight, high demand.",
        "demand_level": "high",
        "notes": "Great for splitting. Each plug individually packaged. Low shipping cost. Verify current sale price.",
    },
    {
        "id": "ARB-014",
        "product": "Cricut Explore 3 Machine",
        "brand": "Cricut",
        "category": "Crafts / Tools",
        "source_price": 199.99,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B08Y613X17",
        "source_status": "unverified",
        "ebay_price": 299.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Cricut+Explore+3+Machine+New",
        "ebay_listings_est": 30,
        "multipack_status": "single_product",
        "unit_description": "1 Cricut machine in retail box",
        "strategy": "Buy on Amazon sale/Prime Day, resell on eBay at retail price. Cricut has strong following.",
        "demand_level": "high",
        "notes": "Crafters love Cricut. Large but not super heavy. Good price spread when on sale.",
    },
    {
        "id": "ARB-015",
        "product": "Dewalt 20V MAX Drill/Driver Kit",
        "brand": "DeWalt",
        "category": "Tools / Power Tools",
        "source_price": 99.99,
        "source_size": 1,
        "source_url": "https://www.amazon.com/dp/B07RK27SZL",
        "source_status": "unverified",
        "ebay_price": 159.99,
        "ebay_search_url": "https://www.ebay.com/sch/i.html?_nkw=Dewalt+20V+MAX+Drill+Driver+Kit+New",
        "ebay_listings_est": 55,
        "multipack_status": "single_product",
        "unit_description": "1 drill + battery + charger kit",
        "strategy": "Buy on Amazon sale, resell on eBay. DeWalt is a premium tool brand with strong resale.",
        "demand_level": "high",
        "notes": "DeWalt commands premium pricing. Kit format — 1 tool + battery + charger. Moderate weight.",
    },
]


@router.get("/curated")
async def api_curated(
    category: Optional[str] = None,
    min_profit: float = 40.0,
    include_below_threshold: bool = False,
    multipack_only: bool = False,
    page: int = 1,
    per_page: int = 50,
    sort_by: str = "net_profit",
    sort_dir: str = "desc",
    search: Optional[str] = None,
):
    """
    Curated arbitrage opportunities — higher-ticket, $40+ net profit target.
    
    FORMAT: each opportunity is a simple BUY → SELL → PROFIT card:
      - Amazon Price (source, UNVERIFIED — verify via link)
      - eBay Selling Price (estimated — verify via eBay search link)
      - Estimated Net Profit
    
    HARD RULES:
    - $40 minimum estimated net profit for primary list (set min_profit lower to see more)
    - Multipack analysis only applies to TRUE MULTIPACKS
    - All source prices are UNVERIFIED estimates — check the actual link
    
    Detailed calculations (ROI, margin, break-even, fee breakdown, config analysis)
    are available in the 'calculations' field of each opportunity.
    """
    candidates = []

    for c in CURATED_OPPORTUNITIES:
        src_price = c["source_price"]
        sell_price = c["ebay_price"]
        mp_status = c.get("multipack_status", "unverified")
        num_units = c["source_size"]
        
        fees_pct = 0.13 + 0.03  # eBay final value + payment processing
        payment_fixed = 0.30
        shipping_est = 6.0  # estimated average shipping cost

        # ============================================================
        # MULTIPACK CLASSIFICATION HARD RULE
        # ============================================================
        best_config = None
        configurations = []

        if mp_status == "true_multipack" and num_units > 1:
            # Evaluate all valid split configurations
            # Config 1: whole pack (1 listing)
            revenue = sell_price
            total_fees = revenue * fees_pct + payment_fixed
            total_shipping = shipping_est
            net = revenue - src_price - total_fees - total_shipping
            configurations.append({
                "sell_size": num_units,
                "num_listings": 1,
                "sell_price_per_listing": sell_price,
                "revenue": revenue,
                "total_fees": round(total_fees, 2),
                "total_shipping": round(total_shipping, 2),
                "net_profit": round(net, 2),
                "profit_per_listing": round(net, 2),
                "roi": round((net / src_price * 100) if src_price else 0, 1),
                "margin": round((net / revenue * 100) if revenue else 0, 1),
            })
            
            # Configs 2..N: split into chunks
            valid_splits = []
            for divisor in range(2, min(num_units, 8) + 1):
                if num_units % divisor == 0 and divisor <= 12:
                    chunk_size = num_units // divisor
                    valid_splits.append((divisor, chunk_size))
            
            for num_listings, chunk_size in valid_splits:
                per_chunk_price = sell_price / num_listings * 1.1  # 10% premium for smaller packs
                revenue = per_chunk_price * num_listings
                total_fees = sum(
                    per_chunk_price * fees_pct + payment_fixed
                    for _ in range(num_listings)
                )
                total_shipping = 4.0 * num_listings
                net = revenue - src_price - total_fees - total_shipping
                configurations.append({
                    "sell_size": chunk_size,
                    "num_listings": num_listings,
                    "sell_price_per_listing": round(per_chunk_price, 2),
                    "revenue": round(revenue, 2),
                    "total_fees": round(total_fees, 2),
                    "total_shipping": round(total_shipping, 2),
                    "net_profit": round(net, 2),
                    "profit_per_listing": round(net / num_listings, 2),
                    "roi": round((net / src_price * 100) if src_price else 0, 1),
                    "margin": round((net / revenue * 100) if revenue else 0, 1),
                })
            
            best_config = max(configurations, key=lambda x: x["net_profit"])
        else:
            # Single product — evaluate as-is only
            revenue = sell_price
            total_fees = revenue * fees_pct + payment_fixed
            total_shipping = shipping_est
            net = revenue - src_price - total_fees - total_shipping
            best_config = {
                "sell_size": num_units,
                "num_listings": 1,
                "sell_price_per_listing": sell_price,
                "revenue": revenue,
                "total_fees": round(total_fees, 2),
                "total_shipping": round(total_shipping, 2),
                "net_profit": round(net, 2),
                "profit_per_listing": round(net, 2),
                "roi": round((net / src_price * 100) if src_price else 0, 1),
                "margin": round((net / revenue * 100) if revenue else 0, 1),
            }
            configurations = [best_config]

        # Full detailed calculations (shown under expandable section)
        calculations = {
            "amazon_price": src_price,
            "ebay_sell_price": best_config["sell_price_per_listing"],
            "revenue": best_config["revenue"],
            "ebay_fees": round(best_config["total_fees"], 2),
            "shipping_cost": round(best_config["total_shipping"], 2),
            "source_cost": src_price,
            "net_profit": best_config["net_profit"],
            "roi": best_config["roi"],
            "margin": best_config["margin"],
            "break_even": round(src_price / best_config["num_listings"], 2),
            "all_configurations": configurations,
        }

        candidates.append({
            "id": c.get("id", ""),
            "product": c["product"],
            "brand": c["brand"],
            "category": c["category"],
            "amazon_price": src_price,
            "amazon_link": c["source_url"],
            "amazon_status": c["source_status"],  # verified / unverified
            "ebay_price": best_config["sell_price_per_listing"],
            "ebay_link": c["ebay_search_url"],
            "ebay_listings_est": c["ebay_listings_est"],
            "net_profit": best_config["net_profit"],
            "profit_per_listing": best_config["profit_per_listing"],
            "roi": best_config["roi"],
            "strategy": c["strategy"],
            "demand_level": c["demand_level"],
            "notes": c["notes"],
            "multipack_status": mp_status,
            "unit_description": c.get("unit_description", ""),
            "best_configuration": best_config,
            "calculations": calculations,
            "meets_threshold": best_config["net_profit"] >= 40.0,
            "profit_tier": (
                "premium" if best_config["net_profit"] >= 100
                else "preferred" if best_config["net_profit"] >= 60
                else "qualified" if best_config["net_profit"] >= 40
                else "below_threshold"
            ),
        })

    # Filter: $40 gate by default (unless include_below_threshold)
    if not include_below_threshold:
        candidates = [c for c in candidates if c["net_profit"] >= min_profit]
    elif min_profit > 0:
        candidates = [c for c in candidates if c["net_profit"] >= min_profit]

    # Filter to multipack-only if requested
    if multipack_only:
        candidates = [c for c in candidates if c["multipack_status"] == "true_multipack"]

    # Filter by category
    if category and category.lower() != "all":
        candidates = [c for c in candidates if category.lower() in c["category"].lower()]

    # Filter by search term
    if search:
        search_lower = search.lower()
        candidates = [
            c for c in candidates
            if search_lower in c["product"].lower()
            or search_lower in c["brand"].lower()
            or search_lower in c["category"].lower()
        ]

    # Sort
    reverse = sort_dir.lower() == "desc"
    sort_key_map = {
        "net_profit": "net_profit",
        "roi": "roi",
        "profit_per_listing": "profit_per_listing",
        "ebay_price": "ebay_price",
        "amazon_price": "amazon_price",
        "ebay_listings": "ebay_listings_est",
    }
    sort_key = sort_key_map.get(sort_by, "net_profit")
    candidates.sort(key=lambda x: x[sort_key], reverse=reverse)

    total = len(candidates)
    categories = sorted(set(c["category"].split(" / ")[0] for c in candidates))

    # Pagination
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    paginated = candidates[start:end]

    # Stats
    premium_count = sum(1 for c in candidates if c["net_profit"] >= 100)
    preferred_count = sum(1 for c in candidates if 60 <= c["net_profit"] < 100)
    qualified_count = sum(1 for c in candidates if 40 <= c["net_profit"] < 60)

    return {
        "success": True,
        "opportunities": paginated,
        "total": total,
        "total_pages": total_pages,
        "total_scanned": len(CURATED_OPPORTUNITIES),
        "premium_count": premium_count,  # $100+
        "preferred_count": preferred_count,  # $60-$99
        "qualified_count": qualified_count,  # $40-$59
        "multipack_count": sum(1 for c in candidates if c["multipack_status"] == "true_multipack"),
        "single_product_count": sum(1 for c in candidates if c["multipack_status"] == "single_product"),
        "page": page,
        "per_page": per_page,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "categories": categories,
        "data_source": "curated",
        "min_profit_threshold": min_profit if not include_below_threshold else 40.0,
        "format": "simple — buy → sell → profit",
        "note": (
            "All Amazon prices are UNVERIFIED estimates. Always click the Amazon "
            "link to check the current price before sourcing. eBay prices are "
            "estimated market values — verify with the eBay search link."
        ),
        "profit_tiers": {
            "premium": "$100+ net profit",
            "preferred": "$60-$99 net profit",
            "qualified": "$40-$59 net profit",
            "below_threshold": "Under $40 — filtered out by default",
        },
    }


@router.get("/scan")
async def api_scan(
    category: Optional[str] = None,
    min_profit: float = 0,
    max_results: int = 0,
    page: int = 1,
    per_page: int = 50,
    sort_by: str = "net_profit",
    sort_dir: str = "desc",
    search: Optional[str] = None,
):
    """
    Scan for opportunities across 100+ preset products.
    Supports pagination, sorting, filtering, and search.
    """
    from .ebay_browse import search_items, extract_listing_price
    from .engine import analyze_all_configs

    # Curated product list: (keyword, source_price, source_size, brand, category)
    # Source prices = typical Amazon/Costco multipack prices
    SCAN_KEYWORDS = [
        # === HEALTH & BEAUTY: Hair Care (14) ===
        ("Kirkland Minoxidil 5% 6 month", 29.99, 6, "Kirkland", "Hair Loss Treatments"),
        ("Rogaine Minoxidil 5% foam 3 month", 44.99, 3, "Rogaine", "Hair Loss Treatments"),
        ("Nioxin System 4 shampoo conditioner duo", 39.99, 2, "Nioxin", "Hair Loss Treatments"),
        ("Olaplex No. 3 Hair Perfector 3.3 oz 2 pack", 54.99, 2, "Olaplex", "Hair Treatments"),
        ("Moroccanoil Treatment 100ml 2 pack", 69.99, 2, "Moroccanoil", "Hair Treatments"),
        ("Redken Extreme Shampoo Conditioner 33.8 oz duo", 49.99, 2, "Redken", "Shampoo & Conditioner"),
        ("Biolage Color Last Shampoo Conditioner 33.8 oz", 34.99, 2, "Biolage", "Shampoo & Conditioner"),
        ("TRESemme Keratin Smooth Shampoo Conditioner 28oz 4 pack", 19.99, 4, "TRESemme", "Shampoo & Conditioner"),
        ("Herbal Essences bio renew shampoo 4 pack", 14.99, 4, "Herbal Essences", "Shampoo & Conditioner"),
        ("Pantene Pro-V Shampoo Conditioner 27.7oz 2 pack", 12.99, 2, "Pantene", "Shampoo & Conditioner"),
        ("Dove Shampoo Conditioner 24 oz 4 pack", 16.99, 4, "Dove", "Shampoo & Conditioner"),
        ("OGX Argan Oil of Morocco shampoo 19.5 oz 4 pack", 24.99, 4, "OGX", "Shampoo & Conditioner"),
        ("Head & Shoulders Clinical 13.5 oz 3 pack", 21.99, 3, "Head & Shoulders", "Shampoo & Conditioner"),
        ("Garnier Fructis Grow Strong Shampoo Conditioner 22oz 2 pack", 9.99, 2, "Garnier", "Shampoo & Conditioner"),

        # === HEALTH & BEAUTY: Skin Care (14) ===
        ("CeraVe Moisturizing Cream 19oz 2 pack", 29.99, 2, "CeraVe", "Skin Care"),
        ("CeraVe SA Cleanser 16oz 2 pack", 24.99, 2, "CeraVe", "Skin Care"),
        ("CeraVe Hydrating Cleanser 16oz 2 pack", 22.99, 2, "CeraVe", "Skin Care"),
        ("Neutrogena Hydro Boost Gel Cream 1.7 oz 2 pack", 34.99, 2, "Neutrogena", "Skin Care"),
        ("Neutrogena Rapid Wrinkle Repair 2 pack", 39.99, 2, "Neutrogena", "Skin Care"),
        ("Olay Regenerist Cream 1.7 oz 2 pack", 39.99, 2, "Olay", "Skin Care"),
        ("Olay Total Effects 1.7 oz 2 pack", 29.99, 2, "Olay", "Skin Care"),
        ("RoC Retinol Correxion cream 1 oz 2 pack", 34.99, 2, "RoC", "Skin Care"),
        ("Eucerin Advanced Repair Lotion 16.9oz 3 pack", 19.99, 3, "Eucerin", "Skin Care"),
        ("Aveeno Daily Moisturizing Lotion 18oz 2 pack", 16.99, 2, "Aveeno", "Skin Care"),
        ("Cetaphil Moisturizing Lotion 16oz 2 pack", 19.99, 2, "Cetaphil", "Skin Care"),
        ("La Roche-Posay Toleriane Double Repair 2.5 oz 2 pack", 39.99, 2, "La Roche-Posay", "Skin Care"),
        ("The Ordinary Niacinamide 10% 1oz 3 pack", 19.99, 3, "The Ordinary", "Skin Care"),
        ("Paulas Choice 2% BHA Liquid Exfoliant 4 oz 2 pack", 34.99, 2, "Paula's Choice", "Skin Care"),

        # === HEALTH & BEAUTY: Oral Care (8) ===
        ("Crest 3D Whitestrips Professional Effects", 39.99, 1, "Crest", "Oral Care"),
        ("Crest Pro-Health Mouthwash 1L 4 pack", 19.99, 4, "Crest", "Oral Care"),
        ("Colgate Optic White toothpaste 4 pack", 14.99, 4, "Colgate", "Oral Care"),
        ("Colgate Total toothpaste 4.8 oz 4 pack", 12.99, 4, "Colgate", "Oral Care"),
        ("Listerine Cool Mint Mouthwash 1L 4 pack", 18.99, 4, "Listerine", "Oral Care"),
        ("Philips Sonicare replacement heads 8 pack", 29.99, 8, "Philips Sonicare", "Electric Toothbrush Heads"),
        ("Oral-B replacement heads 12 pack", 24.99, 12, "Oral-B", "Electric Toothbrush Heads"),
        ("Sensodyne Repair & Protect toothpaste 4 pack", 19.99, 4, "Sensodyne", "Oral Care"),

        # === HEALTH & BEAUTY: Bath & Body (6) ===
        ("Dove Beauty Bar 14 count", 12.99, 14, "Dove", "Bath & Body"),
        ("Dove Body Wash 24 oz 4 pack", 19.99, 4, "Dove", "Bath & Body"),
        ("Bath and Body Works Fine Fragrance Mist 8 oz 3 pack", 29.99, 3, "Bath & Body Works", "Fragrance"),
        ("Old Spice Body Wash 24 oz 4 pack", 18.99, 4, "Old Spice", "Bath & Body"),
        ("Method Body Wash 18 oz 6 pack", 24.99, 6, "Method", "Bath & Body"),
        ("Caress Body Wash 18 oz 4 pack", 14.99, 4, "Caress", "Bath & Body"),

        # === HEALTH & BEAUTY: Shaving (4) ===
        ("Gillette Fusion5 12 count blades", 32.99, 12, "Gillette", "Shaving & Hair Removal"),
        ("Gillette Mach3 15 count cartridges", 27.99, 15, "Gillette", "Shaving & Hair Removal"),
        ("Harrys 5-blade razor refills 12 count", 24.99, 12, "Harry's", "Shaving & Hair Removal"),
        ("Schick Hydro 5 12 count refill blades", 29.99, 12, "Schick", "Shaving & Hair Removal"),

        # === HOUSEHOLD: Cleaning (12) ===
        ("Lysol Disinfecting Wipes 6 pack", 14.99, 6, "Lysol", "Household Cleaning"),
        ("Clorox Disinfecting Wipes 6 pack", 12.99, 6, "Clorox", "Household Cleaning"),
        ("Clorox Bleach 121 oz 3 pack", 18.99, 3, "Clorox", "Household Cleaning"),
        ("Windex Glass Cleaner 23 oz 6 pack", 19.99, 6, "Windex", "Household Cleaning"),
        ("Method All-Purpose Cleaner 28 oz 6 pack", 21.99, 6, "Method", "Household Cleaning"),
        ("Mr. Clean Magic Eraser 10 count", 14.99, 10, "Mr. Clean", "Household Cleaning"),
        ("Simple Green All-Purpose Cleaner 1 gallon 2 pack", 19.99, 2, "Simple Green", "Household Cleaning"),
        ("Pine-Sol Multi-Surface Cleaner 144 oz 2 pack", 16.99, 2, "Pine-Sol", "Household Cleaning"),
        ("Lysol Toilet Bowl Cleaner 24 oz 4 pack", 14.99, 4, "Lysol", "Household Cleaning"),
        ("Scrubbing Bubbles Toilet Cleaner 20 oz 4 pack", 16.99, 4, "Scrubbing Bubbles", "Household Cleaning"),
        ("Febreze Air Freshener 8.8 oz 3 pack", 14.99, 3, "Febreze", "Air Fresheners"),
        ("Glade PlugIns Refills 10 count", 17.99, 10, "Glade", "Air Fresheners"),

        # === HOUSEHOLD: Laundry (6) ===
        ("Tide PODS 112 count", 19.99, 1, "Tide", "Laundry Detergent"),
        ("Tide Liquid Laundry Detergent 150 oz 2 pack", 24.99, 2, "Tide", "Laundry Detergent"),
        ("Persil ProClean 110 load 2 pack", 27.99, 2, "Persil", "Laundry Detergent"),
        ("Gain Flings 112 count", 17.99, 1, "Gain", "Laundry Detergent"),
        ("Downy Fabric Softener 140 oz 2 pack", 19.99, 2, "Downy", "Laundry Detergent"),
        ("Bounce Dryer Sheets 240 count 2 pack", 12.99, 2, "Bounce", "Laundry Detergent"),

        # === HOUSEHOLD: Paper & Plastic (8) ===
        ("Bounty Paper Towels 12 rolls", 24.99, 12, "Bounty", "Paper Towels"),
        ("Brawny Paper Towels 8 rolls", 14.99, 8, "Brawny", "Paper Towels"),
        ("Quilted Northern Toilet Paper 24 rolls", 29.99, 24, "Quilted Northern", "Toilet Paper"),
        ("Charmin Ultra Soft Toilet Paper 24 rolls", 27.99, 24, "Charmin", "Toilet Paper"),
        ("Kleenex Facial Tissue 8 pack", 14.99, 8, "Kleenex", "Facial Tissue"),
        ("Ziploc Freezer Bags Gallon 150 count", 14.99, 1, "Ziploc", "Storage & Organization"),
        ("Glad Trash Bags 13 gallon 120 count", 16.99, 120, "Glad", "Trash Bags"),
        ("Hefty Ultra Strong 13 gallon 100 count", 14.99, 100, "Hefty", "Trash Bags"),

        # === HOUSEHOLD: Kitchen (6) ===
        ("Glad Food Storage Containers 40 piece set", 19.99, 1, "Glad", "Food Storage"),
        ("Reynolds Wrap Aluminum Foil 200 sq ft 2 pack", 14.99, 2, "Reynolds", "Food Storage"),
        ("Saran Wrap 300 sq ft 2 pack", 12.99, 2, "Saran Wrap", "Food Storage"),
        ("Dawn Dish Soap 19.4 oz 6 pack", 19.99, 6, "Dawn", "Dish Soap"),
        ("Finish Quantum Dishwasher Tablets 82 count", 19.99, 82, "Finish", "Dishwasher Detergent"),
        ("Cascade Platinum Pods 62 count", 19.99, 62, "Cascade", "Dishwasher Detergent"),

        # === PET SUPPLIES (12) ===
        ("Frontline Plus for Dogs 6 doses", 49.99, 6, "Frontline", "Flea & Tick"),
        ("Frontline Gold for Dogs 6 doses", 59.99, 6, "Frontline", "Flea & Tick"),
        ("Advantage II for Cats 6 pack", 39.99, 6, "Advantage", "Flea & Tick"),
        ("Advantage Multi for Dogs 6 doses", 74.99, 6, "Advantage", "Flea & Tick"),
        ("Heartgard Plus for Dogs 6 count", 59.99, 6, "Heartgard", "Pet Medications"),
        ("NexGard Chewables for Dogs 6 pack", 99.99, 6, "NexGard", "Flea & Tick"),
        ("Sentinel Spectrum 6 pack Dogs", 54.99, 6, "Sentinel", "Pet Medications"),
        ("Greenies Dental Chews Regular 36 count", 29.99, 36, "Greenies", "Dog Treats"),
        ("Milk-Bone Original Dog Treats 10 lb", 19.99, 1, "Milk-Bone", "Dog Treats"),
        ("Blue Buffalo Life Protection 30lb", 54.99, 1, "Blue Buffalo", "Dog Food"),
        ("Purina Pro Plan 35lb dog food", 59.99, 1, "Purina Pro Plan", "Dog Food"),
        ("Temptations Cat Treats 30 oz", 14.99, 1, "Temptations", "Cat Treats"),

        # === PET SUPPLIES: Cat Litter (2) ===
        ("Tidy Cats Clumping Litter 20 lb 2 pack", 19.99, 2, "Tidy Cats", "Cat Litter"),
        ("Arm & Hammer Clump & Seal 40 lb", 24.99, 1, "Arm & Hammer", "Cat Litter"),

        # === SUPPLEMENTS & VITAMINS (10) ===
        ("Nature Made Vitamin D3 2000 IU 250 ct", 12.99, 1, "Nature Made", "Vitamins"),
        ("Nature Made Vitamin C 1000mg 300 ct", 14.99, 1, "Nature Made", "Vitamins"),
        ("Vital Proteins Collagen Peptides 24oz", 29.99, 1, "Vital Proteins", "Supplements"),
        ("Optimum Nutrition Gold Standard Whey 5lb", 54.99, 1, "Optimum Nutrition", "Protein"),
        ("Omega 3 Fish Oil 240 softgels", 19.99, 1, "Nature's Bounty", "Vitamins"),
        ("Garden of Life Vitamin Code 120 ct", 29.99, 1, "Garden of Life", "Vitamins"),
        ("Turmeric Curcumin with Ginger 180 ct", 14.99, 1, "Nature Made", "Supplements"),
        ("Magnesium Citrate 200 mg 300 tablets", 12.99, 1, "Nature's Bounty", "Vitamins"),
        ("Melatonin 5 mg 300 tablets", 9.99, 1, "Natrol", "Supplements"),
        ("Liquid IV Hydration Multiplier 30 pack", 22.99, 1, "Liquid IV", "Sports Nutrition"),

        # === SMOKING CESSATION (4) ===
        ("Nicotine Lozenge 2mg 216 count", 29.99, 216, "GoodSense", "Smoking Cessation"),
        ("Nicotine Lozenge 4mg 216 count", 34.99, 216, "GoodSense", "Smoking Cessation"),
        ("Nicorette Gum 4mg 170 count", 49.99, 170, "Nicorette", "Smoking Cessation"),
        ("Nicorette Gum 2mg 170 count", 39.99, 170, "Nicorette", "Smoking Cessation"),

        # === KITCHEN & DINING (4) ===
        ("Brita Water Filter Pitcher 10 cup", 29.99, 1, "Brita", "Water Filters"),
        ("Brita Replacement Filters 10 pack", 34.99, 10, "Brita", "Water Filters"),
        ("Pyrex Food Storage 18 piece set", 24.99, 1, "Pyrex", "Food Storage"),
        ("OXO Good Grips 15 piece set", 39.99, 1, "OXO", "Kitchen Tools"),

        # === BABY & KIDS (4) ===
        ("Pampers Swaddlers Size 2 186 count", 39.99, 186, "Pampers", "Diapers"),
        ("Huggies Little Snugglers Size 2 186 ct", 37.99, 186, "Huggies", "Diapers"),
        ("Baby Dove Tip to Toe Wash 13 oz 4 pack", 19.99, 4, "Baby Dove", "Baby Care"),
        ("Johnson's Baby Shampoo 20 oz 3 pack", 16.99, 3, "Johnson's", "Baby Care"),

        # === OFFICE & SCHOOL (4) ===
        ("Paper Mate InkJoy Pens 60 count", 14.99, 60, "Paper Mate", "Office Supplies"),
        ("Post-it Notes 12 pack", 16.99, 12, "Post-it", "Office Supplies"),
        ("Bic Round Stic Pens 60 count", 9.99, 60, "Bic", "Office Supplies"),
        ("Sharpie Permanent Markers 30 count", 19.99, 30, "Sharpie", "Office Supplies"),

        # === AUTOMOTIVE (4) ===
        ("Cabin Air Filter 2 pack", 9.99, 2, "EPAuto", "Automotive"),
        ("Windshield Wipers 26/18 inch set", 19.99, 2, "Michelin", "Automotive"),
        ("Castrol Edge 5W-30 Motor Oil 5 quart", 27.99, 1, "Castrol", "Automotive"),
        ("Meguiar's Gold Class Car Wash 64 oz 2 pack", 19.99, 2, "Meguiar's", "Automotive"),

        # === ELECTRONICS ACCESSORIES (4) ===
        ("Amazon Basics AA Batteries 48 pack", 14.99, 48, "Amazon Basics", "Batteries"),
        ("Duracell AA Batteries 24 count", 16.99, 24, "Duracell", "Batteries"),
        ("Energizer AAA Batteries 24 count", 14.99, 24, "Energizer", "Batteries"),
        ("Anker PowerCore 10000 Power Bank 2 pack", 29.99, 2, "Anker", "Electronics"),
    ]

    results = []
    for kw, src_price, src_size, brand, cat in SCAN_KEYWORDS:
        # Filter by category
        if category and category != "all" and cat.lower() != category.lower():
            continue
        # Filter by search keyword
        if search:
            q = search.lower()
            if (
                q not in kw.lower()
                and q not in brand.lower()
                and q not in cat.lower()
            ):
                continue
        try:
            items = await search_items(keyword=kw, limit=20, sort="price")
            if not items:
                continue
            
            prices = sorted([
                extract_listing_price(i) for i in items if extract_listing_price(i) > 0
            ])
            if not prices:
                continue
            
            median_price = prices[len(prices)//2]

            # Whole-pack economics (honest, defensible):
            # Buy the source pack, resell the same pack as-is on eBay.
            # This avoids the false "split each unit at the whole-pack price" bug.
            revenue = median_price
            fees = revenue * 0.13          # eBay final value fee
            payment = revenue * 0.03 + 0.30  # payment processing fee
            shipping_est = 5.0
            cost = src_price
            net_profit_full = revenue - cost - fees - payment - shipping_est

            # Also evaluate a split option only where it's realistic:
            # sell the pack split into sell_size chunks, each at a per-chunk
            # price estimated from median (only if the per-unit is sensible).
            # Cap split listings to avoid absurd per-unit multiplication.
            # For safety, use splitting only when it improves profit meaningfully.
            best = None
            split_candidates = []
            candidate_sizes = [s for s in [2, 3, 4, 6] if src_size % s == 0 and src_size // s <= 20]
            for s in candidate_sizes:
                chunk_price = median_price / (src_size // s)  # pro-rate pack value
                chunk_cost = src_price / (src_size // s)
                chunk_fees = chunk_price * 0.13
                chunk_payment = chunk_price * 0.03 + 0.30
                chunk_shipping = 4.0
                chunk_net = chunk_price - chunk_cost - chunk_fees - chunk_payment - chunk_shipping
                num_chunks = src_size // s
                split_candidates.append((s, num_chunks, chunk_net * num_chunks))
            best_split = max(split_candidates, key=lambda x: x[2], default=None) if split_candidates else None

            # Choose the better: whole-pack vs best realistic split
            if best_split and best_split[2] > net_profit_full:
                sell_size = best_split[0]
                num_listings = best_split[1]
                net_profit = best_split[2]
                profit_per_listing = best_split[2] / num_listings if num_listings else 0
                roi = (best_split[2] / src_price * 100) if src_price else 0
                margin = (net_profit / revenue * 100) if revenue else 0
                sell_price = (median_price / num_listings)
                break_even = src_price / num_listings
            else:
                sell_size = src_size
                num_listings = 1
                net_profit = net_profit_full
                profit_per_listing = net_profit_full
                roi = (net_profit_full / cost * 100) if cost else 0
                margin = (net_profit_full / revenue * 100) if revenue else 0
                sell_price = median_price
                break_even = cost

            # Skip if below min profit threshold
            if net_profit < min_profit:
                continue

            results.append({
                "keyword": kw,
                "brand": brand,
                "category": cat,
                "ebay_listings": len(prices),
                "ebay_median_price": median_price,
                "ebay_low_price": prices[0],
                "ebay_high_price": prices[-1],
                "source_price": src_price,
                "source_size": src_size,
                "cost_per_unit": src_price / src_size,
                "best_sell_size": sell_size,
                "listings_per_pack": num_listings,
                "net_profit": net_profit,
                "profit_per_listing": profit_per_listing,
                "roi": roi,
                "margin": margin,
                "sell_price": sell_price,
                "break_even": break_even,
                "leftover_units": 0,
            })
        except Exception:
            continue

    # Sort
    reverse = sort_dir == "desc"
    sort_key = sort_by
    results.sort(key=lambda x: x.get(sort_key, 0), reverse=reverse)

    total = len(results)

    # Paginate
    if per_page > 0:
        start = (page - 1) * per_page
        end = start + per_page
        paginated = results[start:end]
    else:
        paginated = results

    # Get all unique categories for filter sidebar
    all_categories = sorted(set(kw[4] for kw in SCAN_KEYWORDS))

    return {
        "success": True,
        "total_scanned": len(SCAN_KEYWORDS),
        "total": total,
        "qualifying": total,
        "min_profit_threshold": min_profit,
        "page": page,
        "per_page": per_page if per_page > 0 else total,
        "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 1,
        "categories": all_categories,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "opportunities": paginated,
    }
