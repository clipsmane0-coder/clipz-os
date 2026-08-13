"""
ArbSense Multipack Arbitrage Analysis Engine
Core profit calculations, configuration analysis, and listing generation
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math

# ---- Fee structure constants ----
EBAY_FINAL_VALUE_FEE = 0.13      # 13% for most categories
EBAY_INSERTION_FEE = 0.30       # per listing (after 250 free)
PAYMENT_FEE_PERCENT = 0.029     # 2.9%
PAYMENT_FEE_FIXED = 0.30        # $0.30 per transaction
SHIPPING_ESTIMATE_DEFAULT = 4.99 # default small package
RETURN_RESERVE = 0.02           # 2% for returns
AD_SPEND = 0.05                 # 5% promoted listings
MATERIALS_COST = 0.50           # packing materials per order


@dataclass
class ProfitConfig:
    """Profit analysis for a single pack-break configuration."""
    pack_units: int
    sell_units: int
    number_of_listings: int
    leftover_units: int
    source_cost: float
    total_revenue: float
    ebay_fees: float
    payment_fees: float
    shipping_cost: float
    return_reserve: float
    ad_spend: float
    materials_cost: float
    total_cost: float
    net_profit: float
    profit_per_unit: float
    profit_per_listing: float
    roi: float
    margin: float
    break_even_sell_price: float
    cost_per_unit: float
    revenue_per_unit: float


@dataclass
class ListingDraft:
    title: str
    description: str
    category: str
    condition: str
    brand: str
    model: Optional[str]
    price: float
    quantity: int
    format: str
    shipping: str
    handling_time: str
    item_specifics: Dict[str, str]
    image_requirements: str


@dataclass
class Opportunity:
    id: str
    product_name: str
    brand: str
    category: str = "Health & Beauty"
    source_url: Optional[str] = None
    ebay_comp_url: Optional[str] = None
    source_pack_price: float = 0.0
    source_pack_size: int = 0
    cost_per_unit: float = 0.0
    ebay_sell_price: float = 0.0
    ebay_sell_size: int = 1
    best_config: Optional[ProfitConfig] = None
    all_configs: List[ProfitConfig] = field(default_factory=list)
    velocity: Dict = field(default_factory=dict)
    confidence: int = 0
    risk_factors: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, approved, rejected
    listing: Optional[ListingDraft] = None


def calculate_profit(
    source_pack_price: float,
    source_pack_size: int,
    sell_price: float,
    sell_size: int,
    shipping_cost: Optional[float] = None,
    include_ad_spend: bool = True,
    include_materials: bool = True,
) -> ProfitConfig:
    """Calculate full profit breakdown for one pack-break configuration."""
    cost_per_unit = source_pack_price / source_pack_size
    number_of_listings = source_pack_size // sell_size
    leftover_units = source_pack_size % sell_size

    cost_per_listing = cost_per_unit * sell_size
    revenue_per_listing = sell_price

    total_revenue = revenue_per_listing * number_of_listings
    total_source_cost = number_of_listings * cost_per_listing

    ebay_fees = (
        total_revenue * EBAY_FINAL_VALUE_FEE +
        number_of_listings * EBAY_INSERTION_FEE
    )
    payment_fees = total_revenue * PAYMENT_FEE_PERCENT + number_of_listings * PAYMENT_FEE_FIXED
    ship_cost = (shipping_cost or SHIPPING_ESTIMATE_DEFAULT) * number_of_listings
    return_reserve = total_revenue * RETURN_RESERVE
    ad_cost = total_revenue * AD_SPEND if include_ad_spend else 0
    materials = MATERIALS_COST * number_of_listings if include_materials else 0

    total_cost = (
        total_source_cost + ebay_fees + payment_fees + ship_cost +
        return_reserve + ad_cost + materials
    )

    net_profit = total_revenue - total_cost
    profit_per_unit = net_profit / (number_of_listings * sell_size) if number_of_listings > 0 else 0
    profit_per_listing = net_profit / number_of_listings if number_of_listings > 0 else 0
    roi = (net_profit / total_source_cost * 100) if total_source_cost > 0 else 0
    margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

    # Break-even sell price per listing
    # revenue - fees - payment - shipping - returns - ads - materials - source = 0
    # N * p * (1 - 0.13 - 0.029 - 0.02 - ad_pct) - N*(0.30 + 0.30 + shipping + materials) - source_cost = 0
    ad_pct = AD_SPEND if include_ad_spend else 0
    N = number_of_listings
    if N <= 0:
        break_even = 0
    else:
        fixed_per_listing = (
            EBAY_INSERTION_FEE + PAYMENT_FEE_FIXED +
            (shipping_cost or SHIPPING_ESTIMATE_DEFAULT) +
            (MATERIALS_COST if include_materials else 0)
        )
        variable_rev_ratio = 1 - EBAY_FINAL_VALUE_FEE - PAYMENT_FEE_PERCENT - RETURN_RESERVE - ad_pct
        total_fixed = N * fixed_per_listing + total_source_cost
        break_even = total_fixed / (N * variable_rev_ratio) if variable_rev_ratio > 0 else 0

    return ProfitConfig(
        pack_units=source_pack_size,
        sell_units=sell_size,
        number_of_listings=number_of_listings,
        leftover_units=leftover_units,
        source_cost=total_source_cost,
        total_revenue=total_revenue,
        ebay_fees=ebay_fees,
        payment_fees=payment_fees,
        shipping_cost=ship_cost,
        return_reserve=return_reserve,
        ad_spend=ad_cost,
        materials_cost=materials,
        total_cost=total_cost,
        net_profit=net_profit,
        profit_per_unit=profit_per_unit,
        profit_per_listing=profit_per_listing,
        roi=roi,
        margin=margin,
        break_even_sell_price=break_even,
        cost_per_unit=cost_per_unit,
        revenue_per_unit=sell_price / sell_size,
    )


def analyze_all_configs(
    source_pack_price: float,
    source_pack_size: int,
    ebay_prices: Dict[int, float],
    shipping_cost: Optional[float] = None,
) -> Tuple[List[ProfitConfig], ProfitConfig]:
    """
    Analyze all valid pack-break configurations.
    ebay_prices: dict of {sell_size: sell_price}
    Returns (all_configs_sorted, best_config)
    """
    sell_sizes = [1, 2, 3, 4, 6, 8, 12]
    configs: List[ProfitConfig] = []

    for sell_size in sell_sizes:
        if sell_size > source_pack_size:
            continue
        if sell_size not in ebay_prices:
            continue
        # Skip if pack doesn't break evenly AND the leftover is significant
        leftover = source_pack_size % sell_size
        leftover_pct = leftover / source_pack_size
        if leftover_pct > 0.25 and sell_size != source_pack_size:
            continue

        config = calculate_profit(
            source_pack_price, source_pack_size,
            ebay_prices[sell_size], sell_size,
            shipping_cost=shipping_cost,
        )
        configs.append(config)

    configs.sort(key=lambda c: c.net_profit, reverse=True)

    if not configs:
        zero_config = ProfitConfig(
            pack_units=source_pack_size,
            sell_units=1,
            number_of_listings=source_pack_size,
            leftover_units=0,
            source_cost=source_pack_price,
            total_revenue=0,
            ebay_fees=0,
            payment_fees=0,
            shipping_cost=0,
            return_reserve=0,
            ad_spend=0,
            materials_cost=0,
            total_cost=source_pack_price,
            net_profit=-source_pack_price,
            profit_per_unit=-source_pack_price/source_pack_size,
            profit_per_listing=-source_pack_price/source_pack_size,
            roi=-100,
            margin=-100,
            break_even_sell_price=0,
            cost_per_unit=source_pack_price/source_pack_size,
            revenue_per_unit=0,
        )
        return [], zero_config

    return configs, configs[0]


def generate_listing(
    product_name: str,
    brand: str,
    sell_size: int,
    sell_price: float,
    category: str = "Health & Beauty",
) -> ListingDraft:
    """Generate an optimized eBay listing draft."""
    size_text = "" if sell_size == 1 else f"{sell_size} Pack "
    unit_word = "Count" if sell_size == 1 else "Pack"

    # Build 80-char optimized title
    title_parts = [
        f"{brand}",
        f"{product_name}",
        f"{size_text}{unit_word}",
        "- New Sealed",
        "- Free Shipping",
    ]
    title = " ".join(title_parts)
    if len(title) > 80:
        title = title[:77] + "..."

    description = f"""
{brand} {product_name} - {sell_size} {unit_word if sell_size == 1 else 'Pack'}

Condition: Brand new, factory sealed. Authentic {brand} product.

Quantity: {sell_size} {'unit' if sell_size == 1 else 'units per pack'}

Features:
• Authentic {brand} product
• Factory sealed packaging
• Fast shipping within 1 business day
• Free shipping on this listing

{'This listing is for a single unit.' if sell_size == 1 else f'This listing is for a {sell_size}-pack.'}

Please see photos for exact product condition and details. Items ship from the USA.
    """.strip()

    specifics = {
        "Brand": brand,
        "Condition": "New",
        "Quantity": str(sell_size),
        "Type": "Dietary Supplement",
        "Formulation": "Softgel",
    }

    return ListingDraft(
        title=title,
        description=description,
        category=category,
        condition="New",
        brand=brand,
        model=None,
        price=round(sell_price, 2),
        quantity=sell_size,
        format="Buy It Now",
        shipping="Free shipping",
        handling_time="1 business day",
        item_specifics=specifics,
        image_requirements=(
            "Need: product front shot, packaging shot, label/ingredients shot. "
            "Use manufacturer product photos (fair use for listings) or your own photos."
        ),
    )


def score_opportunity(
    best_config: ProfitConfig,
    velocity: dict,
) -> Tuple[int, List[str]]:
    """Score an opportunity 0-100 and return risk factors."""
    score = 0
    risk_factors: List[str] = []

    # Profit score (max 40)
    if best_config.net_profit >= 100:
        score += 40
    elif best_config.net_profit >= 60:
        score += 32
    elif best_config.net_profit >= 40:
        score += 25
    elif best_config.net_profit >= 20:
        score += 12
    elif best_config.net_profit > 0:
        score += 5
    else:
        risk_factors.append("Unprofitable")

    if best_config.net_profit < 40:
        risk_factors.append("Below $40 minimum profit threshold")

    # ROI score (max 20)
    if best_config.roi >= 100:
        score += 20
    elif best_config.roi >= 50:
        score += 15
    elif best_config.roi >= 30:
        score += 10
    elif best_config.roi >= 15:
        score += 5

    if best_config.roi < 20:
        risk_factors.append(f"Low ROI ({best_config.roi:.1f}%)")

    # Velocity score (max 25)
    est_sales = velocity.get("estimated_monthly_sales", 0)
    vel_conf = velocity.get("confidence", "low")

    if vel_conf == "high" and est_sales > 50:
        score += 25
    elif vel_conf == "high" or est_sales > 30:
        score += 20
    elif vel_conf == "medium" or est_sales > 10:
        score += 12
    elif est_sales > 5:
        score += 6

    if vel_conf == "low":
        risk_factors.append("Low velocity confidence")
    if est_sales < 10:
        risk_factors.append("Low estimated sales volume")

    # Margin score (max 15)
    if best_config.margin >= 30:
        score += 15
    elif best_config.margin >= 20:
        score += 10
    elif best_config.margin >= 10:
        score += 5

    # Leftover units penalty
    if best_config.leftover_units > 0:
        leftover_pct = best_config.leftover_units / best_config.pack_units
        if leftover_pct > 0.1:
            score -= 5
            risk_factors.append(f"{best_config.leftover_units} leftover units from pack")

    return min(100, max(0, score)), risk_factors


def format_analysis_report(
    product_name: str,
    brand: str,
    source_pack_price: float,
    source_pack_size: int,
    best_config: ProfitConfig,
    all_configs: List[ProfitConfig],
    velocity: dict,
    score: int,
    risk_factors: List[str],
) -> str:
    """Format a human-readable analysis report."""
    lines = []
    lines.append(f"=== ARBSENSE ANALYSIS: {brand} {product_name} ===")
    lines.append("")
    lines.append("SOURCE:")
    lines.append(f"  Pack size: {source_pack_size} units")
    lines.append(f"  Pack price: ${source_pack_price:.2f}")
    lines.append(f"  Cost per unit: ${source_pack_price / source_pack_size:.2f}")
    lines.append("")
    lines.append(f"BEST CONFIGURATION: {best_config.sell_units}-pack @ ${best_config.total_revenue / best_config.number_of_listings:.2f}")
    lines.append(f"  Listings per pack: {best_config.number_of_listings}")
    lines.append(f"  Leftover units: {best_config.leftover_units}")
    lines.append(f"  Net profit: ${best_config.net_profit:.2f}")
    lines.append(f"  Profit per listing: ${best_config.profit_per_listing:.2f}")
    lines.append(f"  ROI: {best_config.roi:.1f}%")
    lines.append(f"  Margin: {best_config.margin:.1f}%")
    lines.append(f"  Break-even price: ${best_config.break_even_sell_price:.2f}")
    lines.append("")
    lines.append("DETAILED COST BREAKDOWN (per source pack):")
    lines.append(f"  Total revenue: ${best_config.total_revenue:.2f}")
    lines.append(f"  Source cost: ${best_config.source_cost:.2f}")
    lines.append(f"  eBay fees: ${best_config.ebay_fees:.2f}")
    lines.append(f"  Payment fees: ${best_config.payment_fees:.2f}")
    lines.append(f"  Shipping: ${best_config.shipping_cost:.2f}")
    lines.append(f"  Return reserve (2%): ${best_config.return_reserve:.2f}")
    lines.append(f"  Ad spend (5%): ${best_config.ad_spend:.2f}")
    lines.append(f"  Materials: ${best_config.materials_cost:.2f}")
    lines.append(f"  Total cost: ${best_config.total_cost:.2f}")
    lines.append("")

    if all_configs:
        lines.append("ALL CONFIGURATIONS:")
        lines.append(f"  {'Size':<6} {'Price':<10} {'Listings':<10} {'Profit':<10} {'ROI':<8}")
        for cfg in all_configs:
            price = cfg.total_revenue / cfg.number_of_listings if cfg.number_of_listings > 0 else 0
            lines.append(
                f"  {cfg.sell_units}-pack  ${price:<8.2f} {cfg.number_of_listings:<10} "
                f"${cfg.net_profit:<8.2f} {cfg.roi:<7.1f}%"
            )
        lines.append("")

    lines.append(f"VELOCITY:")
    lines.append(f"  Est. monthly sales: {velocity.get('estimated_monthly_sales', 0)}")
    lines.append(f"  Confidence: {velocity.get('confidence', 'low')}")
    lines.append(f"  Sold items in sample: {velocity.get('sold_items_count', 0)}")
    lines.append("")

    lines.append(f"OVERALL SCORE: {score}/100")
    if risk_factors:
        lines.append("RISK FACTORS:")
        for rf in risk_factors:
            lines.append(f"  • {rf}")
    lines.append("")

    verdict = "APPROVE" if best_config.net_profit >= 40 and score >= 50 else "REJECT"
    lines.append(f"VERDICT: {verdict}")
    if best_config.net_profit < 40:
        lines.append(f"  Reason: Net profit ${best_config.net_profit:.2f} is below $40 minimum")

    return "\n".join(lines)
