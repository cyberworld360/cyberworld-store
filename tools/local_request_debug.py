import os
os.environ['DATABASE_URL'] = 'sqlite:///./data.db'
os.environ['FORCE_EPHEMERAL'] = '1'
os.environ['FLASK_DEBUG'] = '1'

from app import app

with app.test_client() as c:
    resp = c.get('/')
    print('Status', resp.status)
    print('Headers', dict(resp.headers))
    # If we have debug info in content, print it
    print(resp.get_data(as_text=True)[:2000])
