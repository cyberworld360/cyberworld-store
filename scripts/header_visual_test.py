#!/usr/bin/env python3
"""Header visual regression test using Playwright.

This script captures screenshots of the header component across three
viewport sizes: mobile, tablet, and desktop. It outputs PNG files to a
directory (default: scripts/screenshots). The base URL can be passed via
--base or via PROD_BASE environment variable.

Usage:
  python scripts/header_visual_test.py --base https://localhost:5000

Requires:
  pip install playwright
  python -m playwright install

"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import sys

try:
    from playwright.sync_api import sync_playwright
except Exception as e:
    print("Playwright not installed. Install with: pip install playwright && python -m playwright install")
    raise


VIEWPORTS = {
    "mobile": {"width": 412, "height": 915, "is_mobile": True},
    "tablet": {"width": 768, "height": 1024, "is_mobile": False},
    "desktop": {"width": 1366, "height": 768, "is_mobile": False},
}


def capture_header_screenshots(base_url: str, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, viewport in VIEWPORTS.items():
            print(f"Capturing header screenshot for: {name} (w={viewport['width']} h={viewport['height']})")
            context = browser.new_context(viewport={"width": viewport["width"], "height": viewport["height"]}, is_mobile=viewport.get("is_mobile", False))
            page = context.new_page()
            try:
                page.goto(base_url, timeout=15000)
                # Wait for header to appear
                page.wait_for_selector('header.site-header', timeout=5000)
            except Exception as e:
                print(f"Failed to open page or locate header for {name}: {e}")
                failures += 1
                context.close()
                continue
            try:
                header = page.locator('header.site-header')
                # Ensure header is visible and stable before screenshot
                header.wait_for(state='visible', timeout=3000)
                fname = out_dir / f"header-{name}.png"
                header.screenshot(path=str(fname))
                print(f"Saved: {fname}")
            except Exception as e:
                print(f"Failed to capture header screenshot for {name}: {e}")
                failures += 1
            finally:
                context.close()
        browser.close()
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description="Capture header screenshots across viewport breakpoints")
    parser.add_argument('--base', help='Base URL to run tests against (defaults to PROD_BASE or http://127.0.0.1:5000)', default=os.environ.get('PROD_BASE', 'http://127.0.0.1:5000'))
    parser.add_argument('--out', help='Output screenshot directory', default='scripts/screenshots')
    args = parser.parse_args(argv)

    base_url = args.base
    out_dir = Path(args.out)

    print(f"Using base URL: {base_url}")
    print(f"Writing screenshots to: {out_dir}")

    failures = capture_header_screenshots(base_url, out_dir)
    if failures:
        print(f"Completed with {failures} failures")
        sys.exit(2)
    print("Completed: all header screenshots saved")
    return 0


if __name__ == '__main__':
    sys.exit(main())
