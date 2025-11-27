import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    try:
        inspector = inspect(db.engine)
        cols = inspector.get_columns('settings')
        print('Settings table columns:')
        for c in cols:
            print(c['name'], c.get('type'))
    except Exception as e:
        print('Failed to inspect settings table:', e)
