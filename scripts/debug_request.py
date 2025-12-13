import os
import sys
import traceback

# Ensure project root is on sys.path so `from app import app` works when running this script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

app.config['TESTING'] = True
app.config['DEBUG'] = True

def debug_path(path='/'):
    with app.test_client() as c:
        try:
            resp = c.get(path)
            print('PATH:', path)
            print('STATUS:', resp.status_code)
            data = resp.get_data(as_text=True)
            print('RESPONSE (truncated 1000 chars):')
            print(data[:1000])
        except Exception:
            print('EXCEPTION while requesting', path)
            traceback.print_exc()

if __name__ == '__main__':
    # Test the homepage and a few common endpoints
    for p in ['/', '/cart', '/product/1']:
        print('\n' + '='*80)
        debug_path(p)