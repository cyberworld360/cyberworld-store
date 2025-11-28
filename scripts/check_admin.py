import os, sys
sys.path.insert(0, os.getcwd())
from app import app, db, AdminUser

with app.app_context():
    db.create_all()
    admin = AdminUser.query.filter_by(username='testadmin').first()
    if not admin:
        admin = AdminUser(username='testadmin')
        admin.set_password('secret')
        db.session.add(admin)
        db.session.commit()

client = app.test_client()
resp = client.post('/admin/login', data={'username':'testadmin','password':'secret'}, follow_redirects=True)
print('/admin/login ->', resp.status_code)
resp = client.get('/admin/settings')
print('/admin/settings ->', resp.status_code)
