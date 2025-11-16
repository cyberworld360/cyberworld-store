"""Poll and POST to admin settings API until success or attempts exhausted.

Usage:
  python tools/poll_admin_api.py --url URL --token TOKEN --attempts 12 --interval 15
"""
import time
import argparse
import requests
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--token', required=True)
parser.add_argument('--attempts', type=int, default=12)
parser.add_argument('--interval', type=int, default=15)
parser.add_argument('--dashboard_layout', default='grid')
parser.add_argument('--seo_visible', choices=['true','false'], default='true')
parser.add_argument('--site_announcement', default='Automated update test from poll script')
args = parser.parse_args()

payload = {
    'dashboard_layout': args.dashboard_layout,
    'seo_visible': args.seo_visible.lower() == 'true',
    'site_announcement': args.site_announcement
}

headers = {'Content-Type': 'application/json', 'X-ADMIN-TOKEN': args.token}

for i in range(1, args.attempts + 1):
    print(f'Attempt {i}/{args.attempts} -> POST {args.url}')
    try:
        r = requests.post(args.url, headers=headers, json=payload, timeout=20)
        print('Status:', r.status_code)
        # Try to print JSON (safe)
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text[:2000])
        if r.status_code == 200:
            print('Success on attempt', i)
            sys.exit(0)
    except Exception as e:
        print('Request failed:', e)

    if i < args.attempts:
        print(f'Waiting {args.interval} seconds before next attempt...')
        time.sleep(args.interval)

print('All attempts exhausted, API not available or returning non-200 status')
sys.exit(2)
