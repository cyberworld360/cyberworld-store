from asgiref.wsgi import WsgiToAsgi
from app import app as flask_app

# Wrap the Flask WSGI app to an ASGI app so Vercel's Python runtime can serve it
app = WsgiToAsgi(flask_app)
