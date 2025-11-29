import os
os.environ['DATABASE_URL'] = 'postgres://user:pass@host:5432/dbname?sslmode=require'
# Avoid lingering SQLALCHEMY_DATABASE_URI from env
os.environ.pop('SQLALCHEMY_DATABASE_URI', None)
# Importing app will run normalization
import importlib.util
spec = importlib.util.spec_from_file_location('app', os.path.join(os.path.dirname(__file__), '..', 'app.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('SQLALCHEMY_DATABASE_URI:', mod.app.config.get('SQLALCHEMY_DATABASE_URI'))
