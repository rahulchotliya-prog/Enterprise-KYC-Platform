"""initial migration

Revision ID: ee408b2c03f7
Revises: fd833d402a60
Create Date: 2026-05-11 13:11:27.478451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee408b2c03f7'
down_revision: Union[str, Sequence[str], None] = 'fd833d402a60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This migration is intentionally a no-op.
    # The schema is already created by the prior initial schema revision.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # No schema changes to undo here.
    pass
