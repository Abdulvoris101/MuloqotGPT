"""Add default values

Revision ID: 8ae2396992ad
Create Date: 2024-04-19 15:20:24.401480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ae2396992ad'
down_revision = '48df0e6baa74'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('UPDATE chat_activity SET "translatedMessagesCount" = 0 WHERE "translatedMessagesCount" IS NULL')


def downgrade() -> None:
    pass
