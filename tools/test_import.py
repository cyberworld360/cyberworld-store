import traceback
import importlib.util
from pathlib import Path
p = Path(__file__).parent.parent / 'app.py'
try:
    spec = importlib.util.spec_from_file_location('app', str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with open('import_report_direct.txt','w',encoding='utf-8') as fo:
        fo.write('IMPORTED_OK')
except Exception:
    with open('import_report_direct.txt','w',encoding='utf-8') as fo:
        fo.write('IMPORT_FAILED\n')
        fo.write(traceback.format_exc())
