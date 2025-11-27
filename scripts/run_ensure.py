import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app, _ensure_settings_columns
with app.app_context():
    _ensure_settings_columns()
    print('Done _ensure_settings_columns()')
