"""add_financial_fields_to_inventory

Revision ID: b7f8a9c0d1e2
Revises: a1b2c3d4e5f6
Create Date: 2026-08-10 23:10:00.000000

Adds financial tracking columns to inventory_adjustments:
- unit_price_zmw: price per bird in ZMW (sales only)
- buyer_name: optional buyer name for audit trail
- total_amount_zmw: computed total (quantity * unit_price)

All columns are nullable so existing rows are not broken.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f8a9c0d1e2'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add financial columns to inventory_adjustments table."""
    op.add_column(
        'inventory_adjustments',
        sa.Column('unit_price_zmw', sa.Float(), nullable=True)
    )
    op.add_column(
        'inventory_adjustments',
        sa.Column('buyer_name', sa.String(), nullable=True)
    )
    op.add_column(
        'inventory_adjustments',
        sa.Column('total_amount_zmw', sa.Float(), nullable=True)
    )


def downgrade() -> None:
    """Remove financial columns from inventory_adjustments table."""
    op.drop_column('inventory_adjustments', 'total_amount_zmw')
    op.drop_column('inventory_adjustments', 'buyer_name')
    op.drop_column('inventory_adjustments', 'unit_price_zmw')
