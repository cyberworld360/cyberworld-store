import os
import sqlite3
from urllib.parse import urlparse

def get_sqlite_path(database_url: str) -> str:
    # Expect formats like sqlite:///./data.db or sqlite:////absolute/path.db
    if not database_url.startswith('sqlite:'):
        raise RuntimeError('Not a sqlite database URL')
    path = database_url.replace('sqlite:///', '')
    return os.path.abspath(path)

def ensure_product_created_at(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(product);")
    cols = [r[1] for r in cur.fetchall()]
    if 'created_at' in cols:
        print('created_at column already present')
    else:
        print('Adding created_at column to product table')
        cur.execute("ALTER TABLE product ADD COLUMN created_at DATETIME DEFAULT (CURRENT_TIMESTAMP);")
        conn.commit()
        print('created_at column added')
    conn.close()

if __name__ == '__main__':
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///./data.db')
    try:
        sqlite_path = get_sqlite_path(db_url)
    except Exception as e:
        print('Skipping: not a sqlite DB or invalid DATABASE_URL:', e)
    else:
        if not os.path.exists(sqlite_path):
            print('SQLite DB not found, creating new DB at', sqlite_path)
            open(sqlite_path, 'a').close()
        ensure_product_created_at(sqlite_path)