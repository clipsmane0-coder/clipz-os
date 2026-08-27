"""Add eBay tokens, draft listings, and product sheets tables

Revision ID: f23a9c7b1d4e
Revises: e6b30fb48689
Create Date: 2026-08-27 15:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'f23a9c7b1d4e'
down_revision = 'e6b30fb48689'
branch_labels = None
depends_on = None


def upgrade():
    # eBay tokens
    op.create_table(
        'ebay_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('access_token_expires_at', sa.DateTime(), nullable=False),
        sa.Column('refresh_token_expires_at', sa.DateTime(), nullable=False),
        sa.Column('ebay_user_id', sa.String(), nullable=True),
        sa.Column('ebay_env', sa.String(), nullable=False, default='production'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ebay_tokens_user_id', 'ebay_tokens', ['user_id'])

    # eBay draft listings
    op.create_table(
        'ebay_draft_listings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('mpn', sa.String(), nullable=True),
        sa.Column('upc', sa.String(), nullable=True),
        sa.Column('asin', sa.String(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('subtitle', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_id', sa.String(), nullable=True),
        sa.Column('condition', sa.String(), nullable=False, default='1000'),
        sa.Column('condition_description', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False, default='USD'),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('item_specifics', sa.JSON(), nullable=True),
        sa.Column('shipping_service', sa.String(), nullable=True),
        sa.Column('shipping_cost', sa.Float(), nullable=True),
        sa.Column('free_shipping', sa.Boolean(), default=True),
        sa.Column('handling_time', sa.Integer(), default=1),
        sa.Column('ship_from_postal_code', sa.String(), nullable=True),
        sa.Column('returns_accepted', sa.Boolean(), default=True),
        sa.Column('return_policy', sa.String(), nullable=True),
        sa.Column('return_days', sa.Integer(), default=30),
        sa.Column('pack_size', sa.Integer(), nullable=True),
        sa.Column('cost_per_unit', sa.Float(), nullable=True),
        sa.Column('pack_cost', sa.Float(), nullable=True),
        sa.Column('estimated_ebay_fee', sa.Float(), nullable=True),
        sa.Column('estimated_shipping_cost', sa.Float(), nullable=True),
        sa.Column('estimated_net_profit', sa.Float(), nullable=True),
        sa.Column('estimated_roi', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='draft'),
        sa.Column('ebay_item_id', sa.String(), nullable=True),
        sa.Column('ebay_offer_id', sa.String(), nullable=True),
        sa.Column('ebay_listing_url', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ebay_draft_listings_user_id', 'ebay_draft_listings', ['user_id'])

    # Product sheets
    op.create_table(
        'product_sheets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('mpn', sa.String(), nullable=True),
        sa.Column('upc', sa.String(), nullable=True),
        sa.Column('asin', sa.String(), nullable=True),
        sa.Column('product_type', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=False, default='amazon'),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('pack_size', sa.Integer(), nullable=True),
        sa.Column('pack_price', sa.Float(), nullable=True),
        sa.Column('cost_per_unit', sa.Float(), nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('power_source', sa.String(), nullable=True),
        sa.Column('sensor_type', sa.String(), nullable=True),
        sa.Column('dimensions', sa.String(), nullable=True),
        sa.Column('weight_lbs', sa.Float(), nullable=True),
        sa.Column('certifications', sa.String(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('split_strategy', sa.Text(), nullable=True),
        sa.Column('sell_individually', sa.Boolean(), default=True),
        sa.Column('estimated_ebay_price_per_unit', sa.Float(), nullable=True),
        sa.Column('estimated_shipping_cost', sa.Float(), nullable=True),
        sa.Column('estimated_net_profit_per_pack', sa.Float(), nullable=True),
        sa.Column('estimated_roi', sa.Float(), nullable=True),
        sa.Column('verified_title', sa.Boolean(), default=False),
        sa.Column('verified_pack_size', sa.Boolean(), default=False),
        sa.Column('verified_price', sa.Boolean(), default=False),
        sa.Column('verified_ebay_demand', sa.Boolean(), default=False),
        sa.Column('overall_status', sa.String(), nullable=False, default='pending'),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('suggested_ebay_category_id', sa.String(), nullable=True),
        sa.Column('suggested_ebay_category_name', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_product_sheets_user_id', 'product_sheets', ['user_id'])


def downgrade():
    op.drop_index('ix_product_sheets_user_id', 'product_sheets')
    op.drop_table('product_sheets')
    op.drop_index('ix_ebay_draft_listings_user_id', 'ebay_draft_listings')
    op.drop_table('ebay_draft_listings')
    op.drop_index('ix_ebay_tokens_user_id', 'ebay_tokens')
    op.drop_table('ebay_tokens')
