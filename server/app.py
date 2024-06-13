from flask import Flask, jsonify, session, render_template, redirect, url_for
from game import Game, Deck, Hand



app = Flask(__name__)
app.secret_key = '1606c26f342be029e22d51b06d029d94'
game = Game()

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/start_game', methods=['GET'])
def start_game():
    if 'deck' not in session:
        deck = Deck()
        deck.shuffle()

        player_hand = Hand()
        dealer_hand = Hand(dealer=True)

        for i in range(2):
            player_hand.add_card(deck.deal(1))
            dealer_hand.add_card(deck.deal(1))

        session['deck'] = deck.to_dict()
        session['player_hand'] = player_hand.to_dict()
        session['dealer_hand'] = dealer_hand.to_dict()
    else:
        deck = Deck.from_dict(session.get('deck'))
        player_hand = Hand.from_dict(session.get('player_hand'))
        dealer_hand = Hand.from_dict(session.get('dealer_hand'))

        # player_hand = Hand.from_dict(session['player_hand'])
        # dealer_hand = Hand.from_dict(session['dealer_hand'])

    # return render_template('start_game.html', player_hand=player_hand, dealer_hand=dealer_hand)
    return render_template('start_game.html', player_hand=session['player_hand'], dealer_hand=session['dealer_hand'])

# @app.route('/deal', methods=['POST'])
# def deal():
#     deck = session.get('deck')
#     cards = deck.deal(1)
#     return jsonify(cards=[card.__dict__ for card in cards]), 200

@app.route('/hit', methods=['POST'])
def hit():
    deck = Deck.from_dict(session.get('deck'))
    player_hand = Hand.from_dict(session.get('player_hand'))

    player_hand.add_card(deck.deal(1))
    session['player_hand'] = player_hand.to_dict()
    session['deck'] = deck.to_dict()

    winner = game.check_winner(player_hand, Hand.from_dict(session.get('dealer_hand')), False)
    if winner:
        session['winner'] = winner
        return redirect(url_for('game_over'))

    return redirect(url_for('start_game'))

@app.route('/stand', methods=['POST'])
def stand():
    deck = Deck.from_dict(session.get('deck'))
    dealer_hand = Hand.from_dict(session.get('dealer_hand'))

    while dealer_hand.get_value() < 17:
        dealer_hand.add_card(deck.deal(1))

    session['dealer_hand'] = dealer_hand.to_dict()

    winner = game.check_winner(Hand.from_dict(session.get('player_hand')), dealer_hand, True)
    if winner:
        session['winner'] = winner
        return redirect(url_for('game_over'))

    return redirect(url_for('start_game'))

@app.route('/game_over', methods=['GET'])
def game_over():
    winner = session.get('winner')
    dealer_hand = session.get('dealer_hand')
    player_hand = session.get('player_hand')
    session.clear()  # Clear the session to start a new game
    return render_template('game_over.html', winner=winner, dealer_hand=dealer_hand, player_hand=player_hand)