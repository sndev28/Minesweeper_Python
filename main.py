from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.config import Config
import random
from concurrent.futures import ThreadPoolExecutor
import threading
import time



Window.size = (480,690)


class AdvButton(Button):
    def __init__(self,**kwargs):
        super(Button, self).__init__(**kwargs)
        self.mouse_button = None #mouse_button records what button is pressed
        self.bind(on_touch_down = self.callback_touch_down) #set up a function to be called on mouse events
    def callback_touch_down(self, instance, touch):
        self.mouse_button = touch.button


class Application(App):


    def game_comp(self, button_object, pressed_button, checked_buttons=[]):

        checked_buttons.append(pressed_button)
        
        if pressed_button not in self.mines:
            button_object.background_disabled_normal = ''
            button_object.background_color = (1,1,1,1)
            button_object.disabled = True

            bomb_count = 0

            for i in range(pressed_button[0]-1, pressed_button[0]+2):
                for j in range(pressed_button[1]-1, pressed_button[1]+2):
                    try:
                        if (i,j) in self.mines:
                            bomb_count += 1

                    except IndexError:
                        pass


            if bomb_count == 0:
                for i in range(pressed_button[0]-1, pressed_button[0]+2):
                    for j in range(pressed_button[1]-1, pressed_button[1]+2):
                        if i >= 0 and j >=0:
                            if (i,j) not in checked_buttons:
                                try:
                                    neighbour = self.buttons[i][j]
                                    neighbour.background_disabled_normal = ''
                                    neighbour.background_color = (1,1,1,1)
                                    neighbour.disabled = True                        

                                    self.game_comp(neighbour, (i,j), checked_buttons)

                                except IndexError:
                                    pass

            else:
                button_object.color = (0,0,0,1)
                button_object.text = str(bomb_count)


        


    checked_buttons = []
    flag_first = True

    def pressed(self, object):

        if self.flag_first: 
            self.flag_first = False

            timer = threading.Thread(target=self.timer)
            timer.start()
            

        if object.mouse_button == 'left' : # left clicked box        
            for i, buttonlist in enumerate(self.buttons):
                for j, button in enumerate(buttonlist):
                    if object == button:
                        pressed_button = (i,j)
                        break

            if pressed_button in self.mines: #lost
                for i, buttonlist in enumerate(self.buttons):
                    for j, button in enumerate(buttonlist):
                        if (i,j) in self.mines:
                            button.disabled_color = (1,0,0,1)
                            button.background_color = (1, 1, 1, 1)
                            button.background_disabled_normal = 'flame.jpg'
                        button.disabled = True
                return


            self.game_comp(object, pressed_button, self.checked_buttons)

        elif object.mouse_button == 'right' : # right clicked box
            object.text = 'F'
            object.unbind(on_press = self.pressed)
            object.bind(on_press = self.rebind)


    def rebind(self, object):
        object.text = ''
        object.unbind(on_press = self.rebind)
        object.bind(on_press = self.pressed)

    stopper = True

    def timer(self):
        t1 = time.perf_counter()

        while(self.stopper):
            time.sleep(.9)
            self.root.ids.timer.text = f'Time: {time.strftime("%H:%M:%S", time.gmtime(time.perf_counter() - t1))}' 

        



    buttons = []
    mines = []



    def build(self):
        return Builder.load_file('gui.kv')

    
    def on_start(self, **kwargs):

        color1 = (1, 1, 1, 1)
        color2 = (.5, .5, .5, 1)

        for i in range(26):

            if i%2:
                color = [color1,color2]
            else:
                color = [color2,color1]

            column_buttons = []

            for j in range(22):
                
                button = AdvButton(text='', size=(20, 20), size_hint=(None, None), background_color = color[j%2], on_press = self.pressed)
                # button = AdvButton(text=' ', size=(20, 20), size_hint=(None, None), on_press = self.pressed, background_normal = 'background2.jpg')
                self.root.ids.game_area.add_widget(button)
                column_buttons.append(button)

            self.buttons.append(column_buttons)


        
        self.mines = [(random.randint(0,25), random.randint(0,21)) for _ in range(78)]

       


        

            

        




if __name__ == '__main__':
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    instance = Application()
    instance.run()
    instance.stopper = False