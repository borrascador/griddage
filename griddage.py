from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.properties import DictProperty



class BoardDisplay(GridLayout):
    grid = DictProperty( { (x, y): 'back1' \
                           for x in range(1,6) for y in range(1,6) }
    )

    def flip_card(self, x, y):
        self.grid[(x,y)] = 's3r1'



class GriddageApp(App):
    
    def build(self):
        return BoardDisplay()

if __name__ == '__main__':
    GriddageApp().run()
