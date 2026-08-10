"""create_expenses_table

Revision ID: c3d4e5f6a7b8
Revises: b7f8a9c0d1e2
Create Date: 2026-08-10 23:12:00.000000

Creates the expenses table for tracking batch-level costs
by category (feed, medication, equipment, labour, other).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b7f8a9c0d1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create expenses table."""
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('batches.id'), nullable=False, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('amount_zmw', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Drop expenses table."""
    op.drop_table('expenses')
