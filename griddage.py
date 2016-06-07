import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.properties import \
     NumericProperty, ReferenceListProperty, StringProperty, ObjectProperty

from card import Card, Deck, GridEntry, CardImage, Player, Game
import time



class GridBlank(Image, GridEntry):
    source = StringProperty('cards/blank.png')

class GridButton(Button, GridEntry):
    pass

class GridLabel(Label, GridEntry):
    pass

class Animate(Animation, GridEntry):
    pass



class Board(FloatLayout):
    rows = NumericProperty(1)
    columns = NumericProperty(1)
    shape = ReferenceListProperty(rows, columns)
    game = ObjectProperty()

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)

        with self.canvas.before:
            Color(0, 0.6, 0)
            self.base_rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self.update_background, pos=self.update_background)

        if len(self.game.players) > 1:
            with self.canvas.before:
                Color(1, 1, 0, 1)
                self.rects = [Rectangle(size=self.size, pos=self.pos), \
                              Rectangle(size=self.size, pos=self.pos), \
                              Rectangle(size=self.size, pos=self.pos), \
                              Rectangle(size=self.size, pos=self.pos)]

        self.game.play_round()
        self.make_board()

    def update_background(self, *args):
        for button in self.buttons.values():
            button.disabled = False
            
        self.base_rect.size = self.size
        self.base_rect.pos  = self.pos

        if len(self.game.players) == 1:
            return False
        
        SIZE_FACTOR = .02
        shape_hint = (self.width / self.columns, self.height / self.rows)

        if len(self.game.players) == 2:
            if self.game.current_player == self.game.players[0]:
                pos_iter  = iter((x+0.5, 0.5) for x in range(1,5))
                size_iter = iter((1, (6-(1-SIZE_FACTOR))/SIZE_FACTOR) \
                                      for i in range(4))
            else:
                pos_iter  = iter((0.5, y+0.5) for y in range(1,5))
                size_iter = iter(((6-(1-SIZE_FACTOR))/SIZE_FACTOR, 1) \
                                      for i in range(4))
        elif len(self.game.players) == 4:
            if self.game.current_player == self.game.players[0] or \
               self.game.current_player == self.game.players[2]:
                pos_iter  = iter((x+0.5, 0.5) for x in range(1,5))
                size_iter = iter((1, (6-(1-SIZE_FACTOR))/SIZE_FACTOR) \
                                      for i in range(4))
            else:
                pos_iter  = iter((0.5, y+0.5) for y in range(1,5))
                size_iter = iter(((6-(1-SIZE_FACTOR))/SIZE_FACTOR, 1) \
                                      for i in range(4))
            
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
        self.buttons = dict()
        for i in range(1,6):
            for j in range(1,6):
                self.add_widget(GridBlank(xpos=i, ypos=j,
                                          source='cards/blank.png'))
                button = GridButton(xpos=i, ypos=j, opacity=0)
                self.buttons[(i,j)] = button

        for button in self.buttons.values():
            if button.xpos == 3 and button.ypos == 3:
                starter = CardImage(xpos=3, ypos=3, \
                                    card=self.game.starter, face_down=False)    
                self.add_widget(starter)
                self.game.cards[(3,3)] = starter
            else:
                self.add_widget(button)
                button.bind(on_press=self.place_card)

        if len(self.game.players) == 1:
            self.solo_label = GridLabel(text='[b]0[/b]',
                                        markup=True, font_size=20,
                                        xpos=3, ypos=0)
            self.add_widget(self.solo_label)
            
        elif len(self.game.players) == 2:
            self.col_label = GridLabel(text='[b]%d[/b]' % \
                                       self.game.players[0].score,
                                       markup=True, font_size=20,
                                       xpos=2, ypos=0)
            self.add_widget(self.col_label)
            
            self.row_label = GridLabel(text='[b]%d[/b]' % \
                                       self.game.players[1].score,
                                       markup=True, font_size=20,
                                       xpos=4, ypos=0)
            self.add_widget(self.row_label)
            
        elif len(self.game.players) == 4:
            self.col_label = GridLabel(text='[b]%d[/b]' % \
                                       self.game.players[0].score,
                                       markup=True, font_size=20,
                                       xpos=1.5, ypos=0)
            self.add_widget(self.col_label)
            
            self.row_label = GridLabel(text='[b]%d[/b]' % \
                                       self.game.players[1].score,
                                       markup=True, font_size=20,
                                       xpos=4.5, ypos=0)
            self.add_widget(self.row_label)
            
        for player in self.game.players:
            self.add_widget(GridLabel(text='[b]'+player.name+'[/b]',
                                      markup=True, font_size=20,
                                      xpos=player.xpos, ypos=-.3))
            self.add_widget(GridBlank(xpos=player.xpos, ypos=player.ypos,
                                      source='cards/blank.png'))
            for card in player.cards:
                self.add_widget(card)
                
        self.game.current_player.cards[-1].flip()

        if len(self.game.players) == 2 and self.game.players[1].name == "Bot1" \
        and self.game.current_player.name == "Bot1":
            self.computer_turn()

    def update_score(self, *args):
        if len(self.game.players) == 1:
            self.solo_label.text = '[b]%s[/b]' % self.game.message
        else:
            self.col_label.text  = '[b]%d[/b]' % self.game.players[0].score
            self.row_label.text  = '[b]%d[/b]' % self.game.players[1].score

    def animate(self, instance, coords):
        for button in self.buttons.values():
            button.disabled = True
        anim  = Animate(xpos=coords[0], y=-5, duration=0.5)
        anim &= Animate(ypos=coords[1], x=-5, duration=0.5)
        anim.bind(on_complete=self.update_background)
        if self.game.is_round_over():
            anim.bind(on_complete=self.end_round)
        elif len(self.game.players)==2 and self.game.players[1].name=="Bot1" \
        and self.game.current_player.name != "Bot1":
            anim.bind(on_complete=self.computer_turn)
        anim.start(instance)
        
    def bring_to_front(self, card):
        self.remove_widget(card)
        self.add_widget(card)

    def place_card(self, button):
        coords = (button.xpos, button.ypos)
        self.remove_widget(button)
        del self.buttons[coords]
        
        self.game.cards[coords] = self.game.current_player.pop_card()
        self.bring_to_front(self.game.cards[coords])
        self.animate(self.game.cards[coords], coords)

        self.game.current_player = self.game.turn.next()
        
        if not self.game.current_player.is_empty():
            self.game.current_player.cards[-1].flip()

    def computer_turn(self, *args):
        if self.game.current_player == self.game.players[1]:
            coords, card = self.game.computer_move()

            self.remove_widget(self.buttons[coords])
            del self.buttons[coords]
            
            self.game.cards[coords] = card
            self.bring_to_front(self.game.cards[coords])
            self.animate(self.game.cards[coords], coords)

            self.game.current_player = self.game.turn.next()
    
            if not self.game.current_player.is_empty():
                self.game.current_player.cards[-1].flip()

    def end_round(self, *args):
        self.game.calculate_scores()
        self.game.score_round()
        self.update_score()
        
        if self.game.is_game_over():
            menu_button = GridButton(xpos=3, ypos=-1, text='Back to menu')
            self.add_widget(menu_button)
            menu_button.bind(on_release=self.game.game_over_callback)
        else:
            next_button = GridButton(xpos=3, ypos=-1, text='Next round')
            self.add_widget(next_button)
            next_button.bind(on_release=self.game.round_over_callback)

            
            
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.bind(on_pre_enter=self.build)

    def build(self, *args):
        if   self.manager.mode == 'Solitaire Mode':
            self.game = Game(['Anna'])
        elif self.manager.mode == '2 Player Mode':
            self.game = Game(['Anna', 'Jan'])
        elif self.manager.mode == 'Challenge Mode':
            self.game = Game(['Anna', 'Bot1'])
        elif self.manager.mode == '4 Player Mode':
            self.game = Game(['Anna', 'Jan', 'Garrett', 'Johno'])

        self.board = Board(rows=7, columns=5, game=self.game)
        self.game.bind(round_over=self.new_round)
        self.game.bind(game_over =self.goto_menu)

        self.add_widget(self.board)
    
    def new_round(self, *args):
        self.remove_widget(self.board)
        self.board = Board(rows=7, columns=5, game=self.game)
        self.add_widget(self.board)

    def goto_menu(self, *args):
        self.remove_widget(self.board)
        self.manager.current = 'menu_screen'



class SettingsLyt(StackLayout):
    def __init__(self, **kwargs):
        super(SettingsLyt, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(0, 0.6, 0)
            self.base_rect = Rectangle(size=self.size,
                                            pos=self.pos)
            self.bind(size=self.update_background,
                      pos=self.update_background)

        self.orientation,self.spacing,self.padding = ('lr-tb', [20,20], [20,20])

    def update_background(self, *args):
        self.base_rect.size = self.size
        self.base_rect.pos  = self.pos
        


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        self.settings = SettingsLyt()
        self.add_widget(self.settings)
        self.make_widgets()

    def make_widgets(self):
        button_names = ('Edit Names', self.popup_names), \
                       ('Victory Score', self.popup_score), \
                       ('Back to Menu', self.back_to_menu)

        for name in button_names:
            button = Button(text=name[0], font_size=50, size_hint=(1,None))
            button.bind(on_press=name[1])
            self.settings.add_widget(button)

    def popup_names(self, button):
        popup_layout = StackLayout(orientation='tb-lr',
                                   spacing=[20,20],
                                   padding=[20,20])
        
        for num in range(1,5):
            label_text = 'Player ' + str(num)
            label = Label(text=label_text, size_hint=(0.5,None), height=30)
            popup_layout.add_widget(label)
            
        names = ['Anna', 'Jan', 'Garret', 'Johno']
        for name in names:
            name_input = TextInput(text=name, multiline=False,
                                   size_hint=(0.5,None), height=30)
            popup_layout.add_widget(name_input)
        
        popup = Popup(title='Edit Names',
                      content=popup_layout, 
                      size_hint=(0.8,None), height=290)
        popup.open()

    def popup_score(self, button):
        popup_layout = StackLayout(orientation='tb-lr',
                                   spacing=[20,20],
                                   padding=[20,20])
        
        label = Label(text='Victory Score', size_hint=(0.5,None), height=30)
        popup_layout.add_widget(label)
            
        score_input = TextInput(text=str(61), multiline=False,
                               size_hint=(0.5,None), height=30)
        popup_layout.add_widget(score_input)
        
        popup = Popup(title='Edit Names',
                      content=popup_layout, 
                      size_hint=(0.8,None), height=150)
        popup.open()
        
    def back_to_menu(self, button):
        self.manager.current = 'menu_screen'



class Menu(BoxLayout):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(0, 0.6, 0)
            self.base_rect = Rectangle(size=self.size,
                                            pos=self.pos)
            self.bind(size=self.update_background,
                      pos=self.update_background)

        self.orientation, self.spacing, self.padding = ('vertical', 20, [0, 20])

    def update_background(self, *args):
        self.base_rect.size = self.size
        self.base_rect.pos  = self.pos
        


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        self.menu = Menu()
        self.add_widget(self.menu)
        self.make_buttons()

    def make_buttons(self):
        button_names = ['Solitaire Mode', '2 Player Mode', '4 Player Mode',
                        'Challenge Mode', 'Settings']

        for name in button_names:
            button = Button(text=name, font_size=50, 
                            pos_hint={'center_x':.5}, size_hint=(0.9,0.9))
            button.bind(on_press=self.change)
            self.menu.add_widget(button)
        
    def change(self, button):
        self.manager.mode = button.text
        if button.text == 'Settings':
            self.manager.current = 'settings_screen'
        else:
            self.manager.current = 'game_screen'


        

class GriddageApp(App):
    def build(self):
        self.manager = ScreenManager()

        self.manager.mode = 'Initial'

        self.menu_screen = MenuScreen(name='menu_screen')
        self.manager.add_widget(self.menu_screen)

        self.game_screen = GameScreen(name='game_screen')
        self.manager.add_widget(self.game_screen)

        self.settings_screen = SettingsScreen(name='settings_screen')
        self.manager.add_widget(self.settings_screen)
        
        return self.manager

    

if __name__ == "__main__":
    GriddageApp().run()
