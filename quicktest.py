# quicktest.py
from app import app, db, User

with app.app_context():
    users = User.query.all()
    for user in users:
        print(user.username, user.points, user.rank)
