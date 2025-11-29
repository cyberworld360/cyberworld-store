import time
import requests

for i in range(10):
    try:
        r = requests.get('http://127.0.0.1:5000/')
        print('ready', r.status_code)
        break
    except Exception as e:
        print('waiting...', e)
        time.sleep(1)
else:
    print('server not responding')