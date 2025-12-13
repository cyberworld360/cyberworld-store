import os
import sqlite3

db_url = os.environ.get('DATABASE_URL', 'sqlite:///./data.db')
if not db_url.startswith('sqlite:'):
    print('Not sqlite DB:', db_url)
    raise SystemExit(1)
path = db_url.replace('sqlite:///', '')
path = os.path.abspath(path)
print('Inspecting DB at', path)
if not os.path.exists(path):
    print('DB file does not exist')
    raise SystemExit(1)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)
for t in tables:
    print('\nPRAGMA table_info(%s):' % t)
    cur.execute(f"PRAGMA table_info({t});")
    for r in cur.fetchall():
        print(r)
conn.close()