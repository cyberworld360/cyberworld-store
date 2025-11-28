import ast, sys
p='c:/Users/CYBER360/Desktop/cyberworld_paystack_clone_final/app.py'
try:
    with open(p,'r', encoding='utf-8') as f:
        s=f.read()
    ast.parse(s)
    print('AST parse OK')
except Exception as e:
    print('AST parse error:')
    import traceback
    traceback.print_exc()