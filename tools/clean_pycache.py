import os
import shutil
root='.'
removed=[]
for dirpath, dirnames, filenames in os.walk(root):
    if '__pycache__' in dirnames:
        path=os.path.join(dirpath,'__pycache__')
        try:
            shutil.rmtree(path)
            removed.append(path)
        except Exception:
            pass
    for fn in filenames:
        if fn.endswith('.pyc'):
            p=os.path.join(dirpath,fn)
            try:
                os.remove(p)
                removed.append(p)
            except Exception:
                pass
with open('clean_pycache_report.txt','w',encoding='utf-8') as f:
    if removed:
        f.write('\n'.join(removed))
    else:
        f.write('NONE')
