import sys
from pathlib import Path
proj_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))

from app import app, db

with app.test_client() as c:
    # GET login page first
    r = c.get('/admin/login')
    print('GET /admin/login', r.status_code)
    # Post login
    r2 = c.post('/admin/login', data={'username':'admin','password':'GITG360'}, follow_redirects=True)
    print('POST /admin/login', r2.status_code)
    # Print final path
    print('Final URL after login POST (test client):', r2.request.path if hasattr(r2, 'request') else 'N/A')
    # Check if 'Logged in as admin.' in response data
    txt = r2.get_data(as_text=True)
    if 'Logged in as admin.' in txt:
        print('Login message present in response body')
    else:
        print('Login message NOT present; response body snippets:')
        print(txt[:800])
