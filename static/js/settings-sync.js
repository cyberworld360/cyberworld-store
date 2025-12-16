/**
 * Real-Time Settings Synchronization
 * 
 * This script continuously polls for admin settings changes and instantly
 * applies them to the user interface without requiring a page reload.
 * 
 * - Polls /api/settings/live every 2 seconds
 * - Detects changes using a hash comparison
 * - Updates CSS variables dynamically
 * - Updates custom CSS in real-time
 * - Works on both admin and user pages
 */

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        pollInterval: 2000,  // Poll every 2 seconds
        endpoint: '/api/settings/live',
        enableLogging: false  // Set to true for debugging
    };
    
    // State tracking
    let lastSettingsHash = null;
    let lastSettings = null;
    let pollTimeout = null;
    let isDestroyed = false;
    
    // Logging utility
    function log(message, data) {
        if (CONFIG.enableLogging) {
            console.log('[SettingsSync] ' + message, data || '');
        }
    }
    
    /**
     * Update CSS custom properties with new settings
     */
    function updateCSSVariables(settings) {
        const root = document.documentElement;
        
        const cssVars = {
            '--primary-color': settings.primary_color || '#27ae60',
            '--secondary-color': settings.secondary_color || '#2c3e50',
            '--primary-font': settings.primary_font || 'Arial, sans-serif',
            '--secondary-font': settings.secondary_font || 'Verdana, sans-serif',
            '--logo-height': (settings.logo_height || 48) + 'px',
            '--logo-top': (settings.logo_top_px || 0) + 'px',
            '--header-top': (settings.logo_top_px || 8) + 'px',
            '--logo-zindex': (settings.logo_zindex || 9999) + ''
        };
        
        // Apply each CSS variable
        Object.entries(cssVars).forEach(([key, value]) => {
            try {
                root.style.setProperty(key, value);
                log('Updated CSS var: ' + key + ' = ' + value);
            } catch (e) {
                console.warn('Failed to update CSS variable ' + key, e);
            }
        });
    }
    
    /**
     * Update custom CSS in the head
     */
    function updateCustomCSS(settings) {
        const customCSS = settings.custom_css || '';
        
        if (!customCSS.trim()) {
            // Remove custom CSS if empty
            const existingTag = document.getElementById('dynamic-custom-css');
            if (existingTag) {
                existingTag.remove();
            }
            return;
        }
        
        let styleTag = document.getElementById('dynamic-custom-css');
        
        if (!styleTag) {
            // Create new style tag for custom CSS
            styleTag = document.createElement('style');
            styleTag.id = 'dynamic-custom-css';
            styleTag.type = 'text/css';
            document.head.appendChild(styleTag);
            log('Created dynamic-custom-css style tag');
        }
        
        // Update content if changed
        if (styleTag.textContent !== customCSS) {
            try {
                styleTag.textContent = customCSS;
                log('Updated custom CSS');
            } catch (e) {
                console.warn('Failed to update custom CSS', e);
            }
        }
    }
    
    /**
     * Update cart position (move between left and right)
     */
    function updateCartPosition(settings) {
        const cartElement = document.querySelector('[data-cart-container], .cart-icon, [class*="cart"]');
        if (!cartElement) return;
        
        const shouldBeOnRight = settings.cart_on_right || false;
        
        // This would depend on your specific HTML structure
        // You might need to adjust the selector and logic
        if (shouldBeOnRight) {
            cartElement.classList.add('cart-on-right');
            cartElement.classList.remove('cart-on-left');
        } else {
            cartElement.classList.add('cart-on-left');
            cartElement.classList.remove('cart-on-right');
        }
    }
    
    /**
     * Apply all settings to the UI
     */
    function applySettings(settings) {
        try {
            updateCSSVariables(settings);
            updateCustomCSS(settings);
            updateCartPosition(settings);
            
            // Dispatch custom event so other scripts can listen for settings changes
            const event = new CustomEvent('settingsUpdated', {
                detail: settings,
                bubbles: true,
                cancelable: false
            });
            document.dispatchEvent(event);
            
            log('Settings applied to UI');
        } catch (e) {
            console.error('[SettingsSync] Error applying settings:', e);
        }
    }
    
    /**
     * Fetch settings from the server
     */
    async function fetchSettings() {
        if (isDestroyed) return;
        
        try {
            const response = await fetch(CONFIG.endpoint, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                cache: 'no-cache'
            });
            
            if (!response.ok) {
                log('Fetch failed with status: ' + response.status);
                return;
            }
            
            const data = await response.json();
            
            if (!data.settings) {
                log('No settings in response');
                return;
            }
            
            // Check if settings have changed using hash
            const currentHash = data.hash;
            
            if (currentHash !== lastSettingsHash) {
                log('Settings changed, hash: ' + currentHash);
                lastSettingsHash = currentHash;
                lastSettings = data.settings;
                
                // Apply the new settings to the UI
                applySettings(data.settings);
                
                // Optional: notify user that settings were updated
                // console.log('Settings updated from server:', data.settings);
            } else {
                log('Settings unchanged');
            }
        } catch (e) {
            console.warn('[SettingsSync] Fetch error:', e);
        }
        
        // Schedule next poll
        if (!isDestroyed) {
            pollTimeout = setTimeout(fetchSettings, CONFIG.pollInterval);
        }
    }
    
    /**
     * Start polling for settings changes
     */
    function start() {
        if (isDestroyed) return;
        
        log('Starting settings sync');
        
        // Initial fetch
        fetchSettings();
    }
    
    /**
     * Stop polling and cleanup
     */
    function stop() {
        isDestroyed = true;
        if (pollTimeout) {
            clearTimeout(pollTimeout);
            pollTimeout = null;
        }
        log('Settings sync stopped');
    }
    
    /**
     * Initialize on DOM ready
     */
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', start);
        } else {
            start();
        }
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', stop);
    }
    
    // Export to window for debugging/control
    window.SettingsSync = {
        start: start,
        stop: stop,
        fetchNow: fetchSettings,
        getLastSettings: () => lastSettings,
        getLastHash: () => lastSettingsHash,
        setEnabled: (enabled) => {
            if (enabled && isDestroyed) {
                isDestroyed = false;
                start();
            } else if (!enabled && !isDestroyed) {
                stop();
            }
        }
    };
    
    // Start automatically
    init();
})();
