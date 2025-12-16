# Real-Time Settings Sync - Verification Guide

## Quick Verification (5 minutes)

### Step 1: Verify File Changes
```powershell
# Check if new script file exists
Test-Path ".\static\js\settings-sync.js"  # Should return True

# Verify Python file has no syntax errors
python -m py_compile app.py  # Should complete without errors
```

### Step 2: Start the Application
```powershell
# Activate virtual environment if using one
.\.venv\Scripts\Activate

# Start the Flask app
python run_server.py
# Should see: Running on http://127.0.0.1:5000/
```

### Step 3: Test Admin Settings Auto-Save
1. Open two browser windows
2. In Window 1: Go to `http://localhost:5000/admin` → Login
3. In Window 1: Navigate to `/admin/settings`
4. In Window 2: Go to `http://localhost:5000/` (homepage)
5. In Window 1: Change the "Primary Color" to `#ff0000` (red)
6. **Expected**: Auto-save should trigger after 1 second
7. **Result**: Check Window 2 homepage - buttons/links should turn red in ~2 seconds
8. ✅ If homepage updated without refresh → **Test Passed**

### Step 4: Test Multiple Browsers
1. Open same pages in Chrome and Firefox
2. In Chrome admin: Change "Primary Font" to `Georgia, serif`
3. Wait 2 seconds
4. Check Firefox homepage text
5. ✅ If Firefox text changed to Georgia font → **Test Passed**

### Step 5: Check Network Traffic
1. Open DevTools (F12) → Network tab
2. Filter by `/api/settings/live`
3. Refresh any page
4. Should see requests every 2 seconds
5. Response should be small JSON (~2KB)
6. Status should be 200
7. ✅ If requests appear regularly → **Test Passed**

## Detailed Verification

### Test: Auto-Save Mechanism
```
1. Admin page → Open DevTools → Network tab
2. Change color → Wait 1 second
3. Should see POST to /admin/settings/api
4. Response: {"status": "success", ...}
5. Check database to confirm settings changed
```

### Test: Cache Invalidation
```python
# In Flask shell (python shell within app context)
from app import _settings_cache, Settings

# Before change: Settings in DB
original = Settings.query.first()
print(f"Original color: {original.primary_color}")

# Check cache
print(f"Cache state: {_settings_cache._cache}")

# Make a change (from admin UI)
# Now check cache
print(f"Cache invalidated: {_settings_cache._cache is None}")

# Next get_settings() should fetch from DB
fresh = get_settings()
print(f"Fresh color: {fresh.primary_color}")
```

### Test: API Endpoint
```bash
# From PowerShell or Command Prompt
curl.exe http://localhost:5000/api/settings/live

# Expected response:
# {
#   "status": "success",
#   "settings": {
#     "primary_color": "#27ae60",
#     "logo_height": 48,
#     ...
#   },
#   "hash": "abc123..."
# }
```

### Test: CSS Variable Updates
```javascript
// In browser console on any page
// Check if CSS variables are set
getComputedStyle(document.documentElement)
  .getPropertyValue('--primary-color')

// Should return color value like "rgb(39, 174, 96)" or "#27ae60"

// Check if custom CSS is applied
document.getElementById('dynamic-custom-css')  
// Should return the style tag if custom CSS is set
```

## Complete Test Scenario

### Setup
- Open 3 browser windows:
  - Window A: Admin settings page
  - Window B: Homepage
  - Window C: Another page (cart, products, etc.)

### Test Sequence

#### Test 1: Color Change
**Action**: In Window A, change primary color to #3498db (blue)
- [ ] Window A shows change immediately
- [ ] Window B shows blue buttons/links in 2 seconds
- [ ] Window C shows blue buttons/links in 2 seconds
- [ ] Refresh Window B → Color persists ✅

#### Test 2: Font Change
**Action**: In Window A, change primary font to `Courier New, monospace`
- [ ] Window A text changes to monospace immediately
- [ ] Window B text changes in 2 seconds
- [ ] Window C text changes in 2 seconds
- [ ] Monospace persists after refresh ✅

#### Test 3: Custom CSS
**Action**: In Window A, add to custom CSS:
```css
button { border-radius: 20px !important; }
```
- [ ] Window A buttons become rounded immediately
- [ ] Window B buttons rounded in 2 seconds
- [ ] Window C buttons rounded in 2 seconds
- [ ] Refresh Window A → Still rounded ✅

#### Test 4: Logo Height
**Action**: In Window A, change logo height to 80px
- [ ] Window A logo enlarges immediately
- [ ] Window B logo enlarged in 2 seconds
- [ ] Window C logo enlarged in 2 seconds
- [ ] Refresh Window A → Logo stays large ✅

#### Test 5: Cart Position
**Action**: In Window A, toggle "Cart on Right"
- [ ] Window A header updates
- [ ] Window B header updates in 2 seconds
- [ ] Cart moves to opposite side ✅

#### Test 6: Form Submission (Backward Compatibility)
**Action**: Upload a new logo via file upload in Window A
- [ ] Logo upload works
- [ ] Page processes upload
- [ ] New logo appears after page refresh
- [ ] Changes propagate to other windows ✅

#### Test 7: Network Performance
**Action**: Monitor network tab while changes happen
- [ ] No large requests
- [ ] Auto-save request is ~100-500 bytes
- [ ] API response is ~2KB
- [ ] No 404 or 500 errors ✅

## Browser-Specific Tests

### Chrome
- [ ] Settings sync works
- [ ] Auto-save works
- [ ] Console shows no errors
- [ ] Performance is good

### Firefox
- [ ] Settings sync works
- [ ] Auto-save works
- [ ] Console shows no errors
- [ ] Performance is good

### Safari
- [ ] Settings sync works
- [ ] Auto-save works
- [ ] Console shows no errors
- [ ] Performance is good

### Edge
- [ ] Settings sync works
- [ ] Auto-save works
- [ ] Console shows no errors
- [ ] Performance is good

## Mobile Testing

### iPhone/iPad Safari
- [ ] Settings sync works
- [ ] Layout adjusts with settings
- [ ] Touch interactions work

### Android Chrome
- [ ] Settings sync works
- [ ] Layout adjusts with settings
- [ ] Touch interactions work

## Database Verification

```sql
-- Verify settings table
SELECT * FROM settings;

-- Should show columns:
-- id, primary_color, secondary_color, primary_font,
-- secondary_font, logo_height, logo_top_px, logo_zindex,
-- cart_on_right, custom_css, site_announcement, etc.

-- After making changes, these should update:
UPDATE settings SET primary_color = '#ff0000' WHERE id = 1;
SELECT primary_color FROM settings WHERE id = 1;
```

## Debug Checklist

### If Auto-Save Fails
- [ ] Browser network tab shows POST to `/admin/settings/api`
- [ ] POST returns 200 status
- [ ] Response contains `"status": "success"`
- [ ] Field names match JavaScript `fieldsToAutoSave` list
- [ ] Database permissions are correct
- [ ] No JavaScript errors in console

### If Polling Doesn't Work
- [ ] Network tab shows GET requests to `/api/settings/live`
- [ ] Requests happen every 2 seconds
- [ ] Response is valid JSON
- [ ] Response includes `hash` field
- [ ] JavaScript is enabled in browser
- [ ] Script file loads (check Network tab)

### If Settings Don't Persist
- [ ] Database write is successful
- [ ] No database errors in app logs
- [ ] Check cache is invalidated properly
- [ ] Verify database connection
- [ ] Check for database transaction rollbacks

## Performance Metrics

### Expected Values
- Auto-save delay: 0-1 seconds
- First poll refresh: 0-2 seconds
- API response time: <100ms
- CPU usage: <1% per browser
- Memory usage: <5MB per browser
- Network: ~2KB per poll request

### Monitor Performance
```javascript
// In browser console
performance.measure('settingsSync')
console.log(performance.getEntriesByName('settingsSync'))
```

## Logging & Debugging

### Enable detailed logging
Edit `/static/js/settings-sync.js` line 24:
```javascript
enableLogging: true
```

Then check browser console for messages:
```
[SettingsSync] Starting settings sync
[SettingsSync] Settings changed, hash: abc123def456
[SettingsSync] Updated CSS var: --primary-color = #ff0000
[SettingsSync] Updated custom CSS
```

### Server-side debugging
```python
# In app.py, enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Then watch for messages when testing
# Look for: "Saving settings values:", "Error saving settings:"
```

## Rollback Procedure (If Needed)

If issues occur, rollback to previous behavior:

1. Comment out script tag in base.html (line ~193):
```html
<!-- <script src="/static/js/settings-sync.js"></script> -->
```

2. Remove auto-save code from admin_settings.html

3. Comment out cache invalidation in app.py:
```python
# _settings_cache.invalidate()
```

4. Reload page - should work as before

## Deployment Verification

### Before Going Live
- [ ] All tests pass locally
- [ ] No errors in production logs
- [ ] Settings sync works on staging
- [ ] Performance is acceptable
- [ ] Database backups are current
- [ ] Rollback procedure documented
- [ ] Team is trained on new feature

### After Going Live
- [ ] Monitor server logs for errors
- [ ] Monitor user reports
- [ ] Check performance metrics
- [ ] Verify settings changes propagate
- [ ] Monitor database load

## Success Criteria

✅ **All of the following must be true:**
1. Admin can change settings without page reload
2. Changes appear on user pages within 2 seconds
3. Changes persist after browser restart
4. Multiple browsers sync automatically
5. Auto-save works without form submission
6. File uploads still work (form submission)
7. No JavaScript errors in console
8. No database errors in logs
9. Network requests are lightweight
10. Performance is good on all devices

## Support Information

If any test fails:

1. Check the [SETTINGS_REALTIME_SYNC.md](SETTINGS_REALTIME_SYNC.md) for detailed documentation
2. Review [SETTINGS_QUICK_START.md](SETTINGS_QUICK_START.md) for examples
3. Check browser console for JavaScript errors
4. Check app logs for Python errors
5. Verify database is accessible
6. Confirm settings table exists and is writable

---

**Test Date**: December 2025  
**Status**: Ready for Verification  
**Expected Result**: All tests pass ✅
