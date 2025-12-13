import os
import sys

# Ensure project root on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db

if __name__ == '__main__':
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    with app.app_context():
        print('SQLALCHEMY_DATABASE_URI =', app.config.get('SQLALCHEMY_DATABASE_URI'))
        print('Creating DB tables via SQLAlchemy create_all()')
        db.create_all()
        print('create_all finished')