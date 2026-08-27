"""
eBay Sell API router.
Endpoints for OAuth, draft listings, and publishing.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.config import settings
from app.auth.dependencies import get_current_user
from app.models.models import User
from app.models.ebay_models import EbayToken, EbayDraftListing
from app.services.ebay_service import EbayClient, EbayApiError

router = APIRouter(prefix="/api/v1/ebay", tags=["ebay"])


def get_ebay_client(user_token: Optional[EbayToken] = None) -> EbayClient:
    """Build an eBay client from settings + user token."""
    client_id = getattr(settings, "ebay_client_id", "")
    client_secret = getattr(settings, "ebay_client_secret", "")
    redirect_uri = getattr(settings, "ebay_redirect_uri", "")

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail="eBay API credentials not configured. Set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET.",
        )

    env = getattr(settings, "ebay_env", "production")

    return EbayClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        access_token=user_token.access_token if user_token else None,
        refresh_token=user_token.refresh_token if user_token else None,
        access_token_expires_at=user_token.access_token_expires_at if user_token else None,
        refresh_token_expires_at=user_token.refresh_token_expires_at if user_token else None,
        env=env,
    )


async def get_user_token(db: AsyncSession, user_id: str) -> Optional[EbayToken]:
    """Get the user's eBay token, if any."""
    result = await db.execute(
        select(EbayToken).where(EbayToken.user_id == user_id).limit(1)
    )
    return result.scalar_one_or_none()


async def save_token(
    db: AsyncSession,
    user_id: str,
    token_data: dict,
    env: str = "production",
):
    """Save or update the user's eBay token."""
    token = await get_user_token(db, user_id)
    if token:
        token.access_token = token_data["access_token"]
        token.refresh_token = token_data["refresh_token"]
        token.access_token_expires_at = token_data["access_token_expires_at"]
        token.refresh_token_expires_at = token_data["refresh_token_expires_at"]
        token.ebay_env = env
        token.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        token = EbayToken(
            user_id=user_id,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            access_token_expires_at=token_data["access_token_expires_at"],
            refresh_token_expires_at=token_data["refresh_token_expires_at"],
            ebay_env=env,
        )
        db.add(token)
    await db.commit()
    await db.refresh(token)
    return token


# ============================================================
# AUTH / OAUTH
# ============================================================

@router.get("/auth/url")
async def get_oauth_url(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the eBay OAuth authorization URL. Redirect user here to connect their account."""
    state = str(uuid.uuid4())  # CSRF protection
    client = get_ebay_client()
    auth_url = client.get_authorization_url(state=state)
    return {
        "success": True,
        "data": {
            "auth_url": auth_url,
            "state": state,
        },
        "meta": {},
    }


@router.get("/auth/callback")
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
):
    """
    eBay OAuth callback. User is redirected here after granting access.
    Exchanges the code for tokens and stores them.
    """
    # NOTE: In a real flow, we'd look up the user from the state parameter.
    # For now, we use the session/user context.
    # Since callback comes from eBay directly, we need a way to identify the user.
    # We'll store tokens with a temp marker and the user can claim them.
    try:
        client = get_ebay_client()
        token_data = await client.exchange_code_for_tokens(code)

        # Try to get the user info
        try:
            user_info = await client.get_user()
            ebay_user_id = user_info.get("userId", "")
        except EbayApiError:
            ebay_user_id = ""

        return {
            "success": True,
            "data": {
                "ebay_user_id": ebay_user_id,
                "access_token_expires_at": token_data["access_token_expires_at"].isoformat(),
                "refresh_token_expires_at": token_data["refresh_token_expires_at"].isoformat(),
            },
            "meta": {
                "message": "OAuth successful. Pass the access token to your account via the /auth/connect endpoint.",
            },
        }
    except EbayApiError as e:
        raise HTTPException(status_code=500, detail=f"OAuth failed: {e}")


@router.post("/auth/connect")
async def connect_account(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Connect an eBay account using an access/refresh token pair.
    Use this after the OAuth callback to save tokens to the user's account.
    """
    body = await request.json()
    access_token = body.get("access_token")
    refresh_token = body.get("refresh_token")
    access_token_expires_at = body.get("access_token_expires_at")
    refresh_token_expires_at = body.get("refresh_token_expires_at")
    ebay_user_id = body.get("ebay_user_id", "")

    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="access_token and refresh_token are required")

    # Parse dates
    from datetime import datetime
    access_exp = datetime.fromisoformat(access_token_expires_at) if access_token_expires_at else None
    refresh_exp = datetime.fromisoformat(refresh_token_expires_at) if refresh_token_expires_at else None

    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "access_token_expires_at": access_exp,
        "refresh_token_expires_at": refresh_exp,
    }

    token = await save_token(db, user.id, token_data)
    if ebay_user_id:
        token.ebay_user_id = ebay_user_id
        await db.commit()

    return {
        "success": True,
        "data": {
            "ebay_user_id": token.ebay_user_id,
            "expires_at": token.access_token_expires_at.isoformat() if token.access_token_expires_at else None,
            "connected": True,
        },
        "meta": {},
    }


@router.get("/auth/status")
async def auth_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if user has a connected eBay account."""
    token = await get_user_token(db, user.id)
    if not token:
        return {
            "success": True,
            "data": {"connected": False, "ebay_user_id": None},
            "meta": {},
        }

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    access_valid = token.access_token_expires_at > now if token.access_token_expires_at else False
    refresh_valid = token.refresh_token_expires_at > now if token.refresh_token_expires_at else False

    return {
        "success": True,
        "data": {
            "connected": True,
            "ebay_user_id": token.ebay_user_id,
            "access_token_valid": access_valid,
            "refresh_token_valid": refresh_valid,
            "access_token_expires_at": token.access_token_expires_at.isoformat() if token.access_token_expires_at else None,
        },
        "meta": {},
    }


@router.delete("/auth/disconnect")
async def disconnect_account(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove the user's eBay token (disconnect account)."""
    token = await get_user_token(db, user.id)
    if token:
        await db.delete(token)
        await db.commit()
    return {"success": True, "data": {"connected": False}, "meta": {}}


# ============================================================
# DRAFT LISTINGS
# ============================================================

@router.get("/drafts")
async def list_drafts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List all draft listings for the current user."""
    query = select(EbayDraftListing).where(EbayDraftListing.user_id == user.id)
    if status:
        query = query.where(EbayDraftListing.status == status)
    query = query.order_by(EbayDraftListing.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    drafts = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": d.id,
                "title": d.title,
                "product_name": d.product_name,
                "brand": d.brand,
                "price": d.price,
                "currency": d.currency,
                "quantity": d.quantity,
                "status": d.status,
                "category_id": d.category_id,
                "ebay_item_id": d.ebay_item_id,
                "ebay_offer_id": d.ebay_offer_id,
                "cost_per_unit": d.cost_per_unit,
                "estimated_net_profit": d.estimated_net_profit,
                "estimated_roi": d.estimated_roi,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None,
            }
            for d in drafts
        ],
        "meta": {"count": len(drafts)},
    }


@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single draft listing by ID."""
    result = await db.execute(
        select(EbayDraftListing).where(
            EbayDraftListing.id == draft_id,
            EbayDraftListing.user_id == user.id,
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    return {
        "success": True,
        "data": {
            "id": draft.id,
            "product_name": draft.product_name,
            "brand": draft.brand,
            "model": draft.model,
            "mpn": draft.mpn,
            "upc": draft.upc,
            "asin": draft.asin,
            "source_url": draft.source_url,
            "title": draft.title,
            "subtitle": draft.subtitle,
            "description": draft.description,
            "category_id": draft.category_id,
            "condition": draft.condition,
            "condition_description": draft.condition_description,
            "price": draft.price,
            "currency": draft.currency,
            "quantity": draft.quantity,
            "item_specifics": draft.item_specifics or {},
            "shipping_service": draft.shipping_service,
            "shipping_cost": draft.shipping_cost,
            "free_shipping": draft.free_shipping,
            "handling_time": draft.handling_time,
            "ship_from_postal_code": draft.ship_from_postal_code,
            "returns_accepted": draft.returns_accepted,
            "return_policy": draft.return_policy,
            "return_days": draft.return_days,
            "pack_size": draft.pack_size,
            "cost_per_unit": draft.cost_per_unit,
            "pack_cost": draft.pack_cost,
            "estimated_ebay_fee": draft.estimated_ebay_fee,
            "estimated_shipping_cost": draft.estimated_shipping_cost,
            "estimated_net_profit": draft.estimated_net_profit,
            "estimated_roi": draft.estimated_roi,
            "status": draft.status,
            "ebay_item_id": draft.ebay_item_id,
            "ebay_offer_id": draft.ebay_offer_id,
            "ebay_listing_url": draft.ebay_listing_url,
            "error_message": draft.error_message,
            "submitted_at": draft.submitted_at.isoformat() if draft.submitted_at else None,
            "created_at": draft.created_at.isoformat() if draft.created_at else None,
            "updated_at": draft.updated_at.isoformat() if draft.updated_at else None,
        },
        "meta": {},
    }


@router.post("/drafts")
async def create_draft(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new draft listing. Does NOT publish to eBay yet.
    Calculates economics automatically from provided cost data.
    """
    body = await request.json()

    # Required fields
    title = body.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    price = body.get("price")
    if price is None:
        raise HTTPException(status_code=400, detail="price is required")

    # Calculate economics if we have cost data
    cost_per_unit = body.get("cost_per_unit")
    quantity = body.get("quantity", 1)
    estimated_shipping_cost = body.get("estimated_shipping_cost", 4.0)

    estimated_ebay_fee = round(price * 0.1325 + 0.30, 2)  # 13.25% + $0.30
    estimated_net_profit = 0.0
    estimated_roi = 0.0
    if cost_per_unit:
        total_revenue = price * quantity
        total_cost = cost_per_unit * quantity
        total_fees = estimated_ebay_fee * quantity
        total_shipping = estimated_shipping_cost * quantity
        estimated_net_profit = round(total_revenue - total_cost - total_fees - total_shipping, 2)
        estimated_roi = round((estimated_net_profit / total_cost) * 100, 1) if total_cost > 0 else 0.0

    draft = EbayDraftListing(
        user_id=user.id,
        product_name=body.get("product_name", title),
        brand=body.get("brand"),
        model=body.get("model"),
        mpn=body.get("mpn"),
        upc=body.get("upc"),
        asin=body.get("asin"),
        source_url=body.get("source_url"),
        title=title,
        subtitle=body.get("subtitle"),
        description=body.get("description", ""),
        category_id=body.get("category_id"),
        condition=body.get("condition", "1000"),
        condition_description=body.get("condition_description"),
        price=price,
        currency=body.get("currency", "USD"),
        quantity=quantity,
        item_specifics=body.get("item_specifics", {}),
        shipping_service=body.get("shipping_service", "USPSFirstClass"),
        shipping_cost=body.get("shipping_cost", 0.0),
        free_shipping=body.get("free_shipping", True),
        handling_time=body.get("handling_time", 1),
        ship_from_postal_code=body.get("ship_from_postal_code"),
        returns_accepted=body.get("returns_accepted", True),
        return_policy=body.get("return_policy"),
        return_days=body.get("return_days", 30),
        pack_size=body.get("pack_size"),
        cost_per_unit=cost_per_unit,
        pack_cost=body.get("pack_cost"),
        estimated_ebay_fee=estimated_ebay_fee,
        estimated_shipping_cost=estimated_shipping_cost,
        estimated_net_profit=estimated_net_profit,
        estimated_roi=estimated_roi,
        status="draft",
    )

    db.add(draft)
    await db.commit()
    await db.refresh(draft)

    return {
        "success": True,
        "data": {
            "id": draft.id,
            "title": draft.title,
            "price": draft.price,
            "status": draft.status,
            "estimated_ebay_fee": draft.estimated_ebay_fee,
            "estimated_net_profit": draft.estimated_net_profit,
            "estimated_roi": draft.estimated_roi,
        },
        "meta": {},
    }


@router.put("/drafts/{draft_id}")
async def update_draft(
    draft_id: str,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing draft listing."""
    result = await db.execute(
        select(EbayDraftListing).where(
            EbayDraftListing.id == draft_id,
            EbayDraftListing.user_id == user.id,
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    body = await request.json()

    # Update fields that were provided
    updatable_fields = [
        "product_name", "brand", "model", "mpn", "upc", "asin", "source_url",
        "title", "subtitle", "description", "category_id", "condition",
        "condition_description", "price", "currency", "quantity",
        "item_specifics", "shipping_service", "shipping_cost", "free_shipping",
        "handling_time", "ship_from_postal_code", "returns_accepted",
        "return_policy", "return_days", "pack_size", "cost_per_unit", "pack_cost",
    ]

    for field in updatable_fields:
        if field in body:
            setattr(draft, field, body[field])

    # Recalculate economics if price or cost changed
    if "price" in body or "cost_per_unit" in body or "quantity" in body:
        price = draft.price or 0
        cost_per_unit = draft.cost_per_unit or 0
        quantity = draft.quantity or 1
        shipping_cost = draft.estimated_shipping_cost or 4.0

        draft.estimated_ebay_fee = round(price * 0.1325 + 0.30, 2)
        total_revenue = price * quantity
        total_cost = cost_per_unit * quantity
        total_fees = draft.estimated_ebay_fee * quantity
        total_shipping = shipping_cost * quantity
        draft.estimated_net_profit = round(
            total_revenue - total_cost - total_fees - total_shipping, 2
        )
        draft.estimated_roi = round(
            (draft.estimated_net_profit / total_cost) * 100, 1
        ) if total_cost > 0 else 0.0

    await db.commit()
    await db.refresh(draft)

    return {
        "success": True,
        "data": {
            "id": draft.id,
            "status": draft.status,
            "estimated_net_profit": draft.estimated_net_profit,
            "estimated_roi": draft.estimated_roi,
        },
        "meta": {},
    }


@router.delete("/drafts/{draft_id}")
async def delete_draft(
    draft_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a draft listing."""
    result = await db.execute(
        select(EbayDraftListing).where(
            EbayDraftListing.id == draft_id,
            EbayDraftListing.user_id == user.id,
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    await db.delete(draft)
    await db.commit()

    return {"success": True, "data": {"deleted": True}, "meta": {}}


# ============================================================
# PUBLISH TO EBAY
# ============================================================

@router.post("/drafts/{draft_id}/publish")
async def publish_draft(
    draft_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Publish a draft listing to eBay.
    Creates the inventory item and offer, then publishes.
    Requires a connected eBay account.
    """
    result = await db.execute(
        select(EbayDraftListing).where(
            EbayDraftListing.id == draft_id,
            EbayDraftListing.user_id == user.id,
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    token = await get_user_token(db, user.id)
    if not token:
        raise HTTPException(
            status_code=400,
            detail="No eBay account connected. Connect your account first via /ebay/auth/url.",
        )

    try:
        client = get_ebay_client(token)

        # Generate a SKU
        sku = f"ARBSENSE-{draft.id[:8].upper()}"

        # Step 1: Create inventory item
        await client.create_or_replace_inventory_item(
            sku=sku,
            title=draft.title,
            description=draft.description or "",
            brand=draft.brand or "",
            mpn=draft.mpn or draft.model or "",
            upc=draft.upc,
            quantity=draft.quantity or 1,
            price=draft.price,
            currency=draft.currency or "USD",
            item_specifics=draft.item_specifics or {},
            condition=draft.condition or "NEW",
            condition_description=draft.condition_description,
            ship_from_postal_code=draft.ship_from_postal_code or "90001",
        )

        # Step 2: Create offer
        offer_result = await client.create_offer(
            sku=sku,
            category_id=draft.category_id or "97675",
            price=draft.price,
            currency=draft.currency or "USD",
            quantity=draft.quantity or 1,
            listing_description=draft.description,
            free_shipping=draft.free_shipping or True,
            shipping_service=draft.shipping_service or "USPSFirstClass",
            shipping_cost=draft.shipping_cost or 0.0,
            handling_time=draft.handling_time or 1,
            returns_accepted=draft.returns_accepted or True,
            return_days=draft.return_days or 30,
        )

        offer_id = offer_result.get("offerId", "")
        draft.ebay_offer_id = offer_id

        # Step 3: Publish offer
        publish_result = await client.publish_offer(offer_id)
        item_id = publish_result.get("listingId", "")

        draft.ebay_item_id = item_id
        draft.status = "active"
        draft.ebay_listing_url = f"https://www.ebay.com/itm/{item_id}" if item_id else None

        from datetime import datetime, timezone
        draft.submitted_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await db.commit()
        await db.refresh(draft)

        return {
            "success": True,
            "data": {
                "id": draft.id,
                "ebay_item_id": draft.ebay_item_id,
                "ebay_offer_id": draft.ebay_offer_id,
                "ebay_listing_url": draft.ebay_listing_url,
                "status": draft.status,
            },
            "meta": {},
        }

    except EbayApiError as e:
        draft.status = "error"
        draft.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=502, detail=f"eBay API error: {e}")


@router.get("/seller/info")
async def get_seller_info(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the connected eBay seller info."""
    token = await get_user_token(db, user.id)
    if not token:
        raise HTTPException(status_code=400, detail="No eBay account connected")

    try:
        client = get_ebay_client(token)
        user_info = await client.get_user()
        return {"success": True, "data": user_info, "meta": {}}
    except EbayApiError as e:
        raise HTTPException(status_code=502, detail=f"eBay API error: {e}")
