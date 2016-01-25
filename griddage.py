import kivy
kivy.require('1.9.1')

from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.event import EventDispatcher
from kivy.properties import \
     NumericProperty, ReferenceListProperty, StringProperty

from card import Card, Deck



class GridEntry(EventDispatcher):
    xpos = NumericProperty(0)
    ypos = NumericProperty(0)

class GreenButton(Button, GridEntry):
    pass

class CardSource(EventDispatcher):
    source = StringProperty()

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
        if len(players) == 2:
            self.hands = [HandWidget(players[0], xpos=2, ypos=-1), \
                          HandWidget(players[1], xpos=4, ypos=-1)]
        self.deck.deal(self.hands)
        self.starter = self.deck.pop_card()
         
class Animate(Animation, GridEntry):
    pass



class Board(FloatLayout):

    rows = NumericProperty(1)
    columns = NumericProperty(1)
    shape = ReferenceListProperty(rows, columns)

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)

        self.game = Game(['Anna', 'Jan'])
        
        self.cards = {}
        self.current_player = 1

        self.make_board()

    def do_layout(self, *args):
        shape_hint = (1. / self.columns, 1. / self.rows)
        for child in self.children:
            child.size_hint = (0.95 / self.columns, 0.95 / self.rows)
            if not hasattr(child, 'xpos'):
                child.xpos = 1
            if not hasattr(child, 'ypos'):
                child.ypos = 1

            child.pos_hint = {'x': shape_hint[0] * (child.xpos - 1.),
                              'y': shape_hint[1] * (child.ypos + 1.)}
            
            super(Board, self).do_layout(*args)
        
    def make_board(self):
        buttons = []
        for i in range(1,6):
            for j in range(1,6):
                button = GreenButton(xpos=i, ypos=j)
                buttons.append(button)

        for button in buttons:
            if button.xpos == 3 and button.ypos == 3:
                starter = CardImage(xpos=3, ypos=3, \
                                    card=self.game.starter, face_down=False)
                self.add_widget(starter)
                self.cards[(3,3)] = starter
            else:
                self.add_widget(button)
                button.bind(on_release=self.place_card)

        if len(self.game.hands) == 2:
            self.p1 = self.game.hands[0]
            for card in self.p1.cards:
                self.add_widget(card)
            self.p1.cards[-1].flip()

            self.p2 = self.game.hands[1]
            for card in self.p2.cards:
                self.add_widget(card)

    def animate(self, instance, coords):
        anim  = Animate(xpos=coords[0], y=0, duration=0.75)
        anim &= Animate(ypos=coords[1], x=0, duration=0.75)
        anim.start(instance)
        
    def place_card(self, button):
        coords = (button.xpos, button.ypos)
        
        if self.current_player == 1:
            self.cards[coords] = self.p1.pop_card()
            self.animate(self.cards[coords], coords)
            self.remove_widget(button)
            
            if not self.p2.is_empty():
                self.p2.cards[-1].flip()
                
            self.current_player = 2
            return self.cards

        if self.current_player == 2:
            self.cards[coords] = self.p2.pop_card()
            self.animate(self.cards[coords], coords)
            self.remove_widget(button)
            
            if not self.p1.is_empty():
                self.p1.cards[-1].flip()
                
            self.current_player = 1
            return self.cards
        


class GriddageApp(App):
    def build(self):
        board = Board(rows=7, columns=5)
        return board

if __name__ == "__main__":
    GriddageApp().run()                    
