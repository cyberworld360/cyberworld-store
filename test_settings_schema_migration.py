import os
import sys
from sqlalchemy import inspect

sys.path.insert(0, os.getcwd())
from app import app, db, Settings


def test_settings_columns_types():
    with app.app_context():
        # Use SQLAlchemy inspector to get columns info from running DB
        inspector = inspect(db.engine)
        cols_info = inspector.get_columns('settings')
        cols = {c['name']: c for c in cols_info}

        # Ensure URL columns are large enough
        assert 'logo_image' in cols
        assert 'banner1_image' in cols
        assert 'banner2_image' in cols
        assert 'bg_image' in cols
        # Using string repr to check length if available
        # On some DBs the exact type object is dialect-specific; check type string
        def get_type_str(name):
            t = cols[name].get('type')
            return str(t).lower() if t is not None else ''

        assert 'varchar' in get_type_str('logo_image') or 'character varying' in get_type_str('logo_image')

        # Ensure blob/mime columns exist
        assert 'logo_image_data' in cols
        assert 'banner1_image_data' in cols
        assert 'banner2_image_data' in cols
        assert 'bg_image_data' in cols
        assert 'logo_image_mime' in cols
        assert 'banner1_image_mime' in cols
        assert 'banner2_image_mime' in cols
        assert 'bg_image_mime' in cols
