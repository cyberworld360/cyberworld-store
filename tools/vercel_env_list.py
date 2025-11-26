"""
Simple helper to list Vercel project environment variables via the Vercel API.

Usage:
  python tools/vercel_env_list.py --token <VERCEL_TOKEN> --project <PROJECT_ID_OR_NAME>

This prints the key, target, id, and a masked value (first/last 4 chars) for each env var.
"""
import argparse
import json
import sys
import requests

API_BASE = "https://api.vercel.com"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--token", required=True, help="Vercel API token (VERCEL_TOKEN)")
    p.add_argument("--project", required=True, help="Vercel project ID or slug")
    return p.parse_args()


def main():
    args = parse_args()
    token = args.token
    project = args.project
    url = f"{API_BASE}/v9/projects/{project}/env"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"Failed to list env vars: {resp.status_code} {resp.text}")
        return 1
    data = resp.json()
    items = data.get("envs", [])
    if not items:
        print("No environment variables found")
        return 0
    print(f"Found {len(items)} env vars")
    for item in items:
        key = item.get("key")
        env_id = item.get("id")
        target = item.get("target", [])
        v = item.get("value") or ""
        masked = "" if not v else (v[:4] + '...' + v[-4:] if len(v) > 12 else v)
        print(f"- {key} (id={env_id}) target={target} value={masked}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
