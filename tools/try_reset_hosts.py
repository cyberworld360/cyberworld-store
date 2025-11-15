import requests

urls = [
    'https://www.cyberworldstore.shop/__admin_reset',
    'https://cyberworld-store-o5yterqrh-cyber-shop360.vercel.app/__admin_reset',
    'https://cyberworld-store-n2ir4vzqc-cyber-shop360.vercel.app/__admin_reset',
    'https://cyberworld-store-5l63rg4mw-cyber-shop360.vercel.app/__admin_reset',
    'https://cyberworld-store-ksp7ts83k-cyber-shop360.vercel.app/__admin_reset',
    'https://cyberworld-store-nld9cs2wq-cyber-shop360.vercel.app/__admin_reset',
]

data = {'token':'reset-XYZ-2025','username':'admin','password':'GITG360'}

for u in urls:
    try:
        r = requests.post(u, data=data, timeout=20)
        print('URL:', u)
        print('STATUS:', r.status_code)
        text = r.text.strip()
        print('BODY (first 500 chars):')
        print(text[:500])
        print('-'*80)
    except Exception as e:
        print('URL:', u)
        print('ERROR:', e)
        print('-'*80)
