#!/usr/bin/env python
"""
Set admin settings via direct JSON API (bypasses form complexity).
This script logs in as admin and POSTs settings directly as JSON.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, AdminUser, Settings

def set_admin_settings_json(
    dashboard_layout=None,
    seo_visible=None,
    seo_checklist_done=None,
    site_announcement=None,
    primary_color=None,
    secondary_color=None,
    primary_font=None,
    secondary_font=None
):
    """
    Update admin settings via JSON API.
    
    Args:
        dashboard_layout: 'grid' or 'list'
        seo_visible: Boolean
        seo_checklist_done: Boolean
        site_announcement: String (announcement text)
        primary_color: Hex color code
        secondary_color: Hex color code
        primary_font: Font name
        secondary_font: Font name
    """
    with app.test_client() as client:
        print("[1/3] Logging in as admin...")
        
        # Login as admin
        login_response = client.post('/admin/login', data={
            'email': 'admin@cyberworld.com',
            'password': 'Admin@123'
        }, follow_redirects=True)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: Status {login_response.status_code}")
            return False
        
        if b'Logged in as admin' not in login_response.data:
            print("❌ Login authentication failed")
            return False
        
        print("✓ Successfully logged in")
        
        print("\n[2/3] Preparing JSON payload...")
        
        # Build payload with only provided values
        payload = {}
        if dashboard_layout is not None:
            payload['dashboard_layout'] = dashboard_layout
        if seo_visible is not None:
            payload['seo_visible'] = seo_visible
        if seo_checklist_done is not None:
            payload['seo_checklist_done'] = seo_checklist_done
        if site_announcement is not None:
            payload['site_announcement'] = site_announcement
        if primary_color is not None:
            payload['primary_color'] = primary_color
        if secondary_color is not None:
            payload['secondary_color'] = secondary_color
        if primary_font is not None:
            payload['primary_font'] = primary_font
        if secondary_font is not None:
            payload['secondary_font'] = secondary_font
        
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        print("\n[3/3] POSTing to /admin/settings/api...")
        
        # POST settings as JSON
        api_response = client.post(
            '/admin/settings/api',
            json=payload,
            content_type='application/json'
        )
        
        print(f"Status: {api_response.status_code}")
        
        if api_response.status_code in [200, 201]:
            result = api_response.get_json()
            print(f"✓ {result.get('message', 'Settings updated')}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ API failed with status {api_response.status_code}")
            try:
                error_data = api_response.get_json()
                print(f"Error: {error_data.get('message', 'Unknown error')}")
            except Exception:
                print(f"Response: {api_response.data.decode('utf-8', errors='ignore')}")
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("ADMIN SETTINGS JSON API UPDATER")
    print("=" * 60)
    
    # Example: Update multiple settings
    success = set_admin_settings_json(
        dashboard_layout='grid',
        seo_visible=True,
        seo_checklist_done=False,
        site_announcement='Welcome to CyberWorld - Your trusted e-commerce platform!',
        primary_color='#007bff',
        secondary_color='#6c757d'
    )
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Settings updated successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Failed to update settings")
        print("=" * 60)
        sys.exit(1)
