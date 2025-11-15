"""Simple client to POST JSON settings to /admin/settings/api using an admin token.

Usage:
  python tools/set_admin_settings_api.py --url https://example.com/admin/settings/api --token YOURTOKEN \
    --dashboard_layout grid --seo_visible true --site_announcement "Hello"

If --token omitted, script will read ADMIN_API_TOKEN from env.
"""
import os
import argparse
import requests
import json

parser = argparse.ArgumentParser(description='Post JSON settings to admin settings API')
parser.add_argument('--url', required=False, default=os.environ.get('ADMIN_SETTINGS_API_URL', 'http://127.0.0.1:5000/admin/settings/api'), help='Full URL to /admin/settings/api')
parser.add_argument('--token', required=False, help='Admin API token (or set ADMIN_API_TOKEN env var)')
parser.add_argument('--dashboard_layout', choices=['grid','list'], help='Dashboard layout')
parser.add_argument('--primary_color', help='Primary color (e.g. #27ae60)')
parser.add_argument('--secondary_color', help='Secondary color')
parser.add_argument('--primary_font', help='Primary font')
parser.add_argument('--secondary_font', help='Secondary font')
parser.add_argument('--seo_visible', choices=['true','false'], help='SEO visibility')
parser.add_argument('--seo_checklist_done', choices=['true','false'], help='SEO checklist done')
parser.add_argument('--site_announcement', help='Site announcement HTML/text')
args = parser.parse_args()

token = args.token or os.environ.get('ADMIN_API_TOKEN')
if not token:
    print('Warning: no admin token provided; request will require an active admin session.')

payload = {}
if args.dashboard_layout:
    payload['dashboard_layout'] = args.dashboard_layout
if args.primary_color:
    payload['primary_color'] = args.primary_color
if args.secondary_color:
    payload['secondary_color'] = args.secondary_color
if args.primary_font:
    payload['primary_font'] = args.primary_font
if args.secondary_font:
    payload['secondary_font'] = args.secondary_font
if args.seo_visible is not None:
    payload['seo_visible'] = args.seo_visible.lower() == 'true'
if args.seo_checklist_done is not None:
    payload['seo_checklist_done'] = args.seo_checklist_done.lower() == 'true'
if args.site_announcement is not None:
    payload['site_announcement'] = args.site_announcement

print('Posting to', args.url)
headers = {'Content-Type': 'application/json'}
if token:
    headers['X-ADMIN-TOKEN'] = token

try:
    r = requests.post(args.url, headers=headers, json=payload, timeout=20)
    print('Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text[:2000])
except Exception as e:
    print('Request failed:', e)
