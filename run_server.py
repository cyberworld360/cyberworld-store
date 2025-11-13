#!/usr/bin/env python
"""Flask runner with workaround for Windows asyncio issues"""
import sys
import os

# Disable Flask-Migrate auto reloader which causes asyncio issues
os.environ.pop('WERKZEUG_RUN_MAIN', None)
os.environ['FLASK_DEBUG'] = '0'

# Try to import app
try:
    from app import app
    
    if __name__ == '__main__':
        print("=" * 60)
        print("Cyber World Store - Starting Server")
        print("=" * 60)
        print("Server: http://127.0.0.1:5000")
        print("Press CTRL+C to stop")
        print("=" * 60)
        
        # Run with minimal options to avoid reloader issues
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False,
            use_debugger=False,
            threaded=True
        )
except KeyboardInterrupt:
    print("\nServer stopped")
    sys.exit(0)
except Exception as e:
    print("Error: {}".format(e), file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
