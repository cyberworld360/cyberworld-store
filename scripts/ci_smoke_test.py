import os
import sys
import requests
from urllib.parse import urljoin

# Script checks are run via the `main()` function below; avoid performing
# network calls or sys.exit during import so pytest can collect tests safely.

s = requests.Session()

def full(path, deploy_url):
    return urljoin(deploy_url.rstrip('/') + '/', path.lstrip('/'))

def main():
    DEPLOY_URL = os.environ.get('DEPLOY_URL') or os.environ.get('DEPLOY_URL'.upper())
    ADMIN_USER = os.environ.get('ADMIN_USER')
    ADMIN_PASS = os.environ.get('ADMIN_PASS')

    if not DEPLOY_URL:
        print('ERROR: DEPLOY_URL environment variable not set')
        # Return a non-zero code instead of exiting at import time
        return 2

    print('Checking root...')
    r = s.get(full('/', DEPLOY_URL))
    print('GET / ->', r.status_code)
    if r.status_code >= 400:
        print(r.text[:500])

    print('Checking health endpoint /admin/diag (may redirect if not logged in)')
    r = s.get(full('/admin/diag', DEPLOY_URL))
    print('/admin/diag ->', r.status_code)

    if ADMIN_USER and ADMIN_PASS:
        print('Attempting admin login...')
        login_url = full('/admin/login', DEPLOY_URL)
        # Try common form fields
        data = {'username': ADMIN_USER, 'password': ADMIN_PASS}
        r = s.post(login_url, data=data)
        print('POST /admin/login ->', r.status_code)
        if r.status_code in (302, 200):
            print('Login likely successful (status {})'.format(r.status_code))
            r = s.get(full('/admin/diag', DEPLOY_URL))
            print('/admin/diag after login ->', r.status_code)
        else:
            print('Login failed; trying email/password')
            data = {'email': ADMIN_USER, 'password': ADMIN_PASS}
            r = s.post(login_url, data=data)
            print('POST /admin/login (email) ->', r.status_code)
    else:
        print('Skipping admin login; ADMIN_USER/ADMIN_PASS not set')

    print('Requesting /admin/test-email (if accessible)')
    try:
        r = s.get(full('/admin/test-email', DEPLOY_URL))
        print('/admin/test-email ->', r.status_code)
        print(r.text[:500])
    except Exception as e:
        print('Error calling /admin/test-email:', e)

    print('Smoke tests complete')


if __name__ == '__main__':
    rc = main()
    sys.exit(rc if rc is not None else 0)
