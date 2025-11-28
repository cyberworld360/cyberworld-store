import requests
from urllib.parse import urljoin
import os

base = 'http://127.0.0.1:5000'
print('GET without token -> should be 403')
r = requests.get(urljoin(base, '/__last_error'))
print('status', r.status_code)
print('GET with token header -> should be 200')
r2 = requests.get(urljoin(base, '/__last_error'), headers={'X-ERROR-TOKEN': 'testtoken'})
print('status', r2.status_code)
print('content length', len(r2.text))
print(r2.text[:200])
