from kivy.uix.image import Image
from kivy.event import EventDispatcher
from kivy.properties import \
    NumericProperty, ReferenceListProperty, StringProperty, ObjectProperty, \
    BooleanProperty

from itertools import cycle, combinations



class GridEntry(EventDispatcher):
    xpos = NumericProperty(0)
    ypos = NumericProperty(0)



class Card:
    def __init__(self, suit=0, rank=1):
        self.suit = suit
        self.rank = rank
        if suit != None and rank != None:
            self.source = 'cards/s{}r{}.png'.format(self.suit, self.rank)
        else:
            self.source = 'cards/back1.png'

    def __str__(self):
        return 's{}r{}'.format(self.suit, self.rank)



class CardImage(Image, GridEntry, Card):
    source = StringProperty()
    def __init__(self, xpos, ypos, card, face_down=True):
        super(CardImage, self).__init__()
        self.xpos, self.ypos = xpos, ypos
        self.card = card
        self.suit, self.rank = card.suit, card.rank
        self.source = card.source
        self.face_down = face_down
        if self.face_down:
            self.flip()
            
    def flip(self):
        if self.face_down == True:
            self.face_down = False
            self.source = 'cards/back1.png'
        else:
            self.face_down = True
            self.source = self.card.source



class Deck:
    def __init__(self):
        self.cards = []
        for suit in range(4):
            for rank in range(1,14):
                self.cards.append(Card(suit, rank))

    def __str__(self):
        s = ''
        for i in range(len(self.cards)):
            s = s + ' '*i + str(self.cards[i]) + '\n'
        return s

    def shuffle(self):
        import random
        nCards = len(self.cards)
        for i in range(nCards):
            j = random.randrange(i, nCards)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def pop_card(self):
        return self.cards.pop()

    def is_empty(self):
        return (len(self.cards) == 0)

    def deal(self, hands, nCards=24):
        nHands = len(hands)
        for i in range(nCards):
            if self.is_empty(): break    # break if out of cards
            card = self.pop_card()       # take the top card
            hand = hands[i % nHands]     # whose turn is next?
            hand.add_card(card)          # add the card to the hand



class Player:
    def __init__(self, name, xpos=3, ypos=-1):
        self.cards = []
        self.score = 0
        self.name = name
        self.xpos, self.ypos = xpos, ypos
        
    def add_card(self, card):
        card_image = CardImage(xpos=self.xpos, ypos=self.ypos, card=card)
        self.cards.append(card_image)

    def pop_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()

    def is_empty(self):
        return (len(self.cards) == 0)



class GameEvents(EventDispatcher):
    round_over = BooleanProperty(False)
    game_over  = BooleanProperty(False)
    
    

class Game(GameEvents):
    def __init__(self, player_names):
        self.players = self.set_players(player_names)
        self.turn = self.cycle_players()
        self.round_over = False
        self.game_over  = False

    def set_players(self, player_names):
        if len(player_names) == 1:
            return [Player(player_names[0], xpos=3, ypos=-1)]
        if len(player_names) == 2:
            return [Player(player_names[0], xpos=2, ypos=-1), \
                    Player(player_names[1], xpos=4, ypos=-1)]
        if len(player_names) == 4:
            return [Player(player_names[0], xpos=2, ypos=-1), \
                    Player(player_names[1], xpos=4, ypos=-1), \
                    Player(player_names[2], xpos=1, ypos=-1), \
                    Player(player_names[3], xpos=5, ypos=-1)]

    def cycle_players(self):
        for player in cycle(self.players):
            yield player
            
    def play_round(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.deck.deal(self.players)
        self.starter = self.deck.pop_card()

        self.cards = {}
        self.current_player = self.turn.next()

    def is_round_over(self):
        return len(self.cards) == 25

    def round_over_callback(self, *args):
        self.round_over = True

    def is_game_over(self):
        for player in self.players:
            if player.score >= 50:
                return True
        return False

    def game_over_callback(self, *args):
        self.game_over = True
        
    def score_round(self):            
        coords = self.cards.keys()
        
        col_coords= [[(x,y) for (x,y) in coords if x==col] for col in range(1,6)]
        col_cards = [[self.cards[coord] for coord in col] for col in col_coords]
        self.col_score = self.score_cards(col_cards)

        row_coords= [[(x,y) for (x,y) in coords if y==row] for row in range(1,6)]
        row_cards = [[self.cards[coord] for coord in row] for row in row_coords]
        self.row_score = self.score_cards(row_cards)

        if len(self.players) > 1:
            print('Column Score:', self.col_score)
            print('Row Score:', self.row_score)
            
            if self.col_score > self.row_score:
                print('\n', 'Columns win!')
            elif self.row_score > self.col_score:
                print('\n', 'Rows win!')
            else:
                print('Tie Game!')

        else:
            self.solo_score = self.col_score + self.row_score
            if self.solo_score < 40:
                print('You scored %d. You are a worm.' % self.solo_score)
            elif 40 <= self.solo_score < 50:
                print('You scored %d. You are a crab.' % self.solo_score)
            elif 50 <= self.solo_score < 60:
                print('You scored %d. You are a baby.' % self.solo_score)
            elif 60 <= self.solo_score < 70:
                print('You scored %d. You are a child.' % self.solo_score)
            elif 70 <= self.solo_score < 80:
                print('You scored %d. You are a novice.' % self.solo_score)
            elif 80 <= self.solo_score < 90:
                print('You scored %d. You are an apprentice.' % self.solo_score)
            elif 90 <= self.solo_score < 100:
                print('You scored %d. You are a journeyman.' % self.solo_score)
            elif 100 <= self.solo_score < 110:
                print('You scored %d. You are an adept.' % self.solo_score)
            elif 110 <= self.solo_score < 120:
                print('You scored %d. You are a prodigy.' % self.solo_score)
            elif 120 <= self.solo_score < 130:
                print('You scored %d. You are a master.' % self.solo_score)
            elif self.solo_score >= 140:
                print('You scored %d. You are a grand master.' % self.solo_score)

    def score_cards(self, player_cards):
        round_score = 0
        for hand in player_cards:
            suits  = [card.suit for card in hand]
            ranks  = [card.rank for card in hand]
            values = [card.rank if card.rank <= 10 else 10 for card in hand]
            score  = 0
            score += self.score_fifteens(values)            
            score += self.score_pairs(ranks)            
            score += self.score_runs(ranks)       
            score += self.score_flush(suits)
            round_score += score
        return round_score

    def score_fifteens(self, values):
        fifteens = 0
        for combo_length in range(1,6):
            for combo in combinations(values, combo_length):
                if sum(combo) == 15:
                    fifteens += 1
        score = 2 * fifteens
        return score

    def score_pairs(self, ranks):
        pairs = 0
        for combo in combinations(ranks, 2):
            if combo[0]==combo[1]:
                pairs += 1
        score = 2 * pairs
        return score

    def score_runs(self, ranks):
        run_length = 0
        for combo_length in range(5, 2, -1):
            for combo in combinations(ranks, combo_length):
                combo = sorted(combo)
                if self.is_run(combo):
                    run_length += combo_length
            if run_length > 0:
                break
        score = run_length
        return score

    def is_run(self, combo):
        if len(combo) == 1:
            return True
        if combo[0] + 1 == combo[1]:
            return self.is_run(combo[1:])
        else:
            return False

    def score_flush(self, suits):
        if len(set(suits)) == 1:
            score = 5
        else:
            score = 0
        return score
