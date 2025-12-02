#!/usr/bin/env python3
"""Helper script to run `vercel --prod` with env args from .env
This avoids PowerShell quoting issues when passing many --env flags.
"""
import subprocess
from pathlib import Path
import shlex
import os

env_file = Path('.env')
if not env_file.exists():
    raise SystemExit('.env file not found')

env_args = []
for line in env_file.read_text(encoding='utf-8').splitlines():
    line=line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k,v = line.split('=', 1)
    k=k.strip(); v=v.strip().strip('"').strip("'")
    env_args.extend(['--env', f"{k}={v}"])

# On Windows, use the vercel.cmd under %APPDATA%\npm if available to ensure the executable path is correct
vercel_cmd = None
if os.name == 'nt':
    appdata = os.environ.get('APPDATA')
    if appdata:
        candidate = Path(appdata) / 'npm' / 'vercel.cmd'
        if candidate.exists():
            vercel_cmd = str(candidate)
if not vercel_cmd:
    vercel_cmd = 'vercel'

cmd = [vercel_cmd, '--prod', '--confirm'] + env_args
print('Executing:', ' '.join(shlex.quote(x) for x in cmd))
subprocess.run(cmd, check=True)
