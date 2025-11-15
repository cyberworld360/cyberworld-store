import sys
from pathlib import Path

# Ensure project root is on sys.path
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))

from app import app, db, AdminUser

with app.app_context():
    users = AdminUser.query.all()
    if not users:
        print('No AdminUser records found')
    else:
        for u in users:
            print(f'AdminUser id={u.id} username={u.username} password_hash_present={bool(u.password_hash)}')
