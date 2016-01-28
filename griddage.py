import kivy
kivy.require('1.9.1')

from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.event import EventDispatcher
from kivy.properties import \
     NumericProperty, ReferenceListProperty, StringProperty, ObjectProperty

from itertools import cycle, combinations
from card import Card, Deck



class GridEntry(EventDispatcher):
    xpos = NumericProperty(0)
    ypos = NumericProperty(0)

class CardSource(EventDispatcher):
    source = StringProperty()

class GridButton(Button, GridEntry):
    pass

class Animate(Animation, GridEntry):
    pass

class CardImage(Image, GridEntry, CardSource, Card):
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

class HandWidget:
    def __init__(self, name, xpos=3, ypos=-1):
        self.cards = []
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

class Game:
    def __init__(self, players):
        self.deck = Deck()
        self.deck.shuffle()
        self.hands = self.make_hands(players)
        self.deck.deal(self.hands)
        self.starter = self.deck.pop_card()

        self.cards = {}

        self.turn = self.cycler()
        self.current_player = self.turn.next()

    def make_hands(self, players):
        if len(players) == 1:
            return [HandWidget(players[0], xpos=3, ypos=-1)]
        if len(players) == 2:
            return [HandWidget(players[0], xpos=2, ypos=-1), \
                    HandWidget(players[1], xpos=4, ypos=-1)]
        if len(players) == 4:
            return [HandWidget(players[0], xpos=2, ypos=-1), \
                    HandWidget(players[1], xpos=4, ypos=-1), \
                    HandWidget(players[2], xpos=1, ypos=-1), \
                    HandWidget(players[3], xpos=5, ypos=-1)]

    def cycler(self):
        for player in cycle(self.hands):
            yield player

    def score_match(self):
        coords = self.cards.keys()
        
        v_coords=[[(x,y) for (x,y) in coords if x==col] for col in range(1,6)]
        v_cards =[[self.cards[coord] for coord in col] for col in v_coords]

        v_score = 0
        
        for col in v_cards:
            suits = [card.suit for card in col]
            ranks = [card.rank for card in col]
            values= [card.rank if card.rank <= 10 else 10 for card in col]
            
            score  = 0
            
            score += self.score_fifteens(values)
            print 'Fifteen score:', self.score_fifteens(values)
            
            score += self.score_pairs(ranks)
            print 'Pair score:', self.score_pairs(ranks)
            
            score += self.score_runs(ranks)
            print 'Run score:', self.score_runs(ranks)
            
            score += self.score_flush(suits)
            print 'Flush score:', self.score_flush(suits)
            
            print 'Line score:', score, '\n'
            v_score += score
            
        print 'Total score for player 1:', v_score
            


        h_coords=[[(x,y) for (x,y) in coords if y==row] for row in range(1,6)]
        h_cards =[[self.cards[coord] for coord in row] for row in h_coords]

        h_score = 0
        
        for row in h_cards:
            suits = [card.suit for card in row]
            ranks = [card.rank for card in row]
            values= [card.rank if card.rank <= 10 else 10 for card in row]
            
            score  = 0
            
            score += self.score_fifteens(values)
            print 'Fifteen score:', self.score_fifteens(values)
            
            score += self.score_pairs(ranks)
            print 'Pair score:', self.score_pairs(ranks)
            
            score += self.score_runs(ranks)
            print 'Run score:', self.score_runs(ranks)
            
            score += self.score_flush(suits)
            print 'Flush score:', self.score_flush(suits)
            
            print 'Line score:', score, '\n'
            h_score += score
            
        print 'Total score for player 2:', h_score

        if v_score > h_score:
            print '\n', 'Player 1 wins!'
        elif h_score > v_score:
            print '\n', 'Player 2 wins!'
        else:
            print 'Tie Game!'

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
        return run_length

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

    def is_game_over(self):
        return len(self.cards) == 25

        

class Board(FloatLayout):

    rows = NumericProperty(1)
    columns = NumericProperty(1)
    shape = ReferenceListProperty(rows, columns)

                 
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0, 0.9, 0, 0.3)
            self.rects = [Rectangle(size=self.size, pos=self.pos), \
                          Rectangle(size=self.size, pos=self.pos), \
                          Rectangle(size=self.size, pos=self.pos), \
                          Rectangle(size=self.size, pos=self.pos), \
                          Rectangle(size=self.size, pos=self.pos)]
            self.bind(pos=self.update_rect, size=self.update_rect)

##        self.game = Game(['Anna'])
        self.game = Game(['Anna', 'Jan'])
##        self.game = Game(['Anna', 'Jan', 'Garrett', 'Johno'])
        
        self.make_board()

    def update_rect(self, *args):
        UNIT_WIDTH  = self.width / self.columns
        UNIT_HEIGHT = self.height / self.rows
        v_pos = iter(range(4))
        if self.game.current_player == self.game.hands[0]:
            h_pos = iter((0,1,2,3,4))
            for rect in self.rects:
                new_pos = h_pos.next()
                rect.pos  = [(new_pos * UNIT_WIDTH), \
                             (self.height - 5 * UNIT_HEIGHT)]
                rect.size = [(0.9 * UNIT_WIDTH), (5 * UNIT_HEIGHT)]
                
        if self.game.current_player == self.game.hands[1]:
            v_pos = iter((1,2,3,4,5))
            for rect in self.rects:
                new_pos = v_pos.next()
                rect.pos  = [0, (self.height - new_pos * UNIT_HEIGHT)]
                rect.size = [self.width, (0.9 * UNIT_HEIGHT)]                     

    def do_layout(self, *args):
        shape_hint = (1. / self.columns, 1. / self.rows)
        for child in self.children:
            child.size_hint = (.95 / self.columns, .95 / self.rows)
            if not hasattr(child, 'xpos'):
                child.xpos = 0
            if not hasattr(child, 'ypos'):
                child.ypos = 0

            child.pos_hint = {'x': shape_hint[0] * (child.xpos - 1.),
                              'y': shape_hint[1] * (child.ypos + 1.)}
            
            super(Board, self).do_layout(*args)
        
    def make_board(self):
        buttons = []
        for i in range(1,6):
            for j in range(1,6):
                button = GridButton(xpos=i, ypos=j, opacity=0)
                buttons.append(button)

        for button in buttons:
            if button.xpos == 3 and button.ypos == 3:
                starter = CardImage(xpos=3, ypos=3, \
                                    card=self.game.starter, face_down=False)    
                self.add_widget(starter)
                self.game.cards[(3,3)] = starter
            else:
                self.add_widget(button)
                button.bind(on_release=self.place_card)

        for hand in self.game.hands:
            for card in hand.cards:
                self.add_widget(card)            
        self.game.current_player.cards[-1].flip()

    def animate(self, instance, coords):
        anim  = Animate(xpos=coords[0], y=-5, duration=0.75)
        anim &= Animate(ypos=coords[1], x=-5, duration=0.75)
        anim.start(instance)

    def bring_to_front(self, card):
        self.remove_widget(card)
        self.add_widget(card)

    def place_card(self, button):
        coords = (button.xpos, button.ypos)

        self.game.cards[coords] = self.game.current_player.pop_card()
        self.bring_to_front(self.game.cards[coords])
        self.animate(self.game.cards[coords], coords)
        self.remove_widget(button)
            
        self.game.current_player = self.game.turn.next()
        self.update_rect()
        
        if not self.game.current_player.is_empty():
            self.game.current_player.cards[-1].flip()

        if self.game.is_game_over():
            self.game.score_match()
        


class GriddageApp(App):
    def build(self):
        board = Board(rows=7, columns=5)
        return board

if __name__ == "__main__":
    GriddageApp().run()
