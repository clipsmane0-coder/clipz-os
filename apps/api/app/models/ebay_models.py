"""
eBay Sell API integration models.
Stores OAuth tokens and draft listings per user.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.models import utcnow, gen_uuid


class EbayToken(Base):
    """Per-user eBay OAuth token storage."""
    __tablename__ = "ebay_tokens"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    access_token_expires_at = Column(DateTime, nullable=False)
    refresh_token_expires_at = Column(DateTime, nullable=False)
    ebay_user_id = Column(String, nullable=True)
    ebay_env = Column(String, nullable=False, default="production")  # sandbox | production
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User")


class EbayDraftListing(Base):
    """eBay draft listing — one row per item to list."""
    __tablename__ = "ebay_draft_listings"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Product identity
    product_name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    mpn = Column(String, nullable=True)
    upc = Column(String, nullable=True)
    asin = Column(String, nullable=True)
    source_url = Column(String, nullable=True)

    # Listing data
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    category_id = Column(String, nullable=True)
    condition = Column(String, nullable=False, default="1000")  # 1000 = New
    condition_description = Column(String, nullable=True)

    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    quantity = Column(Integer, nullable=False, default=1)

    # Item specifics
    item_specifics = Column(JSON, default=dict)  # {"Brand": "First Alert", "Type": "...", ...}

    # Shipping
    shipping_service = Column(String, nullable=True)
    shipping_cost = Column(Float, nullable=True)
    free_shipping = Column(Boolean, default=True)
    handling_time = Column(Integer, default=1)
    ship_from_postal_code = Column(String, nullable=True)

    # Returns
    returns_accepted = Column(Boolean, default=True)
    return_policy = Column(String, nullable=True)
    return_days = Column(Integer, default=30)

    # Source / pack info
    pack_size = Column(Integer, nullable=True)
    cost_per_unit = Column(Float, nullable=True)
    pack_cost = Column(Float, nullable=True)
    estimated_ebay_fee = Column(Float, nullable=True)
    estimated_shipping_cost = Column(Float, nullable=True)
    estimated_net_profit = Column(Float, nullable=True)
    estimated_roi = Column(Float, nullable=True)

    # Status
    status = Column(String, nullable=False, default="draft")  # draft | submitted | active | error
    ebay_item_id = Column(String, nullable=True)  # eBay's item ID once created
    ebay_offer_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    ebay_listing_url = Column(String, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User")
