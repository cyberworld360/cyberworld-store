#!/usr/bin/env python3
"""
Check Vercel deployment status and logs.

Requires VERCEL_TOKEN env var (get from https://vercel.com/account/tokens).

Usage:
    python tools/check_vercel_deployment.py [--project PROJECT] [--team TEAM]

Examples:
    python tools/check_vercel_deployment.py
    python tools/check_vercel_deployment.py --project cyberworld-store --team cyberworld360
"""
import os
import sys
import argparse
import requests
import json
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_dotenv(path: str = ".env"):
    """Load .env file manually."""
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if val and val[0] == '"' and val[-1] == '"':
            val = val[1:-1]
        if key and key not in os.environ:
            os.environ[key] = val

load_dotenv()

VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN", "").strip()
VERCEL_PROJECT = os.environ.get("VERCEL_PROJECT_NAME", "cyberworld-store").strip()
VERCEL_TEAM = os.environ.get("VERCEL_TEAM_ID", "").strip()

BASE_URL = "https://api.vercel.com"

def fetch_deployments(project_id: str, limit: int = 5) -> dict:
    """Fetch recent deployments from Vercel."""
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {
        "limit": limit,
        "projectId": project_id
    }
    if VERCEL_TEAM:
        params["teamId"] = VERCEL_TEAM
    
    url = f"{BASE_URL}/v6/deployments"
    print(f"\n[INFO] Fetching deployments from: {url}")
    print(f"[INFO] Project: {project_id}, Team: {VERCEL_TEAM or 'personal'}")
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch deployments: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"[ERROR] Response: {e.response.text}")
            except Exception:
                pass
        return {}

def fetch_deployment_logs(deployment_id: str) -> list:
    """Fetch logs for a specific deployment."""
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {}
    if VERCEL_TEAM:
        params["teamId"] = VERCEL_TEAM
    
    url = f"{BASE_URL}/v9/deployments/{deployment_id}/events"
    print(f"\n[INFO] Fetching logs for deployment: {deployment_id}")
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("events", [])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch logs: {e}")
        return []

def get_projects() -> dict:
    """List projects to find project ID."""
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {}
    if VERCEL_TEAM:
        params["teamId"] = VERCEL_TEAM
    
    url = f"{BASE_URL}/v9/projects"
    print(f"\n[INFO] Fetching projects...")
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch projects: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(
        description="Check Vercel deployment status and logs.",
        epilog="Requires VERCEL_TOKEN env var. Get it from https://vercel.com/account/tokens"
    )
    parser.add_argument("--project", default=VERCEL_PROJECT, help=f"Vercel project name (default: {VERCEL_PROJECT})")
    parser.add_argument("--team", default=VERCEL_TEAM, help=f"Vercel team ID (default: {VERCEL_TEAM or 'personal'})")
    parser.add_argument("--limit", type=int, default=5, help="Number of recent deployments to fetch (default: 5)")
    parser.add_argument("--logs", action="store_true", help="Fetch full logs for the most recent deployment")
    args = parser.parse_args()

    if not VERCEL_TOKEN:
        print("[ERROR] VERCEL_TOKEN not set in environment or .env file")
        print("[INFO] Get your token from: https://vercel.com/account/tokens")
        sys.exit(1)

    print("="*80)
    print(" VERCEL DEPLOYMENT STATUS CHECK")
    print("="*80)
    
    # Get projects
    projects_data = get_projects()
    projects = projects_data.get("projects", [])
    
    if not projects:
        print("[ERROR] No projects found or failed to fetch projects")
        print("[INFO] Ensure VERCEL_TOKEN is valid and team/personal access is granted")
        sys.exit(1)
    
    # Find project by name
    project_id = None
    for proj in projects:
        if proj.get("name") == args.project:
            project_id = proj.get("id")
            break
    
    if not project_id:
        print(f"[ERROR] Project '{args.project}' not found")
        print(f"[INFO] Available projects:")
        for p in projects:
            print(f"  - {p.get('name')} (id: {p.get('id')})")
        sys.exit(1)
    
    print(f"[SUCCESS] Found project: {args.project}")
    print(f"[INFO] Project ID: {project_id}")
    
    # Fetch deployments
    deployments_data = fetch_deployments(project_id, limit=args.limit)
    deployments = deployments_data.get("deployments", [])
    
    if not deployments:
        print("[ERROR] No deployments found")
        sys.exit(1)
    
    print(f"\n[SUCCESS] Found {len(deployments)} recent deployment(s)")
    print("\n" + "="*80)
    print(" DEPLOYMENT HISTORY")
    print("="*80)
    
    for i, dep in enumerate(deployments, 1):
        print(f"\n[{i}] Deployment ID: {dep.get('uid', 'N/A')[:8]}")
        print(f"    URL: {dep.get('url', 'N/A')}")
        print(f"    Status: {dep.get('state', 'unknown')}")
        print(f"    Created: {dep.get('created', 'N/A')}")
        print(f"    Commit SHA: {dep.get('meta', {}).get('githubCommitSha', 'N/A')[:8]}")
        print(f"    Branch: {dep.get('meta', {}).get('githubCommitRef', 'N/A')}")
        print(f"    Environment: {dep.get('target', 'unknown')}")
    
    # Fetch logs for most recent if requested
    if args.logs and deployments:
        most_recent = deployments[0]
        dep_id = most_recent.get("uid")
        print(f"\n" + "="*80)
        print(f" BUILD LOGS: {most_recent.get('url', 'N/A')}")
        print("="*80)
        
        logs = fetch_deployment_logs(dep_id)
        if logs:
            for event in logs:
                timestamp = event.get("created", "")
                text = event.get("text", "")
                event_type = event.get("type", "log")
                
                # Format timestamp
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        timestamp = dt.strftime("%H:%M:%S")
                    except Exception:
                        pass
                
                # Color code by type
                if event_type in ("error", "SYSTEM_ERROR"):
                    prefix = "[ERROR]"
                elif event_type in ("warning", "SYSTEM_WARNING"):
                    prefix = "[WARN]"
                else:
                    prefix = "[LOG]"
                
                if text:
                    print(f"{prefix} {timestamp} {text[:120]}")
        else:
            print("[INFO] No logs available")
    
    # Summary
    print("\n" + "="*80)
    print(" DEPLOYMENT SUMMARY")
    print("="*80)
    
    if deployments:
        latest = deployments[0]
        print(f"\n✓ Latest Deployment:")
        print(f"  - Status: {latest.get('state', 'unknown')}")
        print(f"  - URL: {latest.get('url', 'N/A')}")
        print(f"  - Commit: {latest.get('meta', {}).get('githubCommitSha', 'N/A')[:12]}")
        print(f"  - Branch: {latest.get('meta', {}).get('githubCommitRef', 'N/A')}")
        
        if latest.get('state') == 'READY':
            print(f"\n✅ Deployment is READY and serving traffic")
        elif latest.get('state') == 'BUILDING':
            print(f"\n⏳ Deployment is still BUILDING...")
        elif latest.get('state') == 'ERROR':
            print(f"\n❌ Deployment has ERROR status - check logs above")
        else:
            print(f"\n⚠️  Deployment status is: {latest.get('state')}")
    
    print("\n[INFO] To view full logs, visit:")
    if deployments:
        print(f"  {deployments[0].get('url', 'N/A')}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
