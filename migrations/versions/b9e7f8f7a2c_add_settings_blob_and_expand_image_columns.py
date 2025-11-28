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
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing = {c['name']: c for c in insp.get_columns('settings')}
    with op.batch_alter_table('settings', schema=None) as batch_op:
        # Only alter if the column exists and its current type/length is smaller
        if 'logo_image' in existing:
            # best-effort: try to alter, some dialects may ignore if same type
            batch_op.alter_column('logo_image', type_=sa.String(length=1000), existing_type=sa.String(length=getattr(existing['logo_image']['type'], 'length', None)), nullable=True)
        else:
            # If the column does not exist, add it
            batch_op.add_column(sa.Column('logo_image', sa.String(length=1000), nullable=True))
        if 'banner1_image' in existing:
            batch_op.alter_column('banner1_image', type_=sa.String(length=1000), existing_type=sa.String(length=getattr(existing['banner1_image']['type'], 'length', None)), nullable=True)
        else:
            batch_op.add_column(sa.Column('banner1_image', sa.String(length=1000), nullable=True))
        if 'banner2_image' in existing:
            batch_op.alter_column('banner2_image', type_=sa.String(length=1000), existing_type=sa.String(length=getattr(existing['banner2_image']['type'], 'length', None)), nullable=True)
        else:
            batch_op.add_column(sa.Column('banner2_image', sa.String(length=1000), nullable=True))
        if 'bg_image' in existing:
            batch_op.alter_column('bg_image', type_=sa.String(length=1000), existing_type=sa.String(length=getattr(existing['bg_image']['type'], 'length', None)), nullable=True)
        else:
            batch_op.add_column(sa.Column('bg_image', sa.String(length=1000), nullable=True))

    # Add LargeBinary fields and mime types for settings images if missing
    with op.batch_alter_table('settings', schema=None) as batch_op:
        if 'logo_image_data' not in existing:
            batch_op.add_column(sa.Column('logo_image_data', sa.LargeBinary(), nullable=True))
        if 'banner1_image_data' not in existing:
            batch_op.add_column(sa.Column('banner1_image_data', sa.LargeBinary(), nullable=True))
        if 'banner2_image_data' not in existing:
            batch_op.add_column(sa.Column('banner2_image_data', sa.LargeBinary(), nullable=True))
        if 'bg_image_data' not in existing:
            batch_op.add_column(sa.Column('bg_image_data', sa.LargeBinary(), nullable=True))
        if 'logo_image_mime' not in existing:
            batch_op.add_column(sa.Column('logo_image_mime', sa.String(length=100), nullable=True))
        if 'banner1_image_mime' not in existing:
            batch_op.add_column(sa.Column('banner1_image_mime', sa.String(length=100), nullable=True))
        if 'banner2_image_mime' not in existing:
            batch_op.add_column(sa.Column('banner2_image_mime', sa.String(length=100), nullable=True))
        if 'bg_image_mime' not in existing:
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
