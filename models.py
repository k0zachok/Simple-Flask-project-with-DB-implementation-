from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PickleType

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

# class GameSession(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     user = db.relationship('User', backref=db.backref('game_sessions', lazy=True))
#     deck = db.Column(db.PickleType, nullable=False)
#     player_hand = db.Column(db.PickleType, nullable=False)
#     dealer_hand = db.Column(db.PickleType, nullable=False)

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    deck = db.Column(PickleType)
    player_hand = db.Column(PickleType)
    dealer_hand = db.Column(PickleType)
    winner = db.Column(db.String(40)) #?
    user = db.relationship('User')

    def __repr__(self):
        return '<GameSession %r>' % self.id