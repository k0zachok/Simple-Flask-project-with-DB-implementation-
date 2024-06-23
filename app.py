from flask import Flask, jsonify, session, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from game import Game, Deck, Hand
from models import db, User, GameSession
import pickle
from flask_migrate import Migrate
import logging


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
    user = User.query.get(user_id)
    logged_in = user_id is not None
    return render_template('main.html', logged_in=logged_in, user=user)


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

        return render_template('register_success.html', user=user)
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
        return render_template('login_success.html', user=user)
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/leaderboard_data')
def leaderboard_data():
    users = User.query.order_by(User.points.desc()).all()
    leaderboard_data = [
        {
            'username': user.username,
            'points': user.points,
            'rank': user.rank
        }
        for user in users
    ]
    return jsonify(leaderboard_data)

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/friends_leaderboard_data')
def friends_leaderboard_data():
    user_id = session.get('user_id')
    if not user_id:
        return "Not logged in", 401

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    friends = user.get_friends()
    friend_ids = [friend.id for friend in friends]
    friends_and_user = [user.id] + friend_ids

    users = User.query.filter(User.id.in_(friends_and_user)).order_by(User.points.desc()).all()

    leaderboard_data = [
        {
            'username': user.username,
            'points': user.points,
            'rank': user.rank
        }
        for user in users
    ]

    return jsonify(leaderboard_data)

@app.route('/friends', methods=['GET'])
def friends():
    return render_template('friends.html')

@app.route('/send_friend_request/<friend_username>', methods=['POST'])
def send_friend_request(friend_username):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    friend = User.query.filter_by(username=friend_username).first()
    if not friend:
        return jsonify({'message': 'User not found'}), 404
    user.send_friend_request(friend)
    return jsonify({'message': 'Friend request sent'})


@app.route('/accept_friend_request/<friend_username>', methods=['POST'])
def accept_friend_request(friend_username):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    friend = User.query.filter_by(username=friend_username).first()
    if not friend:
        return jsonify({'message': 'User not found'}), 404
    user.accept_friend_request(friend)
    return jsonify({'message': 'Friend request accepted'})

@app.route('/reject_friend_request/<friend_username>', methods=['POST'])
def reject_friend_request(friend_username):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    friend = User.query.filter_by(username=friend_username).first()
    if not friend:
        return jsonify({'message': 'User not found'}), 404
    user.reject_friend_request(friend)
    return jsonify({'message': 'Friend request rejected'})

@app.route('/remove_friend/<friend>', methods=['POST'])
def remove_friend(friend):
    user_id = session.get('user_id')
    if not user_id:
        return 'User is not logged in'
    user = User.query.get(user_id)
    friend_user = User.query.filter_by(username=friend).first()
    if friend_user:
        user.remove_friend(friend_user)
        return jsonify({'message': 'Friend removed'}), 200
    else:
        return jsonify({'message': 'Friend not found'}), 404

@app.route('/get_friends', methods=['GET'])
def get_friends():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    friends = [friend.username for friend in user.get_friends()]
    return jsonify({'friends': friends})

@app.route('/get_sent_requests', methods=['GET'])
def get_sent_requests():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    sent_requests = [request.username for request in user.get_sent_requests()]
    return jsonify({'sent_requests': sent_requests})

@app.route('/get_received_requests', methods=['GET'])
def get_received_requests():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    received_requests = [request.username for request in user.get_received_requests()]
    return jsonify({'received_requests': received_requests})


@app.route('/place_bet', methods=['GET'])
def place_bet():
    return render_template('place_bet.html')

@app.route('/make_bet', methods=['POST'])
def make_bet():
    bet = request.form.get('bet')
    if not bet:
        return "No bet entered", 400
    user_id = session.get('user_id')
    if not user_id:
        return "Not logged in", 401

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404
    user_balance = user.balance
    print(user_balance)
    bet = int(bet)
    if bet <= 0:
        return "Invalid bet", 400
    if bet > user_balance:
        return 'Not enough money :('
    session['bet'] = bet
    return redirect(url_for('start_game'))

@app.route('/start_game', methods=['GET'])
def start_game():
    user_id = session.get('user_id')
    if not user_id:
        return "Not logged in", 401

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    game_session = GameSession.query.filter_by(user_id=user_id, active=True).first()
    if not game_session:
        bet = session.get('bet')
        if not bet:
            return "No bet placed", 400
        deck = Deck()
        deck.shuffle()

        player_hand = Hand()
        dealer_hand = Hand(dealer=True)

        for i in range(2):
            player_hand.add_card(deck.deal(1))
            dealer_hand.add_card(deck.deal(1))

        game_session = GameSession(user=user, deck=pickle.dumps(deck), player_hand=pickle.dumps(player_hand), dealer_hand=pickle.dumps(dealer_hand), active=True)
        db.session.add(game_session)
        game_session.bet = bet
        print(f'in start game new game {bet}')
        db.session.commit()

        session['game_session_id'] = game_session.id
        logging.info(f"New game session created with id {game_session.id}")
        # dd_allow = pickle.loads(game_session.double_down)
        user_id = session.get('user_id')
        if not user_id:
            return "Not logged in", 401

        user = User.query.get(user_id)
        if not user:
            return "User not found", 404

    else:
        bet = session.get('bet')
        print(f'in start game {bet}')
        game_session.bet = bet
        db.session.commit()
        session['game_session_id'] = game_session.id
        player_hand = pickle.loads(game_session.player_hand)
        dealer_hand = pickle.loads(game_session.dealer_hand)
        # dd_allow = game_session.double_down
        user_id = session.get('user_id')
        if not user_id:
            return "Not logged in", 401

        user = User.query.get(user_id)
        if not user:
            return "User not found", 404


    return render_template('start_game.html', player_hand=player_hand, dealer_hand=dealer_hand, user=user, game_session=game_session, double_down=game_session.double_down)



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
    game_session.double_down = None
    db.session.commit()
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    winner = game.check_winner(player_hand, pickle.loads(game_session.dealer_hand), False, user.username)
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
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    winner = game.check_winner(pickle.loads(game_session.player_hand), dealer_hand, True, user.username)
    if winner:
        game_session.winner = winner
        return redirect(url_for('game_over'))

    return redirect(url_for('start_game'))


@app.route('/double_down', methods=['POST'])
def double_down():
    game_session_id = session.get('game_session_id')
    if not game_session_id:
        return "No game in progress", 400

    game_session = GameSession.query.get(game_session_id)
    if not game_session:
        return "Game not found", 404

    bet = game_session.bet
    bet *= 2
    game_session.bet = bet

    player_hand = pickle.loads(game_session.player_hand)
    deck = pickle.loads(game_session.deck)
    dealer_hand =  pickle.loads(game_session.dealer_hand)

    player_hand.add_card(deck.deal(1))

    while dealer_hand.get_value() < 17:
        dealer_hand.add_card(deck.deal(1))

    game_session.dealer_hand = pickle.dumps(dealer_hand)
    game_session.player_hand = pickle.dumps(player_hand)
    game_session.deck = pickle.dumps(deck)

    db.session.commit()
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    winner = game.check_winner(player_hand, dealer_hand, True, user.username)
    if winner:
        game_session.winner = winner
        return redirect(url_for('game_over'))

    return redirect(url_for('start_game'))



@app.route('/game_over', methods=['GET'])
def game_over():
    game_session_id = session.get('game_session_id')
    user_id = session.get('user_id')
    if not user_id:
        return "Not logged in", 401

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404
    game_session = GameSession.query.filter_by(user_id=user_id, active=True).first()
    if game_session_id:
        game_session = GameSession.query.get(game_session_id)
        if game_session == None:
            return 'game sess not created'
    bet = game_session.bet
    print(f' in game over bet {bet}')
    winner = game.check_winner(pickle.loads(game_session.player_hand), pickle.loads(game_session.dealer_hand), True, user.username)
    if winner == user.username:
        user.balance += bet
        user.points += 15
        if user.points < 30:
            user.rank = 'Newbie'
        elif user.points >= 30 and user.points < 70:
            user.rank = 'Apprentice'
        elif user.points >= 70 and user.points < 120:
            user.rank = 'Rookie'
        elif user.points >= 120 and user.points < 200:
            user.rank = 'Amateur'
        elif user.points >= 200 and user.points < 300:
            user.rank = 'Expert'
        elif user.points >= 300 and user.points < 500:
            user.rank = 'Card Shark'
        elif user.points >= 500 and user.points < 700:
            user.rank = 'High Roller'
        elif user.points >= 700:
            user.rank = 'Blackjack Master'

    if winner == 'Dealer':
        user.balance -= bet
        if user.points >= 10:
            user.points -= 10
            if user.points < 30:
                user.rank = 'Newbie'
            elif user.points >= 30 and user.points < 70:
                user.rank = 'Apprentice'
            elif user.points >= 70 and user.points < 120:
                user.rank = 'Rookie'
            elif user.points >= 120 and user.points < 200:
                user.rank = 'Amateur'
            elif user.points >= 200 and user.points < 300:
                user.rank = 'Expert'
            elif user.points >= 300 and user.points < 500:
                user.rank = 'Card Shark'
            elif user.points >= 500 and user.points < 700:
                user.rank = 'High Roller'
            elif user.points >= 700:
                user.rank = 'Blackjack Master'
    else:
        user.balance = user.balance
    if game_session:
        db.session.delete(game_session)
        db.session.commit()

    return render_template('game_over.html', player_hand=pickle.loads(game_session.player_hand), dealer_hand=pickle.loads(game_session.dealer_hand), winner=winner)

