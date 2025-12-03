#!/usr/bin/env python3
"""
Vercel deployment automation script
This script sets up and deploys the Flask app to Vercel automatically
"""

import os
import subprocess
import sys
import platform
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command with error handling"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    # Present the command in a readable form
    if isinstance(cmd, (list, tuple)):
        display_cmd = ' '.join(cmd)
    else:
        display_cmd = cmd
    print(f"$ {display_cmd}\n")

    # If cmd is a sequence already, prefer shell=False to avoid MSYS/sh involvement on Windows
    try:
        shell_flag = False
        run_args = {}
        if isinstance(cmd, (list, tuple)):
            run_target = cmd
            shell_flag = False
        else:
            # If the command contains shell-only operators, run via shell=True
            shell_ops = ['&&', '||', '|', '>', '<']
            if any(op in cmd for op in shell_ops):
                run_target = cmd
                shell_flag = True
            else:
                # Split the command into args for shell-free execution (safer on Windows)
                run_target = cmd.split()
                shell_flag = False

        # Capture stdout/stderr for diagnostic output
        result = subprocess.run(run_target, shell=shell_flag, capture_output=True, text=True)
        if result.stdout:
            print("--- stdout ---")
            print(result.stdout)
        if result.stderr:
            print("--- stderr ---")
            print(result.stderr)
    except FileNotFoundError as e:
        print(f"\n❌ Command not found: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error running command: {e}")
        return False

    if result.returncode != 0:
        print(f"\n❌ Failed: {description} (exit {result.returncode})")
        return False
    print(f"✅ Success: {description}")
    return True

def main(argv=None):
    # Ensure stdout/stderr use UTF-8 to avoid UnicodeEncodeError on Windows consoles
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        # best-effort; if reconfigure isn't available, continue
        pass

    base_dir = Path(__file__).parent
    import argparse
    parser = argparse.ArgumentParser(description='Deploy to Vercel')
    parser.add_argument('--dry-run', action='store_true', help='Prepare deploy but do not execute vercel')
    parser.add_argument('--non-interactive', action='store_true', help='Use VERCEL_TOKEN for non-interactive deploy')
    args = parser.parse_args(argv or None)
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║     CyberWorld Store - Vercel Deployment Automation      ║
║                                                          ║
║  This script will:                                       ║
║  1. Check dependencies                                   ║
║  2. Validate configuration                               ║
║  3. Build and test the Flask app                        ║
║  4. Deploy to Vercel                                     ║
║  5. Configure environment variables                      ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check Node.js and Vercel CLI
    print("\n🔍 Checking prerequisites...")
    # In dry-run mode, skip node/npm checks: we only want to validate steps
    if not args.dry_run:
        if not run_command("node --version", "Check Node.js"):
            print("⚠️  Node.js not found. Continuing — Vercel CLI may still work if installed separately.")
        if not run_command("npm --version", "Check npm"):
            print("⚠️  npm not found. Continuing — npm may not be required if Vercel CLI is available.")
        # Install Vercel CLI if not present (best-effort)
        run_command("npm install -g vercel", "Install Vercel CLI")
    
    # Step 2: Validate local environment
    print("\n🔍 Validating configuration...")
    env_file = base_dir / ".env"
    if not env_file.exists():
        print(f"⚠️  .env file not found at {env_file}. If you are running non-interactively, ensure necessary env vars are set in the environment (e.g. VERCEL_TOKEN, DATABASE_URL). Continuing...")
    else:
        print(f"✅ .env file found")
    
    # Step 3: Check Python and dependencies
    print("\n🐍 Checking Python environment...")
    run_command(".venv\\Scripts\\python.exe --version", "Check Python version")
    if not args.dry_run:
        run_command(".venv\\Scripts\\pip.exe install -r requirements.txt", "Install Python dependencies")
    
    # Step 4: Test Flask app syntax
    print("\n🧪 Testing Flask app...")
    run_command(".venv\\Scripts\\python.exe -m py_compile app.py", "Check app.py syntax")
    
    # Step 5: Check API wrapper
    run_command(".venv\\Scripts\\python.exe -m py_compile api/index.py", "Check API wrapper syntax")
    
    # Step 6: Git operations
    print("\n📦 Preparing Git...")
    run_command("git status", "Check git status")
    run_command("git add -A", "Stage all changes")
    run_command('git commit -m "chore: Prepare for Vercel deployment" || true', "Commit changes")
    # Push current branch to origin instead of forcing 'main'
    # This avoids modifying main and respects feature branches/PRs.
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
    except Exception:
        branch = 'main'
    run_command(f"git push origin {branch}", "Push current branch to GitHub")
    
    # Step 7: Vercel login (interactive)
    # Determine vercel executable for this platform
    vercel_exe = 'vercel.cmd' if platform.system() == 'Windows' else 'vercel'

    print("\n🔐 Vercel authentication...")
    print("Please login to Vercel (if not already logged in):")
    run_command([vercel_exe, 'login'], "Login to Vercel")
    
    # Step 8: Deploy
    print("\n🚀 Deploying to Vercel...")
    
    # Parse .env into a dictionary of env vars (if present)
    env = {}
    if env_file.exists():
        env_file_content = env_file.read_text()
        for line in env_file_content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip().strip('"\'')
                env[key] = value


    # If a VERCEL_TOKEN is provided, run non-interactively using it (CI friendly)
    vercel_token = os.environ.get('VERCEL_TOKEN') or os.environ.get('VERCEL_TOKEN'.upper())
    if vercel_token or args.non_interactive:
        token = vercel_token or os.environ.get('VERCEL_TOKEN')
        if token:
            # Do NOT pass the token on the command-line to avoid leaking it in logs.
            # Vercel CLI will use the VERCEL_TOKEN environment variable automatically.
            deploy_cmd = [vercel_exe, '--prod', '--confirm']
        else:
            print('VERCEL_TOKEN is not set; non-interactive deploy requested but token missing')
            return False
    else:
        deploy_cmd = [vercel_exe, '--prod']

    # Append environment variables as `--env KEY=VALUE` pairs
    for k, v in env.items():
        deploy_cmd.extend(['--env', f"{k}={v}"])
    if args.dry_run:
        print(f"DRY RUN: Would execute: {deploy_cmd}")
        return True
    if not run_command(deploy_cmd, "Deploy to Vercel"):
        print("\n⚠️  Deployment may have issues. Check your Vercel account.")
        print("Manual deployment: https://vercel.com/new")
        return False
    
    # Step 9: Get deployment info
    print("\n📍 Retrieving deployment info...")
    run_command([vercel_exe, 'ls', '--limit', '5'], "List recent deployments")
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║             ✅ Deployment Complete!                      ║
║                                                          ║
║  Next steps:                                             ║
║  1. Visit: https://vercel.com/dashboard                 ║
║  2. Configure GitHub Secrets for:                       ║
║     - VERCEL_TOKEN                                      ║
║     - VERCEL_ORG_ID                                     ║
║     - VERCEL_PROJECT_ID                                 ║
║  3. Test your live app:                                 ║
║     - Check email delivery                              ║
║     - Test Paystack payments                            ║
║     - Test wallet transactions                          ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
