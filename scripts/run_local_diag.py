import os
import sys

# Set a temporary DIAG_TOKEN for local diagnostic run
os.environ.setdefault('DIAG_TOKEN', os.environ.get('DIAG_TOKEN', 'local-test-token'))

from app import app


def run():
    token = os.environ.get('DIAG_TOKEN')
    if not token:
        print('DIAG_TOKEN not set; set DIAG_TOKEN env var and retry')
        sys.exit(1)

    with app.test_client() as c:
        resp = c.get(f'/admin/diag-env?token={token}')
        print('Local /admin/diag-env status:', resp.status_code)
        try:
            print(resp.get_data(as_text=True))
        except Exception:
            print('Could not decode response body')


if __name__ == '__main__':
    run()
