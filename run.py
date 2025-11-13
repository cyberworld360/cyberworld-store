#!/usr/bin/env python
"""Simple runner without debug mode to avoid reloader issues"""
import os
os.environ['FLASK_DEBUG'] = '0'

from app import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
