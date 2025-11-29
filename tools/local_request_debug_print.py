import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
os.environ['DATABASE_URL'] = 'sqlite:///./data.db'
os.environ['FORCE_EPHEMERAL'] = '1'
os.environ['FLASK_DEBUG'] = '1'

from app import app

with app.test_client() as c:
    try:
        resp = c.get('/')
        content = resp.get_data(as_text=True)
        with open('tools/local_root_output.html', 'w', encoding='utf-8') as fh:
            fh.write(f'STATUS: {resp.status}\n')
            fh.write('HEADERS:\n')
            fh.write('\n'.join([f'{k}: {v}' for k,v in resp.headers.items()]))
            fh.write('\n\n')
            fh.write(content)
        print('Wrote tools/local_root_output.html')
    except Exception as exc:
        import traceback
        with open('tools/local_root_output.html', 'w', encoding='utf-8') as fh:
            fh.write('EXC:\n')
            traceback.print_exc(file=fh)
        print('Wrote exception to tools/local_root_output.html')
