from app import app, db

if __name__ == '__main__':
    with app.app_context():
        print('Creating tables...')
        db.create_all()
        print('Done creating tables')
