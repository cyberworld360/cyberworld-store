"""
Simple helper to create/update Vercel project environment variables via the Vercel API.

Usage:
  python tools/vercel_env_api.py --token <VERCEL_TOKEN> --project <PROJECT_ID_OR_NAME> --env-file vercel_env.json

The env file should be a JSON object of key -> value pairs, e.g.
{
  "SECRET_KEY": "your-secret",
  "PAYSTACK_PUBLIC_KEY": "pk_test_...",
  "PAYSTACK_SECRET_KEY": "sk_test_..."
}

Note: You must provide a Vercel token with permissions for the target project. This script targets the Vercel REST API v9 endpoint and will attempt to create the env var for the "production" target.
"""
import argparse
import json
import os
import sys
import time

import requests


API_BASE = "https://api.vercel.com"


def load_env_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def upsert_env_var(token, project, key, value, target=("production",)):
    url = f"{API_BASE}/v9/projects/{project}/env"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # Vercel API requires a `type` attribute indicating how the var should be stored
    # Acceptable values: "plain" or "encrypted". For secrets, use "encrypted".
    payload = {"key": key, "value": value, "target": list(target), "type": "encrypted"}
    # Try to find an existing var with the same key and target and update it if present
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            items = r.json().get("envs", [])
            for item in items:
                if item.get("key") == key and set(item.get("target", [])) == set(list(target)):
                    # update existing env var
                    env_id = item.get("id")
                    update_url = f"{url}/{env_id}"
                    resp = requests.patch(update_url, headers=headers, json=payload, timeout=30)
                    return resp
    except Exception:
        # if listing fails, fall back to attempting to create
        pass

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    return resp


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--token", required=True, help="Vercel API token (VERCEL_TOKEN)")
    p.add_argument("--project", required=True, help="Vercel project ID or slug")
    p.add_argument("--env-file", required=True, help="Path to JSON file with env vars")
    p.add_argument("--dry-run", action="store_true", help="Show intended operations without calling API")
    return p.parse_args()


def main():
    args = parse_args()
    token = args.token
    project = args.project
    envs = load_env_file(args.env_file)

    print(f"Loaded {len(envs)} env vars from {args.env_file}")
    if args.dry_run:
        for k, v in envs.items():
            print(f"DRY RUN: would set {k} for project {project}")
        return 0

    for k, v in envs.items():
        print(f"Setting {k}...", end=" ")
        try:
            r = upsert_env_var(token, project, k, v)
        except Exception as e:
            print(f"failed: {e}")
            continue

        if r.status_code in (200,201):
            print("ok")
        else:
            print(f"error {r.status_code}: {r.text}")
            # be polite to the API if we hit rate limits
            if r.status_code == 429:
                time.sleep(1)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
