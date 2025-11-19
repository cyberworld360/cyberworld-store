import os
import sys
from sqlalchemy import create_engine, text

url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
if not url:
    print('ERROR: DATABASE_URL not set', file=sys.stderr)
    sys.exit(2)
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('DB connectivity OK')
except Exception as e:
    print('DB connectivity FAILED:', e, file=sys.stderr)
    sys.exit(3)
