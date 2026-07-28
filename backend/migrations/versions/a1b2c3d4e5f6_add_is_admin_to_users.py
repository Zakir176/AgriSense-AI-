"""add_is_admin_to_users

Revision ID: a1b2c3d4e5f6
Revises: 4651dc0f7af9
Create Date: 2026-07-28 10:53:00.000000

Adds the is_admin boolean column to the users table.
Existing rows default to FALSE (non-admin).
The seeded 'operator' user is promoted to admin at runtime via the startup seed function.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '4651dc0f7af9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_admin column to users table."""
    op.add_column(
        'users',
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false())
    )


def downgrade() -> None:
    """Remove is_admin column from users table."""
    op.drop_column('users', 'is_admin')
