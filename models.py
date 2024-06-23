from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PickleType, Boolean, or_, and_

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Integer, default=1000)
    friends = db.relationship("Friendship", foreign_keys='Friendship.user_id', back_populates="user", lazy='dynamic')
    sent_requests = db.relationship("Friendship", foreign_keys='Friendship.user_id', back_populates="user", lazy='dynamic')
    received_requests = db.relationship("Friendship", foreign_keys='Friendship.friend_id', back_populates="friend",lazy='dynamic')
    points = db.Column(db.Integer, default=0)
    rank = db.Column(db.String(30), default='Newbie')

    def send_friend_request(self, user):
        if user not in self.get_friends():
            friendship = Friendship(user_id=self.id, friend_id=user.id, status='pending')
            db.session.add(friendship)
            db.session.commit()

    def accept_friend_request(self, user):
        friendship = Friendship.query.filter_by(user_id=user.id, friend_id=self.id, status='pending').first()
        if friendship:
            friendship.status = 'accepted'
            db.session.commit()

            reverse_friendship = Friendship(user_id=self.id, friend_id=user.id, status='accepted')
            db.session.add(reverse_friendship)
            db.session.commit()

    def reject_friend_request(self, user):
        friendship = Friendship.query.filter_by(user_id=user.id, friend_id=self.id, status='pending').first()
        if friendship:
            db.session.delete(friendship)
            db.session.commit()

    def remove_friend(self, user):
        friendships = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == self.id, Friendship.friend_id == user.id, Friendship.status == 'accepted'),
                and_(Friendship.user_id == user.id, Friendship.friend_id == self.id, Friendship.status == 'accepted')
            )
        ).all()
        for friendship in friendships:
            db.session.delete(friendship)
        db.session.commit()

    def get_friends(self):
        return [friendship.friend for friendship in self.friends if friendship.status == 'accepted']

    def get_received_requests(self):
        return [friendship.user for friendship in self.received_requests if friendship.status == 'pending']

    def get_sent_requests(self):
        return [friendship.friend for friendship in self.sent_requests if friendship.status == 'pending']

    def __repr__(self):
        return '<User %r>' % self.username

class Friendship(db.Model):
    __tablename__ = 'friendships'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    user = db.relationship("User", foreign_keys=[user_id], back_populates="friends")
    friend = db.relationship("User", foreign_keys=[friend_id], back_populates="received_requests")

    def __repr__(self):
        return '<Friendship %r>' % self.id


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