"""
ArbSense API Routes
eBay multipack arbitrage discovery and analysis
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

from .ebay_client import ebay_search, HIGH_POTENTIAL_CATEGORIES
from .ebay_test import test_all_endpoints
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


@router.get("/scan")
async def api_scan(
    category: Optional[str] = None,
    min_profit: float = 40,
    max_results: int = 10,
):
    """
    Scan for opportunities in a category.
    NOTE: This is a discovery stub. Full automated scanning requires
    Amazon price data integration. Use /ebay/search + /analyze for manual analysis.
    """
    # This is the entry point for full automated scanning.
    # For now it returns high-potential search terms and structure.
    categories_to_scan = []
    if category and category in HIGH_POTENTIAL_CATEGORIES:
        categories_to_scan = [category]
    else:
        categories_to_scan = list(HIGH_POTENTIAL_CATEGORIES.keys())[:3]

    return {
        "success": True,
        "status": "discovery_initiated",
        "scanning_categories": categories_to_scan,
        "note": (
            "Automated cross-marketplace scanning requires both eBay AND Amazon "
            "price data. Use /ebay/search to find products, then /analyze with "
            "source prices for full analysis."
        ),
        "next_steps": [
            "1. Search eBay for products with high sold counts",
            "2. Find corresponding Amazon multipack source price",
            "3. Call /analyze with both eBay and source prices",
            "4. Review results and approve/reject",
        ],
    }
