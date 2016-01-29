import kivy
kivy.require('1.9.1')

from kivy.app import App

from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.image import Image

from kivy.properties import \
     NumericProperty, ReferenceListProperty, StringProperty, ObjectProperty

from card import Card, Deck, GridEntry, CardImage, Player, Game

class GridBlank(Image, GridEntry):
    source = StringProperty('cards/blank.png')

class GridButton(Button, GridEntry):
    pass

class Animate(Animation, GridEntry):
    pass

class Board(FloatLayout):
    rows = NumericProperty(1)
    columns = NumericProperty(1)
    shape = ReferenceListProperty(rows, columns)

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0, 0.6, 0)
            self.base_rect = Rectangle(size=self.size, pos=self.pos)

        with self.canvas.before:
            Color(1, 0, 0, 1)
            self.rects = [Rectangle(size=self.size, pos=self.pos), \
                          Rectangle(size=self.size, pos=self.pos), \
                          Rectangle(size=self.size, pos=self.pos), \
                          Rectangle(size=self.size, pos=self.pos), \
                          Rectangle(size=self.size, pos=self.pos)]
            self.bind(pos=self.update_background, size=self.update_background)

##        self.game = Game(['Anna'])
        self.game = Game(['Anna', 'Jan'])
##        self.game = Game(['Anna', 'Jan', 'Garrett', 'Johno'])
        
        self.make_board()

    def update_background(self, *args):
        self.base_rect.size = self.size
        self.base_rect.pos  = self.pos
        
        SIZE_FACTOR = .2
        shape_hint = (self.width / self.columns, self.height / self.rows)
        if self.game.current_player == self.game.players[0]:
            pos_iter = iter((x, 1) for x in range(1,6))
            size_iter = iter((1, (5-(1-SIZE_FACTOR))/SIZE_FACTOR) \
                             for i in range(5))
        else:
            pos_iter = iter((1, y) for y in range(1,6))
            size_iter = iter(((5-(1-SIZE_FACTOR))/SIZE_FACTOR, 1) \
                             for i in range(5))
            
        for rect in self.rects:
            pos  = pos_iter.next()
            xpos, ypos = pos[0], pos[1]
            size = size_iter.next()
            w, l = size[0], size[1]
            
            rect.size = [shape_hint[0] * w * SIZE_FACTOR, \
                         shape_hint[1] * l * SIZE_FACTOR]
            rect.pos  = [shape_hint[0] * (xpos - 1. + (1-SIZE_FACTOR)/2), \
                         shape_hint[1] * (ypos + 1. + (1-SIZE_FACTOR)/2) ]

    def do_layout(self, *args):
        SIZE_FACTOR = 0.9
        shape_hint = (1. / self.columns, 1. / self.rows)
        for child in self.children:
            child.size_hint = (SIZE_FACTOR / self.columns, \
                               SIZE_FACTOR / self.rows)
            if not hasattr(child, 'xpos'):
                child.xpos = 1
            if not hasattr(child, 'ypos'):
                child.ypos = 1

            child.pos_hint = \
                {'x': shape_hint[0] * (child.xpos - 1. + (1-SIZE_FACTOR)/2), \
                 'y': shape_hint[1] * (child.ypos + 1. + (1-SIZE_FACTOR)/2)}
                        
            super(Board, self).do_layout(*args)
        
    def make_board(self):
        blanks = []
        for i in range(1,6):
            for j in range(1,6):
                blank = GridBlank(xpos=i, ypos=j, source='cards/blank.png')
                blanks.append(blank)
                
        for blank in blanks:
            self.add_widget(blank)
            
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

        for player in self.game.players:
            for card in player.cards:
                self.add_widget(card)            
        self.game.current_player.cards[-1].flip()

    def animate(self, instance, coords):
        anim  = Animate(xpos=coords[0], y=-5, duration=0.5)
        anim &= Animate(ypos=coords[1], x=-5, duration=0.5)
        anim.bind(on_complete=self.update_background)
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
