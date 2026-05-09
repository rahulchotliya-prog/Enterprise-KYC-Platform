"""create users table

Revision ID: d0ac6cdc727e
Revises: 1945a6217854
Create Date: 2026-05-09 16:16:52.628413

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = 'd0ac6cdc727e'
down_revision: Union[str, Sequence[str], None] = '1945a6217854'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
