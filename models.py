from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PickleType, Boolean

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Integer, default=1000)

    def __repr__(self):
        return '<User %r>' % self.username


class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deck = db.Column(PickleType)
    bet = db.Column(db.Integer)
    player_hand = db.Column(PickleType)
    dealer_hand = db.Column(PickleType)
    winner = db.Column(db.String(40)) #?
    active = db.Column(Boolean, default=True)
    user = db.relationship('User', backref='game_sessions')
    double_down = db.Column(db.String(20), default='allow')

    def __repr__(self):
        return '<GameSession %r>' % self.id