"""
ArbSense Multipack Product Catalog

Curated list of true multipack products (individually packaged units)
with direct links to Temu, Amazon, and eBay for manual price verification.

No paid APIs, no scraping — just product data and links.
All prices are ESTIMATES, clearly marked as UNVERIFIED.
"""

# Each entry:
# {
#   id, title, category, pack_size,
#   temu_search_query, amazon_search_query, ebay_search_query,
#   est_source_price_low, est_source_price_high,   # whole pack
#   est_ebay_single_low, est_ebay_single_high,     # per unit
#   multipack_confidence: "high"|"medium"|"low",
#   notes
# }

MULTIPACK_CATALOG = [
    # ========================================================================
    # Smart Home
    # ========================================================================
    {
        "id": "MP-001",
        "title": "Smart WiFi Plug (15A, No Hub)",
        "category": "Smart Home",
        "pack_size": 5,
        "temu_search_query": "smart wifi plug 5 pack 15A",
        "amazon_search_query": "smart plug wifi 5 pack 15A no hub",
        "ebay_search_query": "smart plug wifi 15A single new",
        "est_source_price_low": 9.00,
        "est_source_price_high": 18.00,
        "est_ebay_single_low": 12.00,
        "est_ebay_single_high": 25.00,
        "multipack_confidence": "high",
        "notes": "Each plug individually boxed inside the pack. Very high eBay demand. Temu prices vary widely.",
    },
    {
        "id": "MP-002",
        "title": "Smart WiFi Plug Mini (10A)",
        "category": "Smart Home",
        "pack_size": 4,
        "temu_search_query": "mini smart plug wifi 4 pack",
        "amazon_search_query": "mini smart plug wifi 4 pack alexa",
        "ebay_search_query": "mini smart plug wifi single alexa",
        "est_source_price_low": 7.00,
        "est_source_price_high": 15.00,
        "est_ebay_single_low": 10.00,
        "est_ebay_single_high": 20.00,
        "multipack_confidence": "high",
        "notes": "Compact size, high turnover. Many brands on Temu.",
    },
    {
        "id": "MP-003",
        "title": "Smart LED Light Bulb (E26, WiFi)",
        "category": "Smart Home",
        "pack_size": 4,
        "temu_search_query": "smart light bulb wifi 4 pack e26 alexa",
        "amazon_search_query": "smart light bulb wifi 4 pack e26 alexa color",
        "ebay_search_query": "smart light bulb wifi e26 single new",
        "est_source_price_low": 10.00,
        "est_source_price_high": 20.00,
        "est_ebay_single_low": 10.00,
        "est_ebay_single_high": 22.00,
        "multipack_confidence": "medium",
        "notes": "Each bulb individually packaged. Quality varies widely on Temu.",
    },
    {
        "id": "MP-004",
        "title": "Smart Light Switch (WiFi, Single Pole)",
        "category": "Smart Home",
        "pack_size": 2,
        "temu_search_query": "smart light switch wifi 2 pack alexa",
        "amazon_search_query": "smart light switch wifi 2 pack single pole alexa",
        "ebay_search_query": "smart light switch wifi single pole alexa",
        "est_source_price_low": 14.00,
        "est_source_price_high": 25.00,
        "est_ebay_single_low": 18.00,
        "est_ebay_single_high": 35.00,
        "multipack_confidence": "medium",
        "notes": "Higher ticket = better per-unit margin. Verify UL listing on Temu products.",
    },
    {
        "id": "MP-005",
        "title": "Smart Outdoor Plug (WiFi, Waterproof)",
        "category": "Smart Home",
        "pack_size": 2,
        "temu_search_query": "smart outdoor plug wifi waterproof 2 pack",
        "amazon_search_query": "smart outdoor plug wifi 2 pack waterproof alexa",
        "ebay_search_query": "smart outdoor plug wifi waterproof single",
        "est_source_price_low": 12.00,
        "est_source_price_high": 22.00,
        "est_ebay_single_low": 15.00,
        "est_ebay_single_high": 30.00,
        "multipack_confidence": "medium",
        "notes": "Seasonal demand. Higher returns for quality issues.",
    },

    # ========================================================================
    # Audio / Tech Accessories
    # ========================================================================
    {
        "id": "MP-006",
        "title": "Wireless Earbuds TWS (Bluetooth 5.x)",
        "category": "Audio",
        "pack_size": 2,
        "temu_search_query": "wireless earbuds TWS 2 pack bluetooth",
        "amazon_search_query": "wireless earbuds bluetooth 2 pack",
        "ebay_search_query": "wireless earbuds bluetooth new pair",
        "est_source_price_low": 6.00,
        "est_source_price_high": 14.00,
        "est_ebay_single_low": 12.00,
        "est_ebay_single_high": 25.00,
        "multipack_confidence": "high",
        "notes": "Each pair in own retail box. Massive eBay volume. Very competitive.",
    },
    {
        "id": "MP-007",
        "title": "Portable Bluetooth Speaker (Waterproof)",
        "category": "Audio",
        "pack_size": 2,
        "temu_search_query": "portable bluetooth speaker waterproof 2 pack",
        "amazon_search_query": "portable bluetooth speaker waterproof 2 pack",
        "ebay_search_query": "portable bluetooth speaker waterproof single",
        "est_source_price_low": 10.00,
        "est_source_price_high": 20.00,
        "est_ebay_single_low": 15.00,
        "est_ebay_single_high": 35.00,
        "multipack_confidence": "medium",
        "notes": "Higher per-unit value. Quality varies significantly.",
    },
    {
        "id": "MP-008",
        "title": "Magnetic Wireless Charger (MagSafe compatible)",
        "category": "Tech Accessories",
        "pack_size": 2,
        "temu_search_query": "magnetic wireless charger magsafe 2 pack 15W",
        "amazon_search_query": "magnetic wireless charger magsafe 2 pack iphone",
        "ebay_search_query": "magnetic wireless charger magsafe 15W single",
        "est_source_price_low": 8.00,
        "est_source_price_high": 16.00,
        "est_ebay_single_low": 10.00,
        "est_ebay_single_high": 20.00,
        "multipack_confidence": "high",
        "notes": "Each charger individually packaged. iPhone 12+ compatible. High demand.",
    },
    {
        "id": "MP-009",
        "title": "USB-C Fast Charger (20W PD)",
        "category": "Tech Accessories",
        "pack_size": 4,
        "temu_search_query": "USB C charger 20W PD 4 pack",
        "amazon_search_query": "USB C charger 20W PD 4 pack type c",
        "ebay_search_query": "USB C charger 20W PD single new",
        "est_source_price_low": 6.00,
        "est_source_price_high": 12.00,
        "est_ebay_single_low": 6.00,
        "est_ebay_single_high": 14.00,
        "multipack_confidence": "high",
        "notes": "Commodity item. High volume, low margin. Very competitive on eBay.",
    },
    {
        "id": "MP-010",
        "title": "USB-C to USB-C Cable (6ft, 60W)",
        "category": "Tech Accessories",
        "pack_size": 5,
        "temu_search_query": "USB C cable 6ft 5 pack type c 60W braided",
        "amazon_search_query": "USB C to USB C cable 6ft 5 pack 60W braided",
        "ebay_search_query": "USB C to USB C cable 6ft braided single",
        "est_source_price_low": 4.00,
        "est_source_price_high": 10.00,
        "est_ebay_single_low": 5.00,
        "est_ebay_single_high": 12.00,
        "multipack_confidence": "high",
        "notes": "Pure commodity. Razor thin margins. Only works at low source prices.",
    },

    # ========================================================================
    # Phone Accessories
    # ========================================================================
    {
        "id": "MP-011",
        "title": "iPhone Case (Latest Model, Clear/TPU)",
        "category": "Phone Accessories",
        "pack_size": 5,
        "temu_search_query": "iphone 15 case 5 pack clear TPU",
        "amazon_search_query": "iphone 15 case 5 pack clear",
        "ebay_search_query": "iphone 15 case clear single new",
        "est_source_price_low": 5.00,
        "est_source_price_high": 12.00,
        "est_ebay_single_low": 5.00,
        "est_ebay_single_high": 12.00,
        "multipack_confidence": "medium",
        "notes": "Each case in own poly bag/box. Ultra-competitive. Update for new iPhone models.",
    },
    {
        "id": "MP-012",
        "title": "Tempered Glass Screen Protector",
        "category": "Phone Accessories",
        "pack_size": 3,
        "temu_search_query": "iphone 15 tempered glass screen protector 3 pack",
        "amazon_search_query": "iphone 15 screen protector tempered glass 3 pack",
        "ebay_search_query": "iphone 15 screen protector tempered glass 3 pack",
        "est_source_price_low": 2.00,
        "est_source_price_high": 6.00,
        "est_ebay_single_low": 4.00,
        "est_ebay_single_high": 10.00,
        "multipack_confidence": "high",
        "notes": "Typically sold as a 3-pack, not split into singles. Resell as the 3-pack.",
    },
    {
        "id": "MP-013",
        "title": "Car Phone Mount (Magnetic Air Vent)",
        "category": "Car Accessories",
        "pack_size": 4,
        "temu_search_query": "car phone mount magnetic air vent 4 pack",
        "amazon_search_query": "car phone mount magnetic air vent 4 pack",
        "ebay_search_query": "car phone mount magnetic air vent single",
        "est_source_price_low": 5.00,
        "est_source_price_high": 12.00,
        "est_ebay_single_low": 8.00,
        "est_ebay_single_high": 18.00,
        "multipack_confidence": "high",
        "notes": "Each mount individually packaged. Consistent eBay demand.",
    },

    # ========================================================================
    # LED / Lighting
    # ========================================================================
    {
        "id": "MP-014",
        "title": "LED Strip Lights (50ft, Smart WiFi)",
        "category": "Lighting",
        "pack_size": 2,
        "temu_search_query": "LED strip lights 50ft smart wifi 2 rolls 25ft each",
        "amazon_search_query": "LED strip lights 50ft smart wifi 2 pack 25ft",
        "ebay_search_query": "LED strip lights 25ft smart wifi single roll",
        "est_source_price_low": 8.00,
        "est_source_price_high": 18.00,
        "est_ebay_single_low": 12.00,
        "est_ebay_single_high": 25.00,
        "multipack_confidence": "medium",
        "notes": "50ft pack often = 2x 25ft rolls. Each roll individually packaged.",
    },
    {
        "id": "MP-015",
        "title": "LED Night Light (Plug-in, Dusk to Dawn)",
        "category": "Lighting",
        "pack_size": 6,
        "temu_search_query": "LED night light plug in dusk to dawn 6 pack",
        "amazon_search_query": "LED night light plug in dusk to dawn 6 pack warm white",
        "ebay_search_query": "LED night light plug in dusk to dawn single",
        "est_source_price_low": 3.00,
        "est_source_price_high": 8.00,
        "est_ebay_single_low": 3.00,
        "est_ebay_single_high": 8.00,
        "multipack_confidence": "medium",
        "notes": "Low ticket, low profit per unit. Need large pack size to accumulate.",
    },

    # ========================================================================
    # Power / Charging
    # ========================================================================
    {
        "id": "MP-016",
        "title": "Power Bank 10000mAh (Dual USB)",
        "category": "Power",
        "pack_size": 2,
        "temu_search_query": "power bank 10000mah 2 pack dual usb portable charger",
        "amazon_search_query": "power bank 10000mah 2 pack portable charger",
        "ebay_search_query": "power bank 10000mah portable charger single",
        "est_source_price_low": 12.00,
        "est_source_price_high": 25.00,
        "est_ebay_single_low": 15.00,
        "est_ebay_single_high": 30.00,
        "multipack_confidence": "medium",
        "notes": "Higher ticket. Verify battery capacity claims on Temu (often overstated).",
    },

    # ========================================================================
    # Pet Products
    # ========================================================================
    {
        "id": "MP-017",
        "title": "Dog Training Collar (Rechargeable, Remote)",
        "category": "Pet Products",
        "pack_size": 2,
        "temu_search_query": "dog training collar rechargeable remote 2 pack",
        "amazon_search_query": "dog training collar rechargeable remote 2 pack",
        "ebay_search_query": "dog training collar rechargeable remote single",
        "est_source_price_low": 14.00,
        "est_source_price_high": 30.00,
        "est_ebay_single_low": 25.00,
        "est_ebay_single_high": 45.00,
        "multipack_confidence": "medium",
        "notes": "Higher per-unit price = better margin. Quality inconsistency risk.",
    },
    {
        "id": "MP-018",
        "title": "Dog Bark Collar",
        "category": "Pet Products",
        "pack_size": 2,
        "temu_search_query": "dog bark collar rechargeable 2 pack",
        "amazon_search_query": "dog bark collar rechargeable 2 pack",
        "ebay_search_query": "dog bark collar rechargeable single",
        "est_source_price_low": 10.00,
        "est_source_price_high": 20.00,
        "est_ebay_single_low": 20.00,
        "est_ebay_single_high": 35.00,
        "multipack_confidence": "medium",
        "notes": "Good potential spread. Verify reliability before scaling.",
    },

    # ========================================================================
    # Home / Kitchen
    # ========================================================================
    {
        "id": "MP-019",
        "title": "Air Fryer Liners (Parchment Paper)",
        "category": "Home & Kitchen",
        "pack_size": 100,
        "temu_search_query": "air fryer liners parchment paper 100 pack",
        "amazon_search_query": "air fryer liners parchment paper 100 pack round",
        "ebay_search_query": "air fryer liners parchment paper 100 pack",
        "est_source_price_low": 3.00,
        "est_source_price_high": 8.00,
        "est_ebay_single_low": 8.00,
        "est_ebay_single_high": 15.00,
        "multipack_confidence": "low",
        "notes": "NOT a true multipack (just a bag of 100 sheets). Resell as whole pack only.",
    },
    {
        "id": "MP-020",
        "title": "Silicone Cooking Utensil Set",
        "category": "Home & Kitchen",
        "pack_size": 10,
        "temu_search_query": "silicone cooking utensils 10 piece set kitchen",
        "amazon_search_query": "silicone cooking utensils 10 piece set kitchen",
        "ebay_search_query": "silicone cooking utensils set 10 piece",
        "est_source_price_low": 8.00,
        "est_source_price_high": 18.00,
        "est_ebay_single_low": 15.00,
        "est_ebay_single_high": 25.00,
        "multipack_confidence": "low",
        "notes": "Sold as a set, not split. Not a true multipack. Resell as complete set.",
    },

    # ========================================================================
    # Security Cameras
    # ========================================================================
    {
        "id": "MP-021",
        "title": "Mini Security Camera (WiFi, Indoor)",
        "category": "Security",
        "pack_size": 2,
        "temu_search_query": "mini security camera wifi indoor 2 pack",
        "amazon_search_query": "mini security camera wifi indoor 2 pack night vision",
        "ebay_search_query": "mini security camera wifi indoor night vision single",
        "est_source_price_low": 15.00,
        "est_source_price_high": 30.00,
        "est_ebay_single_low": 20.00,
        "est_ebay_single_high": 40.00,
        "multipack_confidence": "medium",
        "notes": "Higher ticket. Verify app quality and reliability before scaling.",
    },
    {
        "id": "MP-022",
        "title": "Video Doorbell (Wireless, Battery)",
        "category": "Security",
        "pack_size": 2,
        "temu_search_query": "wireless video doorbell battery 2 pack wifi",
        "amazon_search_query": "wireless video doorbell battery wifi 2 pack",
        "ebay_search_query": "wireless video doorbell battery wifi single",
        "est_source_price_low": 20.00,
        "est_source_price_high": 40.00,
        "est_ebay_single_low": 25.00,
        "est_ebay_single_high": 50.00,
        "multipack_confidence": "medium",
        "notes": "Higher ticket, higher return rate. Quality varies enormously on Temu.",
    },

    # ========================================================================
    # Gaming
    # ========================================================================
    {
        "id": "MP-023",
        "title": "Wireless Controller (Generic PS/Xbox Compatible)",
        "category": "Gaming",
        "pack_size": 2,
        "temu_search_query": "wireless controller 2 pack pc ps3 bluetooth",
        "amazon_search_query": "wireless controller 2 pack pc bluetooth",
        "ebay_search_query": "wireless controller pc bluetooth single",
        "est_source_price_low": 18.00,
        "est_source_price_high": 35.00,
        "est_ebay_single_low": 20.00,
        "est_ebay_single_high": 35.00,
        "multipack_confidence": "low",
        "notes": "Compatibility and build quality issues common. High return risk.",
    },
    {
        "id": "MP-024",
        "title": "Controller Charging Dock (2 Charger)",
        "category": "Gaming",
        "pack_size": 1,
        "temu_search_query": "ps5 controller charger dock station",
        "amazon_search_query": "ps5 controller charger dock station",
        "ebay_search_query": "ps5 controller charger dock station",
        "est_source_price_low": 8.00,
        "est_source_price_high": 15.00,
        "est_ebay_single_low": 12.00,
        "est_ebay_single_high": 25.00,
        "multipack_confidence": "n/a",
        "notes": "Single product, not a multipack. Included for reference.",
    },
]


def get_catalog(
    category: str = None,
    min_pack_size: int = 2,
    confidence: str = None,
    min_estimated_profit: float = 0,
    sort_by: str = "est_profit",
) -> list:
    """
    Get filtered/sorted catalog entries.
    Returns list of catalog dicts with calculated estimated profit.
    """
    results = []

    for item in MULTIPACK_CATALOG:
        # Filter by pack size
        if item["pack_size"] < min_pack_size:
            continue

        # Filter by category
        if category and category.lower() != "all" and item["category"].lower() != category.lower():
            continue

        # Filter by confidence
        if confidence and confidence != "all" and item["multipack_confidence"] != confidence:
            continue

        # Calculate estimated profit (mid-points)
        source_price = (item["est_source_price_low"] + item["est_source_price_high"]) / 2
        ebay_single = (item["est_ebay_single_low"] + item["est_ebay_single_high"]) / 2
        pack_size = item["pack_size"]

        # Conservative revenue: 80% of estimated eBay price (account for fees, shipping)
        revenue = ebay_single * pack_size
        estimated_net = revenue * 0.70 - source_price  # rough: 30% all-in costs

        entry = {
            **item,
            "est_source_price_mid": round(source_price, 2),
            "est_ebay_single_mid": round(ebay_single, 2),
            "est_net_profit": round(estimated_net, 2),
            "temu_url": f"https://www.temu.com/search_result.html?search_key={item['temu_search_query'].replace(' ', '+')}",
            "amazon_url": f"https://www.amazon.com/s?k={item['amazon_search_query'].replace(' ', '+')}",
            "ebay_url": f"https://www.ebay.com/sch/i.html?_nkw={item['ebay_search_query'].replace(' ', '+')}",
            "source_price_verified": False,
            "ebay_price_verified": False,
        }

        # Filter by estimated profit
        if estimated_net >= min_estimated_profit:
            results.append(entry)

    # Sort
    if sort_by == "est_profit":
        results.sort(key=lambda x: x["est_net_profit"], reverse=True)
    elif sort_by == "pack_size":
        results.sort(key=lambda x: x["pack_size"], reverse=True)
    elif sort_by == "title":
        results.sort(key=lambda x: x["title"])

    return results


def get_categories() -> list:
    """Get list of unique categories in the catalog."""
    cats = set(item["category"] for item in MULTIPACK_CATALOG)
    return sorted(list(cats))


def get_by_id(product_id: str) -> dict:
    """Get a single catalog entry by ID."""
    for item in MULTIPACK_CATALOG:
        if item["id"] == product_id:
            source_price = (item["est_source_price_low"] + item["est_source_price_high"]) / 2
            ebay_single = (item["est_ebay_single_low"] + item["est_ebay_single_high"]) / 2
            pack_size = item["pack_size"]
            revenue = ebay_single * pack_size
            estimated_net = revenue * 0.70 - source_price
            return {
                **item,
                "est_source_price_mid": round(source_price, 2),
                "est_ebay_single_mid": round(ebay_single, 2),
                "est_net_profit": round(estimated_net, 2),
                "temu_url": f"https://www.temu.com/search_result.html?search_key={item['temu_search_query'].replace(' ', '+')}",
                "amazon_url": f"https://www.amazon.com/s?k={item['amazon_search_query'].replace(' ', '+')}",
                "ebay_url": f"https://www.ebay.com/sch/i.html?_nkw={item['ebay_search_query'].replace(' ', '+')}",
            }
    return None
