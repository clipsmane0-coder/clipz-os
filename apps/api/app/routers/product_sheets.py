"""
Product sheets router.
CRUD for product sheets + sync endpoint to create eBay drafts from a product sheet.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.models import User
from app.models.product_sheet import ProductSheet
from app.models.ebay_models import EbayDraftListing

router = APIRouter(prefix="/api/v1/product-sheets", tags=["product-sheets"])


# ============================================================
# CRUD
# ============================================================

@router.get("")
async def list_product_sheets(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List all product sheets."""
    query = select(ProductSheet).where(ProductSheet.user_id == user.id)
    if status:
        query = query.where(ProductSheet.overall_status == status)
    if product_type:
        query = query.where(ProductSheet.product_type == product_type)
    query = query.order_by(ProductSheet.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    sheets = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "product_name": s.product_name,
                "brand": s.brand,
                "model": s.model,
                "asin": s.asin,
                "product_type": s.product_type,
                "pack_size": s.pack_size,
                "pack_price": s.pack_price,
                "cost_per_unit": s.cost_per_unit,
                "estimated_ebay_price_per_unit": s.estimated_ebay_price_per_unit,
                "estimated_net_profit_per_pack": s.estimated_net_profit_per_pack,
                "estimated_roi": s.estimated_roi,
                "overall_status": s.overall_status,
                "verified_title": s.verified_title,
                "verified_pack_size": s.verified_pack_size,
                "verified_price": s.verified_price,
                "verified_ebay_demand": s.verified_ebay_demand,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in sheets
        ],
        "meta": {"count": len(sheets)},
    }


@router.get("/{sheet_id}")
async def get_product_sheet(
    sheet_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single product sheet."""
    result = await db.execute(
        select(ProductSheet).where(
            ProductSheet.id == sheet_id,
            ProductSheet.user_id == user.id,
        )
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=404, detail="Product sheet not found")

    return {
        "success": True,
        "data": {
            "id": sheet.id,
            "product_name": sheet.product_name,
            "brand": sheet.brand,
            "model": sheet.model,
            "mpn": sheet.mpn,
            "upc": sheet.upc,
            "asin": sheet.asin,
            "product_type": sheet.product_type,
            "source": sheet.source,
            "source_url": sheet.source_url,
            "pack_size": sheet.pack_size,
            "pack_price": sheet.pack_price,
            "cost_per_unit": sheet.cost_per_unit,
            "color": sheet.color,
            "power_source": sheet.power_source,
            "sensor_type": sheet.sensor_type,
            "dimensions": sheet.dimensions,
            "weight_lbs": sheet.weight_lbs,
            "certifications": sheet.certifications,
            "features": sheet.features or [],
            "split_strategy": sheet.split_strategy,
            "sell_individually": sheet.sell_individually,
            "estimated_ebay_price_per_unit": sheet.estimated_ebay_price_per_unit,
            "estimated_shipping_cost": sheet.estimated_shipping_cost,
            "estimated_net_profit_per_pack": sheet.estimated_net_profit_per_pack,
            "estimated_roi": sheet.estimated_roi,
            "verified_title": sheet.verified_title,
            "verified_pack_size": sheet.verified_pack_size,
            "verified_price": sheet.verified_price,
            "verified_ebay_demand": sheet.verified_ebay_demand,
            "overall_status": sheet.overall_status,
            "rejection_reason": sheet.rejection_reason,
            "suggested_ebay_category_id": sheet.suggested_ebay_category_id,
            "suggested_ebay_category_name": sheet.suggested_ebay_category_name,
            "notes": sheet.notes,
            "created_at": sheet.created_at.isoformat() if sheet.created_at else None,
            "updated_at": sheet.updated_at.isoformat() if sheet.updated_at else None,
        },
        "meta": {},
    }


@router.post("")
async def create_product_sheet(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product sheet."""
    body = await request.json()

    product_name = body.get("product_name")
    if not product_name:
        raise HTTPException(status_code=400, detail="product_name is required")

    pack_size = body.get("pack_size")
    pack_price = body.get("pack_price")
    cost_per_unit = body.get("cost_per_unit")

    # Calculate cost_per_unit if not provided
    if not cost_per_unit and pack_size and pack_price:
        cost_per_unit = round(pack_price / pack_size, 2)

    sheet = ProductSheet(
        user_id=user.id,
        product_name=product_name,
        brand=body.get("brand"),
        model=body.get("model"),
        mpn=body.get("mpn"),
        upc=body.get("upc"),
        asin=body.get("asin"),
        product_type=body.get("product_type"),
        source=body.get("source", "amazon"),
        source_url=body.get("source_url"),
        pack_size=pack_size,
        pack_price=pack_price,
        cost_per_unit=cost_per_unit,
        color=body.get("color"),
        power_source=body.get("power_source"),
        sensor_type=body.get("sensor_type"),
        dimensions=body.get("dimensions"),
        weight_lbs=body.get("weight_lbs"),
        certifications=body.get("certifications"),
        features=body.get("features", []),
        split_strategy=body.get("split_strategy"),
        sell_individually=body.get("sell_individually", True),
        estimated_ebay_price_per_unit=body.get("estimated_ebay_price_per_unit"),
        estimated_shipping_cost=body.get("estimated_shipping_cost"),
        estimated_net_profit_per_pack=body.get("estimated_net_profit_per_pack"),
        estimated_roi=body.get("estimated_roi"),
        verified_title=body.get("verified_title", False),
        verified_pack_size=body.get("verified_pack_size", False),
        verified_price=body.get("verified_price", False),
        verified_ebay_demand=body.get("verified_ebay_demand", False),
        overall_status=body.get("overall_status", "pending"),
        rejection_reason=body.get("rejection_reason"),
        suggested_ebay_category_id=body.get("suggested_ebay_category_id"),
        suggested_ebay_category_name=body.get("suggested_ebay_category_name"),
        notes=body.get("notes"),
    )

    db.add(sheet)
    await db.commit()
    await db.refresh(sheet)

    return {
        "success": True,
        "data": {"id": sheet.id, "product_name": sheet.product_name},
        "meta": {},
    }


@router.put("/{sheet_id}")
async def update_product_sheet(
    sheet_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a product sheet."""
    result = await db.execute(
        select(ProductSheet).where(
            ProductSheet.id == sheet_id,
            ProductSheet.user_id == user.id,
        )
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=404, detail="Product sheet not found")

    body = await request.json()

    updatable = [
        "product_name", "brand", "model", "mpn", "upc", "asin", "product_type",
        "source", "source_url", "pack_size", "pack_price",
        "color", "power_source", "sensor_type", "dimensions", "weight_lbs",
        "certifications", "features", "split_strategy", "sell_individually",
        "estimated_ebay_price_per_unit", "estimated_shipping_cost",
        "estimated_net_profit_per_pack", "estimated_roi",
        "verified_title", "verified_pack_size", "verified_price",
        "verified_ebay_demand", "overall_status", "rejection_reason",
        "suggested_ebay_category_id", "suggested_ebay_category_name", "notes",
    ]

    for field in updatable:
        if field in body:
            setattr(sheet, field, body[field])

    # Recalculate cost_per_unit if pack_size or pack_price changed
    if "pack_size" in body or "pack_price" in body:
        if sheet.pack_size and sheet.pack_price:
            sheet.cost_per_unit = round(sheet.pack_price / sheet.pack_size, 2)

    await db.commit()
    await db.refresh(sheet)

    return {
        "success": True,
        "data": {"id": sheet.id, "updated": True},
        "meta": {},
    }


@router.delete("/{sheet_id}")
async def delete_product_sheet(
    sheet_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a product sheet."""
    result = await db.execute(
        select(ProductSheet).where(
            ProductSheet.id == sheet_id,
            ProductSheet.user_id == user.id,
        )
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=404, detail="Product sheet not found")

    await db.delete(sheet)
    await db.commit()

    return {"success": True, "data": {"deleted": True}, "meta": {}}


# ============================================================
# SYNC: Product Sheet → eBay Draft
# ============================================================

@router.post("/{sheet_id}/sync-to-ebay-draft")
async def sync_product_sheet_to_ebay_draft(
    sheet_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create (or update) an eBay draft listing from a product sheet.
    One API call goes from verified product sheet → fully populated eBay draft.

    If the product sheet already has an associated eBay draft (via notes),
    it updates that draft instead of creating a new one.

    Body can override any draft field: price, title, etc.
    """
    result = await db.execute(
        select(ProductSheet).where(
            ProductSheet.id == sheet_id,
            ProductSheet.user_id == user.id,
        )
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=404, detail="Product sheet not found")

    if not sheet.pack_size or sheet.pack_size < 2:
        raise HTTPException(
            status_code=400,
            detail="Product sheet must have a pack_size of 2+ to create a split listing",
        )

    body = await request.json()

    # Build the title — prefer override, then sheet.estimated_ebay_title,
    # then auto-generate from product name + brand
    title_override = body.get("title")
    if title_override:
        title = title_override[:80]
    else:
        # Auto-generate a solid eBay title
        parts = []
        if sheet.brand:
            parts.append(sheet.brand)
        if sheet.model:
            parts.append(sheet.model)
        parts.append(sheet.product_name)
        if sheet.color and sheet.color.lower() != "white":
            parts.append(f"- {sheet.color}")
        title = " ".join(parts)[:80]

    # Price — use override or estimated
    price = body.get("price")
    if not price:
        price = sheet.estimated_ebay_price_per_unit
    if not price:
        raise HTTPException(
            status_code=400,
            detail="No price set. Either pass 'price' in body or set estimated_ebay_price_per_unit on the product sheet.",
        )

    # Build item specifics from the sheet data
    item_specifics = {}
    if sheet.brand:
        item_specifics["Brand"] = sheet.brand
    if sheet.model:
        item_specifics["Model"] = sheet.model
    if sheet.mpn:
        item_specifics["MPN"] = sheet.mpn
    if sheet.upc:
        item_specifics["UPC"] = sheet.upc
    if sheet.color:
        item_specifics["Color"] = sheet.color
    if sheet.power_source:
        item_specifics["Power Source"] = sheet.power_source
    if sheet.sensor_type:
        item_specifics["Sensor Technology"] = sheet.sensor_type
    if sheet.certifications:
        item_specifics["Certification"] = sheet.certifications
    # Add any override specifics
    if "item_specifics" in body:
        item_specifics.update(body["item_specifics"])

    # Build description from features
    description = body.get("description")
    if not description:
        desc_parts = [f"{title}\n"]
        if sheet.features and len(sheet.features) > 0:
            desc_parts.append("Key Features:\n")
            for i, f in enumerate(sheet.features[:8]):
                desc_parts.append(f"✅ {f}")
        if sheet.split_strategy:
            desc_parts.append(f"\nCondition: Brand new, individually sealed. Removed from a {sheet.pack_size}-pack multipack — no individual retail box. All original contents included.")
        desc_parts.append(f"\nFast shipping in 1 business day. 30-day returns accepted on unopened units.")
        description = "\n".join(desc_parts)

    # Estimated shipping cost
    shipping_cost = body.get("estimated_shipping_cost") or sheet.estimated_shipping_cost or 4.0

    # Check if we already have a draft for this sheet
    existing_draft_id = None
    if sheet.notes and "ebay_draft_id:" in sheet.notes:
        import re
        m = re.search(r"ebay_draft_id:\s*(\S+)", sheet.notes)
        if m:
            existing_draft_id = m.group(1)

    if existing_draft_id:
        # Update existing draft
        draft_result = await db.execute(
            select(EbayDraftListing).where(
                EbayDraftListing.id == existing_draft_id,
                EbayDraftListing.user_id == user.id,
            )
        )
        draft = draft_result.scalar_one_or_none()
        if draft:
            # Update all fields
            draft.title = title
            draft.description = description
            draft.price = price
            draft.product_name = sheet.product_name
            draft.brand = sheet.brand
            draft.model = sheet.model
            draft.mpn = sheet.mpn
            draft.upc = sheet.upc
            draft.asin = sheet.asin
            draft.source_url = sheet.source_url
            draft.item_specifics = item_specifics
            draft.pack_size = sheet.pack_size
            draft.cost_per_unit = sheet.cost_per_unit
            draft.pack_cost = sheet.pack_price
            draft.estimated_shipping_cost = shipping_cost
            draft.quantity = body.get("quantity", sheet.pack_size or 1)

            # Recalculate economics
            qty = draft.quantity
            draft.estimated_ebay_fee = round(price * 0.1325 + 0.30, 2)
            total_revenue = price * qty
            total_cost = (sheet.cost_per_unit or 0) * qty
            total_fees = draft.estimated_ebay_fee * qty
            total_shipping = shipping_cost * qty
            draft.estimated_net_profit = round(
                total_revenue - total_cost - total_fees - total_shipping, 2
            )
            draft.estimated_roi = round(
                (draft.estimated_net_profit / total_cost) * 100, 1
            ) if total_cost > 0 else 0.0

            # Category
            if sheet.suggested_ebay_category_id:
                draft.category_id = sheet.suggested_ebay_category_id

            await db.commit()
            await db.refresh(draft)

            return {
                "success": True,
                "data": {
                    "action": "updated",
                    "draft_id": draft.id,
                    "title": draft.title,
                    "price": draft.price,
                    "estimated_net_profit": draft.estimated_net_profit,
                    "estimated_roi": draft.estimated_roi,
                    "status": draft.status,
                },
                "meta": {},
            }

    # Create new draft
    quantity = body.get("quantity", sheet.pack_size or 1)
    estimated_ebay_fee = round(price * 0.1325 + 0.30, 2)
    cost_per_unit = sheet.cost_per_unit or 0
    total_revenue = price * quantity
    total_cost = cost_per_unit * quantity
    total_fees = estimated_ebay_fee * quantity
    total_shipping = shipping_cost * quantity
    estimated_net_profit = round(total_revenue - total_cost - total_fees - total_shipping, 2)
    estimated_roi = round((estimated_net_profit / total_cost) * 100, 1) if total_cost > 0 else 0.0

    draft = EbayDraftListing(
        user_id=user.id,
        product_name=sheet.product_name,
        brand=sheet.brand,
        model=sheet.model,
        mpn=sheet.mpn,
        upc=sheet.upc,
        asin=sheet.asin,
        source_url=sheet.source_url,
        title=title,
        description=description,
        category_id=sheet.suggested_ebay_category_id,
        condition=body.get("condition", "1000"),
        condition_description=body.get(
            "condition_description",
            f"Brand new, individually sealed. Removed from a {sheet.pack_size}-pack multipack — no individual retail box."
        ),
        price=price,
        currency="USD",
        quantity=quantity,
        item_specifics=item_specifics,
        shipping_service=body.get("shipping_service", "USPSFirstClass"),
        free_shipping=body.get("free_shipping", True),
        handling_time=body.get("handling_time", 1),
        returns_accepted=body.get("returns_accepted", True),
        return_days=body.get("return_days", 30),
        pack_size=sheet.pack_size,
        cost_per_unit=cost_per_unit,
        pack_cost=sheet.pack_price,
        estimated_ebay_fee=estimated_ebay_fee,
        estimated_shipping_cost=shipping_cost,
        estimated_net_profit=estimated_net_profit,
        estimated_roi=estimated_roi,
        status="draft",
    )

    db.add(draft)
    await db.flush()

    # Link back in the product sheet notes
    draft_ref = f"ebay_draft_id: {draft.id}"
    if sheet.notes:
        sheet.notes = sheet.notes + f"\n{draft_ref}"
    else:
        sheet.notes = draft_ref

    await db.commit()
    await db.refresh(draft)
    await db.refresh(sheet)

    return {
        "success": True,
        "data": {
            "action": "created",
            "draft_id": draft.id,
            "title": draft.title,
            "price": draft.price,
            "quantity": draft.quantity,
            "estimated_ebay_fee": draft.estimated_ebay_fee,
            "estimated_net_profit": draft.estimated_net_profit,
            "estimated_roi": draft.estimated_roi,
            "status": draft.status,
            "draft_url": f"/api/v1/ebay/drafts/{draft.id}",
        },
        "meta": {
            "next_step": f"Verify the draft at /api/v1/ebay/drafts/{draft.id}, then call POST /api/v1/ebay/drafts/{draft.id}/publish to go live on eBay",
        },
    }
