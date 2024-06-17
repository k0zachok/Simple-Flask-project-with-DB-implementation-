import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank['rank']} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = []
        suits = ["spades", "clubs", "hearts", "diamonds"]
        ranks = [
            {"rank": "A", "value": 11},
            {"rank": "2", "value": 2},
            {"rank": "3", "value": 3},
            {"rank": "4", "value": 4},
            {"rank": "5", "value": 5},
            {"rank": "6", "value": 6},
            {"rank": "7", "value": 7},
            {"rank": "8", "value": 8},
            {"rank": "9", "value": 9},
            {"rank": "10", "value": 10},
            {"rank": "J", "value": 10},
            {"rank": "Q", "value": 10},
            {"rank": "K", "value": 10},
        ]
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

    @classmethod
    def from_dict(cls, data):
        deck = cls()
        deck.cards = [Card(rank=card['rank'], suit=card['suit']) for card in data['cards']]
        return deck

    def shuffle(self):
        if len(self.cards) > 1:
            random.shuffle(self.cards)

    def deal(self, number):
        cards_dealt = []
        for x in range(number):
            if len(self.cards) > 0:
                card = self.cards.pop()
                cards_dealt.append(card)
        return cards_dealt

    def to_dict(self):
        return {
            'cards': [card.__dict__ for card in self.cards]
        }

class Hand:
    def __init__(self, dealer=False):
        self.cards = []
        self.value = 0
        self.dealer = dealer


    @classmethod
    def from_dict(cls, data):
        hand = cls(dealer=data.get('dealer', False))
        hand.cards = [Card(rank=card['rank'], suit=card['suit']) for card in data['cards']]
        return hand

    def add_card(self, card_list):
        self.cards.extend(card_list)

    def calculate_value(self):
        self.value = 0
        has_ace = False

        for card in self.cards:
            card_value = int(card.rank["value"])
            self.value += card_value
            if card.rank["rank"] == "A":
                has_ace = True

        if has_ace and self.value > 21:
            self.value -= 10

    def get_value(self):
        self.calculate_value()
        return self.value

    def is_blackjack(self):
        return self.get_value() == 21

    def display(self, show_all_dealer_cards=False):
        print(f'''{"Dealer's" if self.dealer else "Your"} hand:''')
        for index, card in enumerate(self.cards):
            if index == 0 and self.dealer \
                    and not show_all_dealer_cards and not self.is_blackjack():
                print("hidden")
            else:
                print(card)

        if not self.dealer:
            print("Value:", self.get_value())
        print()

    def to_dict(self):
        return {
            'cards': [card.__dict__ for card in self.cards],
            'value': self.get_value(),
            'dealer': self.dealer
        }


class Game:
    # ... (rest of your code)

    def play(self):
        game_number = 0
        game_data = {}

        deck = Deck()
        deck.shuffle()

        player_hand = Hand()
        dealer_hand = Hand(dealer=True)

        for i in range(2):
            player_hand.add_card(deck.deal(1))
            dealer_hand.add_card(deck.deal(1))

        dealer_hand_value = dealer_hand.get_value()

        game_data['game_number'] = game_number
        game_data['player_hand'] = player_hand.get_value()
        game_data['dealer_hand'] = dealer_hand.get_value()
        game_data['dealer_hand_value'] = dealer_hand_value

        game_over = self.check_winner(player_hand, dealer_hand, False)
        if game_over:
            game_data['game_over'] = True
            game_data['winner'] = self.check_winner(player_hand, dealer_hand, True)
            return game_data

        while player_hand.get_value() < 21:
            player_hand.add_card(deck.deal(1))

        game_over = self.check_winner(player_hand, dealer_hand, False)
        if game_over:
            game_data['game_over'] = True
            game_data['winner'] = self.check_winner(player_hand, dealer_hand, True)
            return game_data

        while dealer_hand.get_value() < 17:
            dealer_hand.add_card(deck.deal(1))

        game_over = self.check_winner(player_hand, dealer_hand, False)
        if game_over:
            game_data['game_over'] = True
            game_data['winner'] = self.check_winner(player_hand, dealer_hand, True)
            return game_data

        game_data['final_results'] = {
            'player_hand': player_hand.get_value(),
            'dealer_hand': dealer_hand.get_value()
        }

        game_over = self.check_winner(player_hand, dealer_hand, True)
        if game_over:
            game_data['game_over'] = True
            game_data['winner'] = self.check_winner(player_hand, dealer_hand, True)

        return game_data

    # def check_winner(self, player_hand, dealer_hand, game_over=False):
    #     if not game_over:
    #         if player_hand.get_value() > 21:
    #             return "Dealer"
    #         elif dealer_hand.get_value() > 21:
    #             return "Player"
    #         elif dealer_hand.is_blackjack() and player_hand.is_blackjack():
    #             return "Tie"
    #         elif player_hand.is_blackjack():
    #             return "Player"
    #         elif dealer_hand.is_blackjack():
    #             return "Dealer"
    #         elif player_hand.get_value() > dealer_hand.get_value():
    #             return "Player"
    #         elif player_hand.get_value() < dealer_hand.get_value():
    #             return "Dealer"
    #     else:
    #         #add cases of blackjack
    #         if player_hand.get_value() > dealer_hand.get_value():
    #             return "Player"
    #         elif player_hand.get_value() == dealer_hand.get_value():
    #             return "Tie"
    #         else:
    #             return "Dealer"
    #     return None

    def check_winner(self, player_hand, dealer_hand, game_over, player_username):
        if game_over:  # If the player has chosen to stand
            if dealer_hand.get_value() > 21:
                return player_username
            elif player_hand.get_value() > 21:
                return 'Dealer'
            elif player_hand.get_value() > dealer_hand.get_value():
                return player_username
            elif player_hand.get_value() < dealer_hand.get_value():
                return 'Dealer'
            else:
                return 'Draw'
        else:  # If the player has chosen to hit
            if player_hand.get_value() > 21:
                return 'Dealer'
            elif player_hand.get_value() == 21:
                return player_username
            else:
                return None

# g = Game()
# g.play()
