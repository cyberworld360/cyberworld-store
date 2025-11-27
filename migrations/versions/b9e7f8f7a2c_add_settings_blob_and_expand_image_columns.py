"""Add settings blob columns and expand image URL length

Revision ID: b9e7f8f7a2c
Revises: a54b6c8d9e2f
Create Date: 2025-11-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9e7f8f7a2c'
down_revision = 'a54b6c8d9e2f'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure image URL varchar fields are large enough for S3 URLs
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('logo_image', type_=sa.String(length=1000), existing_type=sa.String(length=300), nullable=True)
        batch_op.alter_column('banner1_image', type_=sa.String(length=1000), existing_type=sa.String(length=300), nullable=True)
        batch_op.alter_column('banner2_image', type_=sa.String(length=1000), existing_type=sa.String(length=300), nullable=True)
        batch_op.alter_column('bg_image', type_=sa.String(length=1000), existing_type=sa.String(length=300), nullable=True)

    # Add LargeBinary fields and mime types for settings images if missing
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('logo_image_data', sa.LargeBinary(), nullable=True))
        batch_op.add_column(sa.Column('banner1_image_data', sa.LargeBinary(), nullable=True))
        batch_op.add_column(sa.Column('banner2_image_data', sa.LargeBinary(), nullable=True))
        batch_op.add_column(sa.Column('bg_image_data', sa.LargeBinary(), nullable=True))
        batch_op.add_column(sa.Column('logo_image_mime', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('banner1_image_mime', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('banner2_image_mime', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('bg_image_mime', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('bg_image_mime')
        batch_op.drop_column('banner2_image_mime')
        batch_op.drop_column('banner1_image_mime')
        batch_op.drop_column('logo_image_mime')
        batch_op.drop_column('bg_image_data')
        batch_op.drop_column('banner2_image_data')
        batch_op.drop_column('banner1_image_data')
        batch_op.drop_column('logo_image_data')
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('bg_image', type_=sa.String(length=300), existing_type=sa.String(length=1000), nullable=True)
        batch_op.alter_column('banner2_image', type_=sa.String(length=300), existing_type=sa.String(length=1000), nullable=True)
        batch_op.alter_column('banner1_image', type_=sa.String(length=300), existing_type=sa.String(length=1000), nullable=True)
        batch_op.alter_column('logo_image', type_=sa.String(length=300), existing_type=sa.String(length=1000), nullable=True)
