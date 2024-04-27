"""Topup field

Revision ID: 620d5c0fdd20
Revises: 270220b141e8
Create Date: 2024-04-27 00:58:19.874554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '620d5c0fdd20'
down_revision = '270220b141e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('UPDATE message SET "isCleaned" = false WHERE "isCleaned" IS NULL')


def downgrade() -> None:
    pass
