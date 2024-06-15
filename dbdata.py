from flask import Flask
from models import db, User, GameSession

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'  # replace with your actual database URI
db.init_app(app)


# with app.app_context():
#     # Delete all game sessions
#     GameSession.query.delete()
#     db.session.commit()


#session id still exists somehow even though i deleted all the sessions.
# have tp find out how it is and also change method check if sess
# active in start_game


with app.app_context():
    # Query all users
    users = User.query.all()
    for user in users:
        if user == '':
            print('no users')
        else:
            user.balance = 1000
            print(f'User ID: {user.id}, Username: {user.username}, Balance: {user.balance}')

    # Query all game sessions
    game_sessions = GameSession.query.all()
    for game_session in game_sessions:
        print(f'Game Session ID: {game_session.id}, User ID: {game_session.user_id}')