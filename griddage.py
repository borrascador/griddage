
'''A kivy layout with a set number of rows and columns, whose children
are positioned according to their `row` and `col` properties if they
exist. If they do not have these properties, they default to the
zeroth row and column.
SparseGridLayout is *not* a subclass of GridLayout, but is instead a
FloatLayout subclass to avoid filling a GridLayout with empty widgets
(and having to manage all their positions). If your grid is densely
populated, or if you want certain finer control over widget sizing,
you may find a GridLayout more convenient.
'''

from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.event import EventDispatcher

from kivy.properties import \
     NumericProperty, ReferenceListProperty, StringProperty

from kivy.animation import Animation

from card import Card, Hand, Game



class GridEntry(EventDispatcher):
    xpos = NumericProperty(0)
    ypos = NumericProperty(0)

class GreenButton(Button, GridEntry):
    pass

class CardImage(Image, GridEntry, Card):
    pass
##    def __str__(self):
##        return self.path

class PlayerHand(Image, GridEntry):
    source = StringProperty('cards/back1.png')

class Anim(Animation, GridEntry):
    pass

game = Game()

class SparseGridLayout(FloatLayout):

    rows = NumericProperty(1)
    columns = NumericProperty(1)
    shape = ReferenceListProperty(rows, columns)

    def __init__(self, **kwargs):
        super(SparseGridLayout, self).__init__(**kwargs)

        self.p1 = PlayerHand(xpos=2, ypos=-1, source=game.p1.pop_card().path)
        self.p2 = PlayerHand(xpos=4, ypos=-1)

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
            

            super(SparseGridLayout, self).do_layout(*args)

    def reposition(self, child, **kwargs):   
        for prop in ('x', 'y', 'size'):
            value = kwargs.pop(prop, None)
            if not value:
                continue
            Animation(d=.5, **{prop: value}).start(child)

        
    def make_board(self):
        buttons = []
        for i in range(1,6):
            for j in range(1,6):
                button = GreenButton(xpos=i, ypos=j)
                buttons.append(button)

        for button in buttons:
            if button.xpos == 3 and button.ypos == 3:
                starter = CardImage(xpos=3, ypos=3, source=game.starter.path)
                self.add_widget(starter)
                self.cards[(3,3)] = starter
            else:
                self.add_widget(button)
                button.bind(on_release=self.place_card)

        self.add_widget(self.p1)
        self.add_widget(self.p2)

    def animate(self, instance, coords):
        anim  = Anim(xpos=coords[0], y=0, duration=0.75)
        anim &= Anim(ypos=coords[1], x=0, duration=0.75)
        anim.start(instance)

    def place_card(self, button):
        next_card = self.choose_card()
        
        coords = (button.xpos, button.ypos)
        if self.current_player == 1:
            self.cards[coords] = CardImage(xpos=4, ypos=-1,
                                           source=next_card)
        if self.current_player == 2:
            self.cards[coords] = CardImage(xpos=2, ypos=-1,
                                           source=next_card)

        self.add_widget(self.cards[coords])
        self.animate(self.cards[coords], coords)
        self.remove_widget(button)

        if len(self.cards) == 25:
            print [str(card) for card in self.cards.values()]

        return self.cards

    def choose_card(self):
        if self.current_player == 1:
            next_card = self.p1.source
            if len(game.p1.cards) == 0:
                self.remove_widget(self.p1)
                self.p2.source = game.p2.pop_card().path
            else:
                self.p1.source = 'cards/back1.png'
                self.p2.source = game.p2.pop_card().path   
            self.current_player = 2
            return next_card
        
        if self.current_player == 2:
            next_card = self.p2.source
            if len(game.p2.cards) == 0:
                self.remove_widget(self.p2)
            else:
                self.p1.source = game.p1.pop_card().path
                self.p2.source = 'cards/back1.png'
            self.current_player = 1
            return next_card
    
    def make_coords(self, button):
        return '({}, {})'.format(button.xpos, button.ypos)
        
class GriddageGame():
    def __init__(self, players=2):
        print players



class GriddageApp(App):
    def build(self):
        board = SparseGridLayout(rows=7, columns=5)
        return board

if __name__ == "__main__":
    GriddageApp().run()                    
