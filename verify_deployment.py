#!/usr/bin/env python3
"""
Pre-deployment verification script
Checks all components before deploying to Vercel
"""

import os
import sys
import subprocess
from pathlib import Path
import json

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(status, message):
    """Print status message with color"""
    if status == "✅":
        color = Colors.GREEN
    elif status == "❌":
        color = Colors.RED
    elif status == "⚠️":
        color = Colors.YELLOW
    else:
        color = Colors.BLUE
    
    print(f"{color}{status} {message}{Colors.RESET}")

def check_file_exists(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print_status("✅", f"{description}: {path}")
        return True
    else:
        print_status("❌", f"{description} NOT FOUND: {path}")
        return False

def check_command(cmd, description):
    """Check if a command works"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        if result.returncode == 0:
            output = result.stdout.decode().strip()
            if output:
                print_status("✅", f"{description}: {output.splitlines()[0]}")
            else:
                print_status("✅", description)
            return True
        else:
            print_status("❌", f"{description}: Command failed")
            return False
    except Exception as e:
        print_status("❌", f"{description}: {str(e)}")
        return False

def check_python_syntax(file_path):
    """Check Python file for syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            compile(f.read(), file_path, 'exec')
        print_status("✅", f"Python syntax valid: {file_path}")
        return True
    except SyntaxError as e:
        print_status("❌", f"Python syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print_status("⚠️", f"Could not check {file_path}: {e}")
        return True  # Don't fail on encoding issues

def check_vercel_config():
    """Check vercel.json configuration"""
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        # Check required fields
        if 'functions' in config and 'routes' in config:
            print_status("✅", "vercel.json configuration is valid")
            return True
        else:
            print_status("⚠️", "vercel.json might be missing important fields")
            return False
    except Exception as e:
        print_status("❌", f"vercel.json error: {e}")
        return False

def check_env_file():
    """Check .env file configuration"""
    required_vars = [
        'SECRET_KEY', 'PAYSTACK_SECRET_KEY', 'PAYSTACK_PUBLIC_KEY',
        'MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD'
    ]
    
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        missing = []
        for var in required_vars:
            if f'{var}=' not in env_content:
                missing.append(var)
        
        if missing:
            print_status("⚠️", f".env missing: {', '.join(missing)}")
            return False
        else:
            print_status("✅", ".env has all required variables")
            return True
    except FileNotFoundError:
        print_status("❌", ".env file not found")
        return False

def check_requirements():
    """Check requirements.txt"""
    required_packages = [
        'Flask', 'Flask-SQLAlchemy', 'Flask-Login', 'Flask-Migrate',
        'requests', 'asgiref', 'Werkzeug'
    ]
    
    try:
        with open('requirements.txt', 'r') as f:
            reqs_content = f.read()
        
        missing = []
        for pkg in required_packages:
            if pkg.lower() not in reqs_content.lower():
                missing.append(pkg)
        
        if missing:
            print_status("⚠️", f"requirements.txt might be missing: {', '.join(missing)}")
            return False
        else:
            print_status("✅", "requirements.txt includes all essential packages")
            return True
    except FileNotFoundError:
        print_status("❌", "requirements.txt not found")
        return False

def main():
    print(f"""
{Colors.BOLD}{Colors.BLUE}
╔════════════════════════════════════════════════════════════════╗
║         CyberWorld Store - Pre-Deployment Verification        ║
║                                                               ║
║  This script checks if your app is ready for Vercel deploy   ║
╚════════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)
    
    checks_passed = 0
    checks_failed = 0
    checks_warning = 0
    
    # Section 1: File structure
    print(f"\n{Colors.BOLD}📁 File Structure{Colors.RESET}")
    print("-" * 60)
    
    files_to_check = [
        ('app.py', 'Main Flask app'),
        ('api/index.py', 'Vercel API wrapper'),
        ('vercel.json', 'Vercel configuration'),
        ('requirements.txt', 'Python dependencies'),
        ('.env', 'Environment variables'),
        ('.github/workflows/deploy-vercel.yml', 'GitHub Actions workflow'),
        ('templates/base.html', 'Base template'),
    ]
    
    for file_path, description in files_to_check:
        if check_file_exists(file_path, description):
            checks_passed += 1
        else:
            checks_failed += 1
    
    # Section 2: Python syntax
    print(f"\n{Colors.BOLD}🐍 Python Syntax{Colors.RESET}")
    print("-" * 60)
    
    python_files = ['app.py', 'api/index.py']
    for py_file in python_files:
        if check_python_syntax(py_file):
            checks_passed += 1
        else:
            checks_failed += 1
    
    # Section 3: Configuration
    print(f"\n{Colors.BOLD}⚙️  Configuration{Colors.RESET}")
    print("-" * 60)
    
    if check_vercel_config():
        checks_passed += 1
    else:
        checks_failed += 1
    
    if check_env_file():
        checks_passed += 1
    else:
        checks_warning += 1
    
    if check_requirements():
        checks_passed += 1
    else:
        checks_warning += 1
    
    # Section 4: Git status
    print(f"\n{Colors.BOLD}📦 Git Status{Colors.RESET}")
    print("-" * 60)
    
    if check_command("git status --porcelain | head -3", "Git changes"):
        checks_passed += 1
    else:
        checks_warning += 1
    
    if check_command("git log --oneline -1", "Last commit"):
        checks_passed += 1
    else:
        checks_failed += 1
    
    # Section 5: Dependencies
    print(f"\n{Colors.BOLD}📚 Installed Packages{Colors.RESET}")
    print("-" * 60)
    
    if check_command(".venv\\Scripts\\pip.exe show Flask -q", "Flask version"):
        checks_passed += 1
    else:
        checks_warning += 1
    
    # Section 6: Optional checks
    print(f"\n{Colors.BOLD}🔧 Optional Components{Colors.RESET}")
    print("-" * 60)
    
    if check_command("vercel --version", "Vercel CLI"):
        checks_passed += 1
    else:
        print_status("⚠️", "Vercel CLI not installed (install with: npm install -g vercel)")
        checks_warning += 1
    
    if check_command("git remote -v", "GitHub remote"):
        checks_passed += 1
    else:
        checks_failed += 1
    
    # Summary
    total = checks_passed + checks_failed + checks_warning
    
    print(f"""
{Colors.BOLD}{Colors.BLUE}
╔════════════════════════════════════════════════════════════════╗
║                    VERIFICATION SUMMARY                       ║
╚════════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)
    
    print(f"{Colors.GREEN}✅ Passed: {checks_passed}{Colors.RESET}")
    print(f"{Colors.RED}❌ Failed: {checks_failed}{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  Warnings: {checks_warning}{Colors.RESET}")
    print(f"\nTotal: {total} checks")
    
    # Recommendations
    if checks_failed == 0:
        print(f"""
{Colors.GREEN}{Colors.BOLD}
╔════════════════════════════════════════════════════════════════╗
║            ✅ YOUR APP IS READY FOR DEPLOYMENT!               ║
║                                                               ║
║  Next steps:                                                  ║
║  1. Ensure all GitHub Secrets are set                         ║
║  2. Run: vercel --prod                                        ║
║  3. Or just push to main branch for auto-deployment           ║
║                                                               ║
║  📚 See VERCEL_SETUP_COMPLETE.md for detailed instructions   ║
╚════════════════════════════════════════════════════════════════╝
{Colors.RESET}
        """)
        return 0
    else:
        print(f"""
{Colors.RED}{Colors.BOLD}
╔════════════════════════════════════════════════════════════════╗
║           ⚠️  PLEASE FIX ERRORS BEFORE DEPLOYING              ║
║                                                               ║
║  Failed checks above must be resolved                         ║
║  See VERCEL_SETUP_COMPLETE.md for troubleshooting             ║
╚════════════════════════════════════════════════════════════════╝
{Colors.RESET}
        """)
        return 1

if __name__ == "__main__":
    sys.exit(main())
