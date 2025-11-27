#!/usr/bin/env python3
"""Set Vercel environment variables for the current project using the Vercel CLI.

Usage: python scripts/set_vercel_env.py [--env-file .env] [--targets production,preview]

This script requires the `vercel` CLI to be installed and the user to be logged in via `vercel login`.
It will attempt to skip existing env vars and only add variables that have non-empty values in the given env file.

Note: Values are read from `.env` — DO NOT PUT PRODUCTION SECRETS IN A COMMITTED `.env` FILE. Use .env locally only.
"""

import subprocess
from pathlib import Path
import argparse
import shlex

parser = argparse.ArgumentParser(description='Set Vercel environment variables from .env')
parser.add_argument('--env-file', default='.env', help='Path to .env file')
parser.add_argument('--targets', default='production,preview,development', help='Comma-separated targets')
parser.add_argument('--vars', default='', help='Comma-separated list of vars to set (default: common keys)')
parser.add_argument('--dry-run', action='store_true')

args = parser.parse_args()

env_path = Path(args.env_file)
if not env_path.exists():
    print(f"Env file not found: {env_path}")
    raise SystemExit(1)

# Read .env file
envs = {}
for line in env_path.read_text().splitlines():
    s = line.strip()
    if not s or s.startswith('#') or '=' not in s:
        continue
    k,v = s.split('=', 1)
    k=k.strip(); v=v.strip().strip('"').strip("'")
    if v:
        envs[k] = v

# Default variable list to add if --vars not provided
default_vars = [
    'PAYSTACK_SECRET_KEY', 'PAYSTACK_PUBLIC_KEY', 'PAYSTACK_CALLBACK_URL',
    'MAIL_SERVER','MAIL_PORT','MAIL_USERNAME','MAIL_PASSWORD','MAIL_USE_TLS','MAIL_USE_SSL','MAIL_DEFAULT_SENDER','ADMIN_EMAIL',
    'SENDGRID_API_KEY'
]

if args.vars:
    keys = [k.strip() for k in args.vars.split(',') if k.strip()]
else:
    keys = default_vars

targets = [t.strip() for t in args.targets.split(',') if t.strip()]

# List current env vars via the CLI and parse to identify names already set
print('Querying current Vercel environment variables (project context must be the current directory) ...')
try:
    completed = subprocess.run(['vercel','env','ls'], capture_output=True, text=True, check=False)
    existing_output = completed.stdout + completed.stderr
except FileNotFoundError:
    print('`vercel` CLI not found. Please install and login (vercel login).')
    raise SystemExit(1)

existing_vars = set()
for line in existing_output.splitlines():
    # Lines often look like: NAME  production  Value  ... - we'll pick names.
    parts = line.split()
    if not parts: continue
    name = parts[0].strip()
    # Skip table header lines
    if name.upper() == 'NAME' or name.startswith('-'):
        continue
    # Basic validation that name looks like an env var
    if name.isidentifier() and name in existing_output:
        existing_vars.add(name)

print('Existing env var names on Vercel (sample):', ', '.join(sorted(list(existing_vars))[:20]))

added = []
skipped = []
failed = []

for key in keys:
    if key not in envs:
        print(f'Skipping {key}: not present in {args.env_file} or empty')
        skipped.append(key)
        continue
    value = envs[key]
    if key in existing_vars:
        print(f'Skipping {key}: already exists on Vercel (skipped)')
        skipped.append(key)
        continue

    for target in targets:
        cmd = ['vercel', 'env', 'add', key, target]
        print('=>', shlex.join(cmd))
        if args.dry_run:
            print('DRY RUN: not executing')
            continue
        # Run vercel env add and feed the value via stdin
        try:
            proc = subprocess.run(cmd, input=value + '\n', text=True, capture_output=True, check=False)
            if proc.returncode == 0:
                print(f'Added {key} for {target}')
                added.append((key, target))
            else:
                print(f'Failed to add {key} for {target}. stdout/stderr follows:')
                print(proc.stdout)
                print(proc.stderr)
                failed.append((key, target, proc.stdout + proc.stderr))
        except Exception as e:
            print(f'Error calling vercel CLI for {key} / {target}: {e}')
            failed.append((key, target, str(e)))

print('\nDone. Summary:')
print('Added: ', added)
print('Skipped: ', skipped)
print('Failed: ', failed)
print('\nIf you want these set on GitHub as secrets (for CI), set them in GitHub repo settings -> Secrets -> Actions (recommended).')
