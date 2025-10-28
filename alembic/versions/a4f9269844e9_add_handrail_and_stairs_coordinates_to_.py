"""Add handrail and stairs coordinates to Camera model

Revision ID: a4f9269844e9
Revises: 5504bd12b11a
Create Date: 2025-09-19 10:27:39.672819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4f9269844e9'
down_revision: Union[str, Sequence[str], None] = '5504bd12b11a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cameras', sa.Column('handrail_coordinates', sa.JSON(), nullable=True))
    op.add_column('cameras', sa.Column('stairs_coordinates', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('cameras', 'stairs_coordinates')
    op.drop_column('cameras', 'handrail_coordinates')