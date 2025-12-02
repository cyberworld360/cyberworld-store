Header visual test (Playwright - Python)

This script captures screenshots of the shop header (hamburger, logo and cart) across multiple viewports (mobile / tablet / desktop).

Prerequisites
- Python 3.8+
- venv recommended - e.g., in PowerShell:

  python -m venv .venv
  .\.venv\Scripts\Activate
  python -m pip install --upgrade pip
  python -m pip install playwright
  python -m playwright install

Usage
- Basic (use PROD_BASE env var or --base):

  $env:PROD_BASE='https://your-deploy-url.vercel.app'
  python scripts\header_visual_test.py --base $env:PROD_BASE --out scripts/screenshots/header

- Or with explicit URL:

  python scripts\header_visual_test.py --base https://localhost:5000 --out scripts/screenshots/header

Files created
- `scripts/screenshots/header-mobile.png`
- `scripts/screenshots/header-tablet.png`
- `scripts/screenshots/header-desktop.png`

Notes
- The script uses Playwright's Chromium browser by default (headless). To visually inspect during runs, modify the script to launch with `headless=False` and (optionally) `slow_mo` in `launch()` call.
- If using CI (GitHub Actions), install Playwright browsers in CI using `python -m playwright install --with-deps` on Linux, and run the script in the pipeline to capture visual diffs.
