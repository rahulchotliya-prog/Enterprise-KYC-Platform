"""create users table

Revision ID: 1945a6217854
Revises: b246d93611c5
Create Date: 2026-05-09 16:16:06.080638

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '1945a6217854'
down_revision: Union[str, Sequence[str], None] = 'b246d93611c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
