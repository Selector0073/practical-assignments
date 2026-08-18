"""create weather table

Revision ID: 68839217c732
Revises:
Create Date: 2026-08-17 22:15:45.611483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68839217c732'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'weather',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('time', sa.DateTime()),
        sa.Column('temperature', sa.Float()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('weather')
