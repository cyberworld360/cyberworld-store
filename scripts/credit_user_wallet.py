import os, sys
sys.path.insert(0, os.getcwd())
from app import app, db, User

email = 'smoketest@example.com'
amount = '100'

with app.app_context():
    user = User.query.filter_by(email=email).first()
    if not user:
        print('User not found')
    else:
        if not user.wallet:
            from app import Wallet
            user.wallet = Wallet(user_id=user.id, balance=0)
        user.wallet.balance = float(user.wallet.balance) + float(amount)
        db.session.commit()
        print('credited user', user.email, 'new balance', user.wallet.balance)
