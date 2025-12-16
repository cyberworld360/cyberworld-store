from pathlib import Path
from importlib import util
import traceback
import os

# Set safe envs to avoid background threads or network calls during import
os.environ.setdefault('CI', '1')
os.environ.setdefault('FORCE_EPHEMERAL', '1')
os.environ.setdefault('DATABASE_URL', 'sqlite:///./data.db')
os.environ.setdefault('MAIL_SERVER', '')
os.environ.setdefault('PAYSTACK_SECRET', '')

# Load app module by file
spec = util.spec_from_file_location('app', str(Path(__file__).parent.parent / 'app.py'))
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = mod.app

try:
    with app.test_request_context('/'):
        from flask import render_template
        out = render_template('admin_base.html')
    with open('template_test_result.txt','w',encoding='utf-8') as f:
        f.write('RENDER_OK')
except Exception:
    with open('template_test_result.txt','w',encoding='utf-8') as f:
        f.write('RENDER_FAILED\n')
        f.write(traceback.format_exc())
