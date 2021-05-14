from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.config import Config
import random
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import sys
import os


Window.size = (480,720)

#pyexe
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



class Minefield:

    def __init__(self, buttons = []):
        self.buttons = buttons
        
        self.timer_on = False    #False => not running, True => running
        self.mines = []
        self.MAX_ROWS = 26
        self.MAX_COLS = 22
        self.MAX_BOMBS = 78
        self.checked_buttons = []
        self.flag_first = True

    def game_comp(self, button_object, pressed_button, checked_buttons=[]):

        checked_buttons.append(pressed_button)

        if pressed_button in self.mines: #lost
            
            self.stopper = False

            for i, buttonlist in enumerate(self.buttons):
                for j, button in enumerate(buttonlist):
                    button.disabled = True
                    if (i,j) in self.mines:
                        button.disabled_color = (1,0,0,1)
                        button.background_color = (1, 1, 1, 1)
                        button.background_disabled_normal = resource_path('flame.jpg')
            
            return -1
        
        else:
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



        if self.iswin():  #did win?
            self.stopper = False
            for i, j in self.mines:
                self.buttons[i][j].disabled = True
            # self.root.ids.progress.text = 'You win!!'

            return 1

        return 0




    def pressed(self, object):

        if self.flag_first: 
            self.flag_first = False

            self.first_click(self.ret_index_of_button(object))

            # For developers use only - reveals bomb positions - uncomment to use
            for i, j in self.mines:
                print(i,',',j)
                self.buttons[i][j].background_color = (1,0,0,1)

            # self.root.ids.progress.text = 'Game under progress!!'
            

        if object.mouse_button == 'right' : # right clicked box
            object.text = 'F'

        else: # left clicked box  or solver click
            if object.text == 'F':   #if flagged remove flag
                object.text = ''

            else: #if not flagged

                object.disabled = True    #disabling the clicked box
                pressed_button = self.ret_index_of_button(object)
                status = self.game_comp(object, pressed_button, self.checked_buttons)   #game setter

                if status == -1:
                    return 'Oof..you landed on a mine!! Game over!!'

                elif status == 1:
                    return 'You win!!'


        return 'Game under progress!!'





    def iswin(self):
        for i, buttonlist in enumerate(self.buttons):
            for j, button in enumerate(buttonlist):
                if (i,j) not in self.mines:
                    if not button.disabled:
                        return False
        return True

    


    def first_click(self, pos):
        self.timer_on = True
        self.mines = [(random.randint(0,self.MAX_ROWS-1), random.randint(0,self.MAX_COLS-1)) for _ in range(self.MAX_BOMBS)]
        
        for index, mine in enumerate(self.mines):
            if mine == pos:
                self.mines[index] = (random.randint(0,self.MAX_ROWS-1), random.randint(0,self.MAX_COLS-1))
                while(self.mines[index] != pos):     #runs in the super rare chance that the same pos is generated again
                    self.mines[index] = (random.randint(0,self.MAX_ROWS-1), random.randint(0,self.MAX_COLS-1))


    def ret_index_of_button(self, check_button):

        for i, buttonlist in enumerate(self.buttons):
            for j, button in enumerate(buttonlist):
                if check_button == button:
                    return (i,j)


# class Solver:
    
#     def __init__(self, list_of_buttons):
#         self.mine_buttons = list_of_buttons
#         self.minefield = Minefield(list_of_buttons)
        

#     def press_button(self, pos):                         #simulates a button press
#         button = self.mine_buttons[pos[0]][pos[1]]
#         button.background_disabled_normal = ''
#         button.background_color = (1,1,1,1)
#         button.disabled = True
#         self.minefield.game_comp()

#     def solve(self):
        
#         pass



        
    





class AdvButton(Button):
    def __init__(self,**kwargs):
        super(Button, self).__init__(**kwargs)
        self.mouse_button = None #mouse_button records what button is pressed
        self.bind(on_touch_down = self.callback_touch_down) #set up a function to be called on mouse events
    def callback_touch_down(self, instance, touch):
        self.mouse_button = touch.button


class Application(App):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.user_start = False     #Checks if user all started. Used for solver.
        self.timer_on = False       #Timer status check
        self.timer_display = threading.Thread(target=self.timer)    #inintializing the timer thread
        


    def press(self, object):

        status = self.minefield.pressed(object)
        self.root.ids.progress.text = status

        if not self.timer_on and self.minefield.timer_on:
            self.timer_on = True
            self.timer_display.start()



    def build(self):
        return Builder.load_file(resource_path('gui.kv'))

    
    def on_start(self, **kwargs):

        self.minefield = Minefield()

        color1 = (1, 1, 1, 1)
        color2 = (.5, .5, .5, 1)
        buttons = []

        #MAX_ROWS, MAX_COLS are declared in the Minefield class

        for i in range(self.minefield.MAX_ROWS):

            if i%2:
                color = [color1,color2]
            else:
                color = [color2,color1]

            column_buttons = []

            for j in range(self.minefield.MAX_COLS):
                
                button = AdvButton(text='', size=(20, 20), size_hint=(None, None), background_color = color[j%2], on_press = self.press)
                self.root.ids.game_area.add_widget(button)
                column_buttons.append(button)

            buttons.append(column_buttons)

        self.minefield.__init__(buttons)

    
    def timer(self):
        t1 = time.perf_counter()

        while(self.timer_on):
            time.sleep(.9)
            self.root.ids.timer.text = f'Time: {time.strftime("%H:%M:%S", time.gmtime(time.perf_counter() - t1))}' 

    

    def solver(self):
        pass

   

        




if __name__ == '__main__':
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    instance = Application()
    instance.run()
    instance.timer_on = False






