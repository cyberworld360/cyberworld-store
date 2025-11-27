"""Add logo and header settings fields to Settings

Revision ID: a54b6c8d9e2f
Revises: 9f3a8b2c1d4e
Create Date: 2025-11-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a54b6c8d9e2f'
down_revision = '9f3a8b2c1d4e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('logo_height', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('logo_top_px', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('logo_zindex', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('cart_on_right', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('custom_css', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('custom_css')
        batch_op.drop_column('cart_on_right')
        batch_op.drop_column('logo_zindex')
        batch_op.drop_column('logo_top_px')
        batch_op.drop_column('logo_height')
