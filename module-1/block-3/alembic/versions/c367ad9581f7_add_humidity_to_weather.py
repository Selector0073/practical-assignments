"""add humidity to weather

Revision ID: c367ad9581f7
Revises: 68839217c732
Create Date: 2026-08-17 22:16:30.791630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c367ad9581f7'
down_revision: Union[str, Sequence[str], None] = '68839217c732'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('weather', sa.Column('humidity', sa.Float()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('weather', 'humidity')
