"""Test client for admin settings API (GET to check, then POST to update).

Usage:
  python tools/test_admin_api.py --url BASE_URL --token TOKEN [--get] [--post] [--data KEY=VALUE ...]
"""
import argparse
import requests
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True, help='Base URL (e.g., https://www.cyberworldstore.shop)')
parser.add_argument('--token', required=True, help='Admin API token')
parser.add_argument('--get', action='store_true', help='GET current settings')
parser.add_argument('--post', action='store_true', help='POST updates to settings')
parser.add_argument('--dashboard_layout', help='Dashboard layout (grid or list)')
parser.add_argument('--seo_visible', choices=['true','false'], help='SEO visible')
parser.add_argument('--seo_checklist_done', choices=['true','false'], help='SEO checklist done')
parser.add_argument('--site_announcement', help='Site announcement text')
parser.add_argument('--attempts', type=int, default=1, help='Number of attempts for polling')
parser.add_argument('--interval', type=int, default=5, help='Seconds between attempts')

args = parser.parse_args()

# Default: do both GET and POST if neither specified
if not args.get and not args.post:
    args.get = True
    args.post = True

base_url = args.url.rstrip('/')
api_url = f'{base_url}/admin/settings/api'
headers = {'Content-Type': 'application/json', 'X-ADMIN-TOKEN': args.token}

# Build POST payload
payload = {}
if args.dashboard_layout:
    payload['dashboard_layout'] = args.dashboard_layout
if args.seo_visible is not None:
    payload['seo_visible'] = args.seo_visible.lower() == 'true'
if args.seo_checklist_done is not None:
    payload['seo_checklist_done'] = args.seo_checklist_done.lower() == 'true'
if args.site_announcement:
    payload['site_announcement'] = args.site_announcement

import time

for attempt in range(1, args.attempts + 1):
    print(f'\n=== Attempt {attempt}/{args.attempts} ===')
    
    if args.get:
        print(f'GET {api_url}')
        try:
            r = requests.get(api_url, headers=headers, timeout=20)
            print(f'Status: {r.status_code}')
            try:
                result = r.json()
                print(json.dumps(result, indent=2))
                if r.status_code == 200:
                    print('✓ GET successful')
            except Exception:
                print(r.text[:500])
        except Exception as e:
            print(f'GET failed: {e}')
    
    if args.post and payload:
        print(f'\nPOST {api_url}')
        print(f'Payload: {json.dumps(payload, indent=2)}')
        try:
            r = requests.post(api_url, headers=headers, json=payload, timeout=20)
            print(f'Status: {r.status_code}')
            try:
                result = r.json()
                print(json.dumps(result, indent=2))
                if r.status_code == 200:
                    print('✓ POST successful')
            except Exception:
                print(r.text[:500])
        except Exception as e:
            print(f'POST failed: {e}')
    
    if attempt < args.attempts:
        print(f'\nWaiting {args.interval} seconds before next attempt...')
        time.sleep(args.interval)

print('\nDone.')
