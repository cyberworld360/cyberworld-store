import sys
p='app.py'
out = []
with open(p,'r',encoding='utf-8') as f:
    for i,l in enumerate(f, start=1):
        if '\t' in l:
            out.append(f"{i}: {l.rstrip()}\n")
with open('tabs_report.txt','w',encoding='utf-8') as fo:
    if out:
        fo.writelines(out)
    else:
        fo.write('NO_TABS')
