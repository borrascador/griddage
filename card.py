from kivy.event import EventDispatcher
from kivy.properties import \
    NumericProperty, ReferenceListProperty, StringProperty, ObjectProperty, \
    BooleanProperty, ListProperty, BoundedNumericProperty
from kivy.uix.image import Image

from itertools import cycle, combinations
from random import choice



class GridEntry(EventDispatcher):
    xpos = NumericProperty(0)
    ypos = NumericProperty(0)



class Card:
    def __init__(self, card_back, suit=0, rank=1):
        self.suit = suit
        self.rank = rank
        self.card_back = card_back
        if suit != None and rank != None:
            self.source = 'cards/s{}r{}.png'.format(self.suit, self.rank)
        else:
            self.source = 'cards/back{}.png'.format(str(self.card_back))

    def __str__(self):
        return 's{}r{}'.format(self.suit, self.rank)



class CardImage(Image, GridEntry, Card):
    source = StringProperty()
    def __init__(self, xpos, ypos, card, face_down=True):
        super(CardImage, self).__init__()
        self.xpos, self.ypos = xpos, ypos
        self.card = card
        self.suit, self.rank = card.suit, card.rank
        self.card_back = card.card_back
        self.source = card.source
        self.face_down = face_down
        if self.face_down:
            self.flip()
            
    def flip(self):
        if self.face_down == True:
            self.face_down = False
            self.source = 'cards/back{}.png'.format(self.card_back)
        else:
            self.face_down = True
            self.source = self.card.source



class Deck:
    def __init__(self, card_back):
        self.cards = []
        for suit in range(4):
            for rank in range(1,14):
                self.cards.append(Card(card_back, suit, rank))

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



class GameEvents(EventDispatcher):
    pause_game = BooleanProperty(False)
    round_over = NumericProperty(1)
    game_over  = BooleanProperty(False)
    score = NumericProperty(0)



class Player(GameEvents):
    def __init__(self, name, xpos=3, ypos=-1, npc=False):
        self.cards = []
        self.score = 0
        self.name = name
        self.xpos, self.ypos = xpos, ypos
        self.npc = npc
        
    def add_card(self, card):
        card_image = CardImage(xpos=self.xpos, ypos=self.ypos, card=card)
        self.cards.append(card_image)

    def pop_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()

    def is_empty(self):
        return (len(self.cards) == 0)

    
    
class Game(GameEvents):
    def __init__(self, player_names, victory_score, card_back):
        self.players = self.set_players(player_names)
        self.victory_score = victory_score
        self.card_back = card_back
        self.turn = self.cycle_players()

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
        self.deck = Deck(self.card_back)
        self.deck.shuffle()
        self.deck.deal(self.players)
        self.starter = self.deck.pop_card()

        self.cards = {}
        self.current_player = self.turn.next()

    def pause_game_callback(self, *args):
        if self.pause_game:
            self.pause_game = False
        else:
            self.pause_game = True

    def is_round_over(self):
        return len(self.cards) == 25

    def round_over_callback(self, *args):
        self.round_over += 1

    def is_game_over(self):
        if len(self.players) > 1:
            for player in self.players:
                if player.score >= self.victory_score:
                    return True
        return False

    def game_over_callback(self, *args):
        self.game_over = True

    def computer_move(self):
        card = self.current_player.pop_card()
        cards_ = self.cards
        move_scores = {}
        for i in range(1,6):
            for j in range(1,6):
                if (i,j) not in cards_.keys():
                    cards_[(i,j)] = card
                    self.calculate_scores(cards_.keys())
                    move_scores[(i,j)] = self.row_score - self.col_score
                    del cards_[(i,j)]
        move_scores = sorted(move_scores.items(),
                             key=lambda x: x[1], reverse=True)
        high_scores = [((i,j),c) for ((i,j),c) in move_scores
                       if c == move_scores[0][1]]
        coord = choice(high_scores)[0]
        return (coord, card)
        
    def calculate_scores(self, coords=None):
        if coords==None:
            coords=self.cards.keys()

        self.col_score, self.row_score = 0, 0
            
        col_coords=[[(x,y) for (x,y) in coords if x==col] for col in range(1,6)]
        col_coords=[coord for coord in col_coords if coord!=[]]
        col_cards =[[self.cards[coord] for coord in col] for col in col_coords]
        self.col_score = self.score_cards(col_cards)

        row_coords=[[(x,y) for (x,y) in coords if y==row] for row in range(1,6)]
        row_coords=[coord for coord in row_coords if coord!=[]]
        row_cards =[[self.cards[coord] for coord in row] for row in row_coords]
        self.row_score = self.score_cards(row_cards)

    def score_round(self):     
        if len(self.players) > 1:
            self.players[0].score += self.col_score
            self.players[1].score += self.row_score
        else:
            self.players[0].score = self.col_score + self.row_score
            
            template  = "You scored {}. You are {}."
            name_dict = ((0,40,'a worm'), (40,50,'a crab'), (50,60,'a lizard'),
                         (60,70,'a puppy'), (70,80,'a beaver'),
                         (80,90,'a dikdik'), (90,100,'a water bear'),
                         (100,110,'a magic mushroom'),(110,120,'a tiger'),
                         (120,130,'an elephant'),(130,200,'a dragon'))

            for (low, high, name) in name_dict:
                if low <= self.players[0].score < high:
                    self.message = str(template.format(self.players[0].score,
                                                       name))

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
            score += self.score_flush(suits, hand)
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

    def score_flush(self, suits, hand):
        if len(set(suits)) == 1:
            # Flushes are scored as 5 at end of round
            # However they are rated less by computer during the game
            score = len(hand)
        else:
            score = 0
        return score
