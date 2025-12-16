import traceback
try:
    with open('app.py','r',encoding='utf-8') as f:
        src = f.read()
    compile(src, 'app.py', 'exec')
    with open('compile_report.txt','w',encoding='utf-8') as fo:
        fo.write('OK')
except Exception as e:
    with open('compile_report.txt','w',encoding='utf-8') as fo:
        fo.write('ERROR:\n')
        fo.write(traceback.format_exc())
