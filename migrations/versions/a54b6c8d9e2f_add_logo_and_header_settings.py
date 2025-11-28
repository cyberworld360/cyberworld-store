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
    # Add new header/logo columns if missing
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_cols = {c['name'] for c in insp.get_columns('settings')}
    with op.batch_alter_table('settings', schema=None) as batch_op:
        if 'logo_height' not in existing_cols:
            batch_op.add_column(sa.Column('logo_height', sa.Integer(), nullable=True))
        if 'logo_top_px' not in existing_cols:
            batch_op.add_column(sa.Column('logo_top_px', sa.Integer(), nullable=True))
        if 'logo_zindex' not in existing_cols:
            batch_op.add_column(sa.Column('logo_zindex', sa.Integer(), nullable=True))
        if 'cart_on_right' not in existing_cols:
            batch_op.add_column(sa.Column('cart_on_right', sa.Boolean(), nullable=True))
        if 'custom_css' not in existing_cols:
            batch_op.add_column(sa.Column('custom_css', sa.Text(), nullable=True))


def downgrade():
    # Only drop columns if they exist
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_cols = {c['name'] for c in insp.get_columns('settings')}
    with op.batch_alter_table('settings', schema=None) as batch_op:
        if 'custom_css' in existing_cols:
            batch_op.drop_column('custom_css')
        if 'cart_on_right' in existing_cols:
            batch_op.drop_column('cart_on_right')
        if 'logo_zindex' in existing_cols:
            batch_op.drop_column('logo_zindex')
        if 'logo_top_px' in existing_cols:
            batch_op.drop_column('logo_top_px')
        if 'logo_height' in existing_cols:
            batch_op.drop_column('logo_height')
