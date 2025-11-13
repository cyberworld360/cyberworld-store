#!/usr/bin/env python3
"""
Check all Jinja2 templates for syntax errors by loading them via Flask's jinja_env.
Print any TemplateSyntaxError or other exceptions with filename and message.
"""
import sys
import os
from flask import Flask

# ensure project root is on path
ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)

from app import app
from jinja2 import TemplateSyntaxError

failed = False
print("Checking templates via app.jinja_env.list_templates()...\n")
try:
    tmpl_names = app.jinja_env.list_templates()
except Exception as e:
    print("ERROR: Unable to list templates:", e)
    raise

for name in sorted(tmpl_names):
    try:
        # Attempt to load/compile the template
        app.jinja_env.get_template(name)
        print(f"OK: {name}")
    except TemplateSyntaxError as tse:
        failed = True
        print(f"SYNTAX ERROR in {name}: {tse.message} (line {tse.lineno})")
    except Exception as e:
        failed = True
        print(f"ERROR loading {name}: {e}")

if failed:
    print("\nOne or more templates failed to load.")
    sys.exit(2)
else:
    print("\nAll templates loaded successfully.")
    sys.exit(0)
