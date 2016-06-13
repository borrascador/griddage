import kivy
kivy.require('1.9.1')

from kivy.app import App

from kivy.animation import Animation
from kivy.event import EventDispatcher
from kivy.graphics import Color, Rectangle
from kivy.properties import \
     NumericProperty, ReferenceListProperty, StringProperty, ObjectProperty, \
     ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import DragBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from card import Card, Deck, GridEntry, CardImage, Player, Game



class Animation(Animation, GridEntry):
    pass

class Label(Label):
    font_name = 'cards/Chunkfive.otf'
    
class Button(Button):
    background_normal = ''
    background_color = [0.2, 0.65, 0.2, 0.5]
    font_name = 'cards/Chunkfive.otf'
    
class GridBlank(ButtonBehavior, Image, GridEntry):
    source = StringProperty('cards/felt.png')

class GridButton(Button, GridEntry):
    background_normal = ''
    background_color = [0.1, 0.8, 0.1, 0.5]

class GridLabel(Label, GridEntry):
    pass

class CardButton(ButtonBehavior, Image):
    pass



class Board(FloatLayout):
    rows = NumericProperty(1)
    columns = NumericProperty(1)
    shape = ReferenceListProperty(rows, columns)
    game = ObjectProperty()

    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)

        self.texture = Image(source='cards/felt2.png').texture
        self.texture.wrap = 'repeat'
        self.texture.uvsize = (10,10)
        with self.canvas.before:
            Color(0, 0, 0)
            self.rect = Rectangle(pos=(0,0), size=(2000,2000))

        with self.canvas.before:
            if len(self.game.players) > 1:
                Color(1, 1, 0, 1)
                self.rects = [Rectangle(size=self.size, pos=self.pos), \
                              Rectangle(size=self.size, pos=self.pos), \
                              Rectangle(size=self.size, pos=self.pos), \
                              Rectangle(size=self.size, pos=self.pos)]
                self.bind(size=self.update_background,
                          pos=self.update_background)

        self.game.play_round()
        self.make_board()

    def enter_background(self, *args):
        with self.canvas.before:
            Color(0, 2, 0)
            self.rect = Rectangle(pos=(0,0), size=(2000,2000),
                                  texture=self.texture)

    def update_background(self, *args):
        if len(self.game.players) == 1:
            return False
        
        SIZE_FACTOR = .02
        shape_hint = (self.width / self.columns, self.height / self.rows)

        if len(self.game.players) == 2:
            if self.game.current_player == self.game.players[0] or \
               self.game.players[1].name == 'Bot1':
                pos_iter  = iter((x+0.5, 0.5) for x in range(1,5))
                size_iter = iter((SIZE_FACTOR, 5) for i in range(4))
            else:
                pos_iter  = iter((0.5, y+0.5) for y in range(1,5))
                size_iter = iter((5, SIZE_FACTOR) for i in range(4))
                
        elif len(self.game.players) == 4:
            if self.game.current_player == self.game.players[0] or \
               self.game.current_player == self.game.players[2]:
                pos_iter  = iter((x+0.5, 0.5) for x in range(1,5))
                size_iter = iter((SIZE_FACTOR, 5) for i in range(4))
            else:
                pos_iter  = iter((0.5, y+0.5) for y in range(1,5))
                size_iter = iter((5, SIZE_FACTOR) for i in range(4))
            
        for rect in self.rects:
            pos  = pos_iter.next()
            xpos, ypos = pos[0], pos[1]
            size = size_iter.next()
            width, length = size[0], size[1]
            
            rect.size = [shape_hint[0] * width, \
                         shape_hint[1] * length]
            rect.pos  = [shape_hint[0] * (xpos - 0.5), \
                         shape_hint[1] * (ypos + 1.5) ]

    def do_layout(self, *args):
        SIZE_FACTOR = 0.95
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
                if (i,j) == (3,3):
                    starter = CardImage(xpos=3, ypos=3, \
                                        card=self.game.starter, face_down=False)    
                    self.add_widget(starter)
                    self.game.cards[(3,3)] = starter
                else:
                    button = GridBlank(xpos=i, ypos=j, opacity=0.4,
                                       source='cards/blank.png')
                    button.bind(on_press=self.place_card)
                    self.buttons[(i,j)] = button
                    self.add_widget(button)
        
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
                                      source='cards/blank.png', opacity = 0.4))
            for card in player.cards:
                self.add_widget(card)

        pause_button = GridButton(text='Pause', font_size=20)
        quit_button = GridButton(text='Quit', font_size=20)
        
        if len(self.game.players) == 1:
            pause_button.xpos, pause_button.ypos = 1, -1
            quit_button.xpos, quit_button.ypos = 5, -1
        elif len(self.game.players) > 1:
            pause_button.xpos, pause_button.ypos = 3, 0
            quit_button.xpos, quit_button.ypos = 3, -1
            
        pause_button.bind(on_press=self.game.pause_game_callback)
        quit_button.bind(on_press=self.game.game_over_callback)

        self.add_widget(pause_button)
        self.add_widget(quit_button)
        
        self.game.current_player.cards[-1].flip()

        if self.game.current_player.name == 'Bot1':
            self.computer_turn()

    def update_score(self, *args):
        if len(self.game.players) == 1:
            self.solo_label.text = '[b]%s[/b]' % self.game.message
        else:
            self.col_label.text  = '[b]%d[/b]' % self.game.players[0].score
            self.row_label.text  = '[b]%d[/b]' % self.game.players[1].score

    def end_turn(self, anim, card_image):
        self.remove_widget(self.button)
        del self.buttons[self.coords], self.button, self.coords
        
        self.game.current_player = self.game.turn.next()
        if not self.game.current_player.is_empty():
            self.game.current_player.cards[-1].flip()
            
        if self.game.is_round_over():
            return False
        elif self.game.current_player.name == 'Bot1':
            self.computer_turn()
        else:
            for button in self.buttons.values():
                button.disabled = False

    def animate(self, instance, coords, button):
        self.coords, self.button = coords, button

        for button in self.buttons.values():
            button.disabled = True
            
        anim  = Animation(xpos=self.coords[0], y=-5, duration=0.5)
        anim &= Animation(ypos=self.coords[1], x=-5, duration=0.5)
        anim.bind(on_complete=self.update_background)
        if self.game.is_round_over():
            anim.bind(on_complete=self.end_round)
        anim.bind(on_complete=self.end_turn)
            
        anim.start(instance)
        
    def bring_to_front(self, card):
        self.remove_widget(card)
        self.add_widget(card)

    def place_card(self, button):
        coords = (button.xpos, button.ypos)
        
        self.game.cards[coords] = self.game.current_player.pop_card()
        self.bring_to_front(self.game.cards[coords])
        self.animate(self.game.cards[coords], coords, button)

    def computer_turn(self, *args):
        coords, card = self.game.computer_move()
        button = self.buttons[coords]

        self.game.cards[coords] = card
        self.bring_to_front(self.game.cards[coords])
        self.animate(self.game.cards[coords], coords, button)

    def end_round(self, *args):
        self.game.calculate_scores()
        self.game.score_round()
        self.update_score()
        
        if self.game.is_game_over():
            main_button = GridButton(xpos=3, ypos=-1, text='Back to main')
            self.add_widget(main_button)
            main_button.bind(on_release=self.game.game_over_callback)
        else:
            next_button = GridButton(xpos=3, ypos=-1, text='Next round')
            self.add_widget(next_button)
            next_button.bind(on_release=self.game.round_over_callback)

            
            
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.bind(on_pre_enter=self.build)

    def build(self, *args):
        names = self.manager.all_names
        victory_score = self.manager.victory_score
        card_back = self.manager.card_back
        if   self.manager.mode == 'SOLITAIRE':
            self.game = Game(names[:1], victory_score, card_back)
        elif self.manager.mode == '2 PLAYERS':
            self.game = Game(names[:2], victory_score, card_back)
        elif self.manager.mode == '4 PLAYERS':
            self.game = Game(names[:4], victory_score, card_back)
        elif self.manager.mode == 'CHALLENGE':
            self.game = Game([names[0], 'Bot1'], victory_score, card_back)

        self.game.bind(pause_game=self.pause)
        self.game.bind(round_over=self.new_round)
        self.game.bind(game_over =self.goto_main)

        self.board = Board(rows=7, columns=5, game=self.game)
        self.add_widget(self.board)
        self.board.enter_background()

    def pause(self, *args):
        popup_layout = StackLayout(orientation='tb-lr',
                                   spacing=[10,10],
                                   padding=[10,10])

        self.popup = Popup(title='Pause',
                           content=popup_layout, 
                           size_hint=(0.8,0.4))
        self.popup.open()

        victory_score = self.manager.victory_score
        victory_label = Label(text='Playing to {}'.format(victory_score),
                              font_size=30, size_hint=(1,0.5))
        popup_layout.add_widget(victory_label)

        resume_button = Button(text='Resume',
                               font_size=30, size_hint=(1,0.5))
        resume_button.bind(on_press=self.popup.dismiss)
        popup_layout.add_widget(resume_button)
    
    def new_round(self, *args):
        self.remove_widget(self.board)
        self.board = Board(rows=7, columns=5, game=self.game)
        self.add_widget(self.board)
        self.board.enter_background()

    def goto_main(self, *args):
        self.remove_widget(self.board)
        self.manager.current = 'main_screen'



class MenuLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MenuLayout, self).__init__(**kwargs)

        self.heading_font_size = 60
        self.button_font_size  = 40

        self.texture = Image(source='cards/felt2.png').texture
        self.texture.wrap = 'repeat'
        self.texture.uvsize = (10,10)
        with self.canvas.before:
            Color(0, 0, 0)
            self.rect = Rectangle(pos=(0,0), size=(2000,2000))
            
        self.orientation, self.spacing, self.padding = ('vertical', 20, [0, 20])

    def enter_background(self, *args):
        with self.canvas.before:
            Color(0, 2, 0)
            self.rect = Rectangle(pos=(0,0), size=(2000,2000),
                                  texture=self.texture)

    def exit_background(self, *args):
        with self.canvas.before:
            Color(0, 0, 0)
            self.rect = Rectangle(pos=(0,0), size=(2000,2000))


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        self.layout = MenuLayout()
        self.add_widget(self.layout)
        self.make_widgets()
        self.bind(on_pre_enter=self.layout.enter_background)
        self.bind(on_leave=self.layout.exit_background)

    def make_widgets(self):
        self.layout.add_widget(Label(text='SETTINGS',
                                     font_size=self.layout.heading_font_size,
                                     pos_hint={'center_x':.5},
                                     size_hint=(0.9,0.9)))
        
        button_names = ('EDIT NAMES', self.popup_names), \
                       ('VICTORY SCORE', self.popup_score), \
                       ('CARDBACKS', self.popup_backs), \
                       ('BACK TO MENU', self.goto_main)

        for name in button_names:
            button = Button(text=name[0],
                            font_size=self.layout.button_font_size,
                            pos_hint={'center_x':.5}, size_hint=(0.9,0.9))
            button.bind(on_press=name[1])
            self.layout.add_widget(button)

    def popup_names(self, button):
        popup_layout = StackLayout(orientation='tb-lr',
                                   spacing=[20,20],
                                   padding=[20,20])

        self.popup = Popup(title='Edit Names',
                           content=popup_layout, 
                           size_hint=(0.8,None), height=290)
        self.popup.open()
        
        for num in range(1,5):
            label_text = 'Player ' + str(num)
            label = Label(text=label_text, size_hint=(0.5,None), height=30)
            popup_layout.add_widget(label)

        self.name_inputs = []            
        for name in self.manager.all_names:
            name_input = TextInput(text=name, multiline=False,
                                   size_hint=(0.5,None), height=30)
            name_input.bind(on_text_validate=self.change_names)
            self.name_inputs.append(name_input)
            popup_layout.add_widget(name_input)
                    
    def change_names(self, name_input):
        for i in range(4):
            self.manager.all_names[i] = self.name_inputs[i].text
            
    def popup_score(self, button):
        popup_layout = StackLayout(orientation='tb-lr',
                                   spacing=[20,20],
                                   padding=[20,20])

        self.popup = Popup(title='Choose Victory Score',
                           content=popup_layout, 
                           size_hint=(0.8,None), height=150)
        self.popup.open()
        
        label = Label(text='Victory Score', size_hint=(0.5,None), height=30)
        popup_layout.add_widget(label)
            
        score_input = TextInput(text=str(self.manager.victory_score),
                                multiline=False,
                                size_hint=(0.5,None), height=30)
        score_input.bind(on_text_validate=self.change_score)
        popup_layout.add_widget(score_input)

    def change_score(self, text_input):
        self.manager.victory_score = int(text_input.text)
        self.popup.dismiss()

    def popup_backs(self, button):
        popup_layout = StackLayout(orientation='lr-tb',
                                   spacing=[20,20],
                                   padding=[20,20])

        self.popup = Popup(title='Choose Card Backs',
                           content=popup_layout, 
                           size_hint=(0.8,0.85))
        self.popup.open()
        
        for value in range(1,7):
            source = 'cards/back{}.png'.format(str(value))
            card_button = CardButton(source=source, size_hint=(0.5, 0.3))
            card_button.value = value
            card_button.bind(on_press=self.change_backs)
            popup_layout.add_widget(card_button)
            
    def change_backs(self, card_button):
        self.manager.card_back = card_button.value
        self.popup.dismiss()
        
    def goto_main(self, button):
        self.manager.current = 'main_screen'
        


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.layout = MenuLayout()
        self.add_widget(self.layout)
        self.make_widgets()
        self.bind(on_pre_enter=self.layout.enter_background)
        self.bind(on_leave=self.layout.exit_background)

    def make_widgets(self):
        title = Label(text='GRIDDAGE', font_size=self.layout.heading_font_size,
                      pos_hint={'center_x':.5}, size_hint=(0.9,0.9))
        self.layout.add_widget(title)
        
        button_names = ['SOLITAIRE', '2 PLAYERS', '4 PLAYERS',
                        'CHALLENGE', 'SETTINGS']
        
        for name in button_names:
            button = Button(text=name, font_size=self.layout.button_font_size, 
                            pos_hint={'center_x':.5}, size_hint=(0.9,0.9))
            button.bind(on_press=self.switch_screens)
            self.layout.add_widget(button)
        
    def switch_screens(self, button):
        self.manager.mode = button.text
        if button.text == 'SETTINGS':
            self.manager.current = 'settings_screen'
        else:
            self.manager.current = 'game_screen'



class ScreenManager(ScreenManager, EventDispatcher):
    victory_score = NumericProperty(61)
    all_names = ListProperty(['Anna', 'Jan', 'Garret', 'Johno'])
    card_back = NumericProperty(1)



class GriddageApp(App):
    def build(self):    
        self.manager = ScreenManager()

        self.manager.mode = 'Initial'

        self.main_screen = MainScreen(name='main_screen')
        self.manager.add_widget(self.main_screen)

        self.game_screen = GameScreen(name='game_screen')
        self.manager.add_widget(self.game_screen)

        self.settings_screen = SettingsScreen(name='settings_screen')
        self.manager.add_widget(self.settings_screen)
        
        return self.manager

    

if __name__ == "__main__":
    GriddageApp().run()
