import os
import sqlite3

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'data.db')

if not os.path.exists(DB_PATH):
    print('No SQLite DB found at', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)

try:
    cur.execute("SELECT version_num FROM alembic_version")
    row = cur.fetchone()
    print('alembic_version:', row[0] if row else 'None')
except Exception as e:
    print('alembic_version: error -', e)

conn.close()
