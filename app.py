from flask import Flask, jsonify, session, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from game import Game, Deck, Hand
from models import db, User, GameSession
import pickle
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db.init_app(app)

migrate = Migrate(app, db)

app.secret_key = '1606c26f342be029e22d51b06d029d94'
game = Game()

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    user_id = session.get('user_id')
    logged_in = user_id is not None
    return render_template('main.html', logged_in=logged_in)

# @app.route('/start_game', methods=['GET'])
# def start_game():
#     if 'deck' not in session:
#         deck = Deck()
#         deck.shuffle()
#
#         player_hand = Hand()
#         dealer_hand = Hand(dealer=True)
#
#         for i in range(2):
#             player_hand.add_card(deck.deal(1))
#             dealer_hand.add_card(deck.deal(1))
#
#         session['deck'] = deck.to_dict()
#         session['player_hand'] = player_hand.to_dict()
#         session['dealer_hand'] = dealer_hand.to_dict()
#     else:
#         deck = Deck.from_dict(session.get('deck'))
#         player_hand = Hand.from_dict(session.get('player_hand'))
#         dealer_hand = Hand.from_dict(session.get('dealer_hand'))
#
#         # player_hand = Hand.from_dict(session['player_hand'])
#         # dealer_hand = Hand.from_dict(session['dealer_hand'])
#
#     # return render_template('start_game.html', player_hand=player_hand, dealer_hand=dealer_hand)
#     return render_template('start_game.html', player_hand=session['player_hand'], dealer_hand=session['dealer_hand'])


# @app.route('/hit', methods=['POST'])
# def hit():
#     deck = Deck.from_dict(session.get('deck'))
#     player_hand = Hand.from_dict(session.get('player_hand'))
#
#     player_hand.add_card(deck.deal(1))
#     session['player_hand'] = player_hand.to_dict()
#     session['deck'] = deck.to_dict()
#
#     winner = game.check_winner(player_hand, Hand.from_dict(session.get('dealer_hand')), False)
#     if winner:
#         session['winner'] = winner
#         return redirect(url_for('game_over'))
#
#     return redirect(url_for('start_game'))
#
# @app.route('/stand', methods=['POST'])
# def stand():
#     deck = Deck.from_dict(session.get('deck'))
#     dealer_hand = Hand.from_dict(session.get('dealer_hand'))
#
#     while dealer_hand.get_value() < 17:
#         dealer_hand.add_card(deck.deal(1))
#
#     session['dealer_hand'] = dealer_hand.to_dict()
#
#     winner = game.check_winner(Hand.from_dict(session.get('player_hand')), dealer_hand, True)
#     if winner:
#         session['winner'] = winner
#         return redirect(url_for('game_over'))
#
#     return redirect(url_for('start_game'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            return "User already exists", 400

        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        return render_template('register_success.html')
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return "Invalid username or password", 401

        session['user_id'] = user.id
        return render_template('login_success.html')
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))


# @app.route('/game_over', methods=['GET'])
# def game_over():
#     winner = session.get('winner')
#     dealer_hand = session.get('dealer_hand')
#     player_hand = session.get('player_hand')
#     session.clear()  # Clear the session to start a new game
#     return render_template('game_over.html', winner=winner, dealer_hand=dealer_hand, player_hand=player_hand)


@app.route('/start_game', methods=['GET'])
def start_game():
    user_id = session.get('user_id')
    if not user_id:
        return "Not logged in", 401

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    game_session_id = session.get('game_session_id')
    game_session = None
    if game_session_id:
        game_session = GameSession.query.get(game_session_id)

    if not game_session:
        # Game session does not exist, start a new game
        deck = Deck()
        deck.shuffle()

        player_hand = Hand()
        dealer_hand = Hand(dealer=True)

        for i in range(2):
            player_hand.add_card(deck.deal(1))
            dealer_hand.add_card(deck.deal(1))

        game_session = GameSession(user=user, deck=pickle.dumps(deck), player_hand=pickle.dumps(player_hand), dealer_hand=pickle.dumps(dealer_hand))
        db.session.add(game_session)
        db.session.commit()

        session['game_session_id'] = game_session.id

    player_hand = pickle.loads(game_session.player_hand)
    dealer_hand = pickle.loads(game_session.dealer_hand)

    return render_template('start_game.html', player_hand=pickle.loads(game_session.player_hand), dealer_hand=pickle.loads(game_session.dealer_hand))

@app.route('/hit', methods=['POST'])
def hit():
    game_session_id = session.get('game_session_id')
    if not game_session_id:
        return "No game in progress", 400

    game_session = GameSession.query.get(game_session_id)
    if not game_session:
        return "Game not found", 404

    player_hand = pickle.loads(game_session.player_hand)
    deck = pickle.loads(game_session.deck)

    player_hand.add_card(deck.deal(1))

    game_session.player_hand = pickle.dumps(player_hand)
    game_session.deck = pickle.dumps(deck)

    db.session.commit()

    winner = game.check_winner(player_hand, pickle.loads(game_session.dealer_hand), False)
    if winner:
        game_session.winner = winner
        return redirect(url_for('game_over'))

    return redirect(url_for('start_game'))

@app.route('/stand', methods=['POST'])
def stand():
    game_session_id = session.get('game_session_id')
    if not game_session_id:
        return "No game in progress", 400

    game_session = GameSession.query.get(game_session_id)
    if not game_session:
        return "Game not found", 404

    dealer_hand = pickle.loads(game_session.dealer_hand)
    deck = pickle.loads(game_session.deck)

    while dealer_hand.get_value() < 17:
        dealer_hand.add_card(deck.deal(1))

    game_session.dealer_hand = pickle.dumps(dealer_hand)
    game_session.deck = pickle.dumps(deck)

    db.session.commit()

    winner = game.check_winner(pickle.loads(game_session.player_hand), dealer_hand, True)
    if winner:
        game_session.winner = winner
        return redirect(url_for('game_over'))

    return redirect(url_for('start_game'))

@app.route('/game_over', methods=['GET'])
def game_over():
    game_session_id = session.get('game_session_id')
    if game_session_id:
        game_session = GameSession.query.get(game_session_id)
        winner = game.check_winner(pickle.loads(game_session.player_hand), pickle.loads(game_session.dealer_hand), True)
        if game_session:
            db.session.delete(game_session)
            db.session.commit()

    return render_template('game_over.html', player_hand=pickle.loads(game_session.player_hand), dealer_hand=pickle.loads(game_session.dealer_hand), winner=winner)