from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.properties import DictProperty, StringProperty, ObjectProperty
from card import Game

game = Game()



class BoardDisplay(GridLayout):
    
    grid = DictProperty( { (x, y): 'back1' \
                           for x in range(1,6) for y in range(1,6) }
    )
    
    next_player = 1

    p1 = StringProperty( str( game.p1.pop_card() ) \
                         if next_player == 1 else 'back1')
    p2 = StringProperty( str( game.p2.pop_card() ) \
                         if next_player == 2 else 'back1')
    
    starter = str(game.starter)

    def flip_card(self, x, y):
        if self.next_player == 1:
            self.grid[(x,y)] = self.p1
            self.p1 = 'back1'
            self.p2 = str( game.p2.pop_card() )
            self.next_player = 2
            return self.next_player
            
        if self.next_player == 2:
            self.grid[(x,y)] = self.p2
            self.p2 = 'back1'
            self.p1 = str( game.p1.pop_card() )
            self.next_player = 1
            return self.next_player



class GriddageApp(App):
    
    def build(self):
        return BoardDisplay()

if __name__ == '__main__':
    GriddageApp().run()
