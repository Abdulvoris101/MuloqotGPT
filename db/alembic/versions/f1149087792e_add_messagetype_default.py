"""ADD messageType default

Revision ID: f1149087792e
Revises: 5dfd9351842e
Create Date: 2024-04-19 17:39:48.329020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1149087792e'
down_revision = '5dfd9351842e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('UPDATE message SET "messageType" = \'message\' WHERE "messageType" IS NULL')


def downgrade() -> None:
    pass
