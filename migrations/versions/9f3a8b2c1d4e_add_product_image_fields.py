"""Add product_image_data and product_image_mime to Product

Revision ID: 9f3a8b2c1d4e
Revises: 422e58176fdc
Create Date: 2025-11-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f3a8b2c1d4e'
down_revision = '422e58176fdc'
branch_labels = None
depends_on = None


def upgrade():
    # Add binary column for product image data and mime type (only if missing)
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_cols = {c['name'] for c in insp.get_columns('product')}
    with op.batch_alter_table('product', schema=None) as batch_op:
        if 'product_image_data' not in existing_cols:
            batch_op.add_column(sa.Column('product_image_data', sa.LargeBinary(), nullable=True))
        if 'product_image_mime' not in existing_cols:
            batch_op.add_column(sa.Column('product_image_mime', sa.String(length=100), nullable=True))


def downgrade():
    # Remove the columns on downgrade
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('product_image_mime')
        batch_op.drop_column('product_image_data')
