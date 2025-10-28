"""Add port to camera model

Revision ID: 5504bd12b11a
Revises: 
Create Date: 2025-09-17 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5504bd12b11a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('cameras', sa.Column('port', sa.Integer(), nullable=False, server_default='554'))


def downgrade() -> None:
    op.drop_column('cameras', 'port')