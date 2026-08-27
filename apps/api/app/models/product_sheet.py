"""
Product sheet models.
Stores verified product data — the single source of truth for listing candidates.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.models import utcnow, gen_uuid


class ProductSheet(Base):
    """
    Verified product sheet — one per candidate product (multipack).
    Contains all verified specs, source data, and split strategy.
    Feeds into eBay draft listings via the sync endpoint.
    """
    __tablename__ = "product_sheets"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Core identity (VERIFIED)
    product_name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    mpn = Column(String, nullable=True)
    upc = Column(String, nullable=True)
    asin = Column(String, nullable=True)
    product_type = Column(String, nullable=True)  # e.g. "smoke_detector", "smart_plug", etc.

    # Source details
    source = Column(String, nullable=False, default="amazon")  # amazon | walmart | etc
    source_url = Column(String, nullable=True)
    pack_size = Column(Integer, nullable=True)  # number of identical units in pack
    pack_price = Column(Float, nullable=True)  # total cost of the pack
    cost_per_unit = Column(Float, nullable=True)  # pack_price / pack_size

    # Product specs
    color = Column(String, nullable=True)
    power_source = Column(String, nullable=True)
    sensor_type = Column(String, nullable=True)
    dimensions = Column(String, nullable=True)
    weight_lbs = Column(Float, nullable=True)
    certifications = Column(String, nullable=True)  # UL listed, etc.

    # Key features (JSON array of strings)
    features = Column(JSON, default=list)

    # Split strategy
    split_strategy = Column(Text, nullable=True)  # how to split and sell
    sell_individually = Column(Boolean, default=True)

    # Economics (estimated — real numbers come from eBay comps)
    estimated_ebay_price_per_unit = Column(Float, nullable=True)
    estimated_shipping_cost = Column(Float, nullable=True)
    estimated_net_profit_per_pack = Column(Float, nullable=True)
    estimated_roi = Column(Float, nullable=True)

    # Verification status
    verified_title = Column(Boolean, default=False)
    verified_pack_size = Column(Boolean, default=False)
    verified_price = Column(Boolean, default=False)
    verified_ebay_demand = Column(Boolean, default=False)
    overall_status = Column(String, nullable=False, default="pending")  # pending | verified | rejected | listed

    # Rejection reason (if rejected)
    rejection_reason = Column(Text, nullable=True)

    # eBay category suggestion
    suggested_ebay_category_id = Column(String, nullable=True)
    suggested_ebay_category_name = Column(String, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User")
