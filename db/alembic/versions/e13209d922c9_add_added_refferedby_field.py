"""ADD: added refferedBy field

Revision ID: e13209d922c9
Revises: 620d5c0fdd20
Create Date: 2024-04-27 12:14:21.435005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e13209d922c9'
down_revision = '620d5c0fdd20'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat', sa.Column('referredBy', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat', 'referredBy')
    # ### end Alembic commands ###