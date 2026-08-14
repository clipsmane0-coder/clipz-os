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


@router.get("/scan")
async def api_scan(
    category: Optional[str] = None,
    min_profit: float = 40,
    max_results: int = 10,
):
    """
    Scan for opportunities across preset product lists.
    Returns all qualifying opportunities sorted by net profit.
    """
    from .ebay_browse import search_items, extract_listing_price
    from .engine import analyze_all_configs

    # Curated keyword list for batch scanning (source_price = typical Amazon/Costco multipack price)
    SCAN_KEYWORDS = [
        # Health & Beauty
        ("Kirkland Minoxidil 5% 6 month", 29.99, 6, "Kirkland", "Hair Loss Treatments"),
        ("Crest 3D Whitestrips Professional Effects", 39.99, 2, "Crest", "Oral Care"),
        ("Dove Beauty Bar 14 count", 12.99, 14, "Dove", "Bath & Body"),
        ("Gillette Fusion5 12 count blades", 32.99, 12, "Gillette", "Shaving & Hair Removal"),
        ("Colgate Optic White 4 pack toothpaste", 14.99, 4, "Colgate", "Oral Care"),
        ("Neutrogena Hydro Boost Gel Cream 2 pack", 19.99, 2, "Neutrogena", "Skin Care"),
        ("Olay Regenerist Cream 2 pack", 29.99, 2, "Olay", "Skin Care"),
        # Household
        ("Lysol Disinfecting Wipes 6 pack", 14.99, 6, "Lysol", "Household Supplies"),
        ("Clorox Disinfecting Wipes 6 pack", 12.99, 6, "Clorox", "Household Supplies"),
        ("Bounty Paper Towels 12 rolls", 24.99, 12, "Bounty", "Paper Towels"),
        ("Tide PODS 112 count", 19.99, 1, "Tide", "Laundry Detergent"),
        ("Ziploc Freezer Bags Gallon 150 ct", 14.99, 1, "Ziploc", "Storage & Organization"),
        # Pet Supplies
        ("Frontline Plus for Dogs 6 doses", 49.99, 6, "Frontline", "Flea & Tick"),
        ("Greenies Dental Chews Regular 36 ct", 29.99, 36, "Greenies", "Dog Treats"),
        ("Advantage II for Cats 6 pack", 39.99, 6, "Advantage", "Flea & Tick"),
        # Supplements
        ("Nature Made Vitamin D3 2000 IU 250 ct", 12.99, 1, "Nature Made", "Vitamins"),
        ("Vital Proteins Collagen Peptides 24oz", 29.99, 1, "Vital Proteins", "Supplements"),
        ("Optimum Nutrition Gold Standard Whey 5lb", 54.99, 1, "Optimum Nutrition", "Protein"),
        ("Omega 3 fish oil 240 softgels", 19.99, 1, "Generic", "Vitamins"),
        ("Liquid IV Hydration Multiplier 30 pack", 22.99, 1, "Liquid IV", "Sports Nutrition"),
        # Nicotine
        ("Nicotine Lozenge 2mg 216 count", 29.99, 216, "Generic", "Smoking Cessation"),
        ("Nicorette Gum 4mg 170 count", 39.99, 170, "Nicorette", "Smoking Cessation"),
        # Personal care
        ("Philips Sonicare replacement heads 8 pack", 29.99, 8, "Philips", "Electric Toothbrush Heads"),
        ("Brita water filters 10 pack", 29.99, 10, "Brita", "Water Filters"),
    ]

    results = []
    for kw, src_price, src_size, brand, cat in SCAN_KEYWORDS:
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
            
            configs, best = analyze_all_configs(
                src_price, src_size, {1: median_price}, shipping_cost=5.0
            )
            
            if best.net_profit >= min_profit:
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
                    "best_sell_size": best.sell_units,
                    "listings_per_pack": best.number_of_listings,
                    "net_profit": best.net_profit,
                    "profit_per_listing": best.profit_per_listing,
                    "roi": best.roi,
                    "margin": best.margin,
                    "sell_price": best.total_revenue / best.number_of_listings if best.number_of_listings > 0 else 0,
                    "break_even": best.break_even_sell_price,
                    "leftover_units": best.leftover_units,
                })
        except Exception:
            continue

    # Sort by net profit descending
    results.sort(key=lambda x: x["net_profit"], reverse=True)

    return {
        "success": True,
        "total_scanned": len(SCAN_KEYWORDS),
        "qualifying": len(results),
        "min_profit_threshold": min_profit,
        "opportunities": results[:max_results] if max_results > 0 else results,
    }
