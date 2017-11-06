from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.config import Config
from kivy.app import App
from kivy.uix.button import Button
import itertools
import random


Config.set('graphics', 'width', '1500')
Config.set('graphics', 'height', '450')


class MyApp(App):
    def build(self):

        self.main_box = BoxLayout(orientation='horizontal', spacing=10)

        the_possible_states_button = GridLayout(cols=1)
        layout_current = GridLayout(cols=3)
        layout_possible = GridLayout(cols=3)

        # Create the grid that we play into - Interactive
        for i in range(0, 9):
            btn = Button(text=str(i), background_color=[0, 0.7, 0.9, 0.8], font_size=30, id=str(i))
            layout_current.add_widget(btn)
            btn.bind(on_press=self.callback)

        # Create the grid that displays the possible states that we choose on the left
        for i in range(0, 9):
            btn2 = Button(text=str(i), background_color=[0, 1, 1, 1], font_size=30)
            layout_possible.add_widget(btn2)

        # This is list of buttons that when clicked, display the next possible state
        for i in range(0, 9):
            btn3 = Button(text='Possible State: '+str(i), background_color=[0, 0.3, 0.2, 1], font_size=15)
            the_possible_states_button.add_widget(btn3)
            btn3.bind(on_press=self.draw_possible_state)

        btn = Button(text='Reset Game', background_color=[1, 0, 0, 1], font_size=15)
        btn.bind(on_press=self.reset_game)

        the_possible_states_button.add_widget(btn)

        self.main_box.add_widget(the_possible_states_button)
        self.main_box.add_widget(layout_current)
        self.main_box.add_widget(layout_possible)

        self.all_possible_states()
        self.current_state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        return self.main_box

    def callback(self, btn):
        if btn.text != 'O' and btn.text != 'X':
            if sum(map(abs, self.current_state)) == 0:
                self.reset_game(btn)
            btn.text = 'X'
            self.current_state[int(btn.id)] = 1
            self.get_possible_states()

    def get_possible_states(self):
        # This function just gives the possible next moves of the computer - Just those that have an extra O
        possible_states = []
        ii = 0
        for i in range(0, 9):
            temp = self.current_state[:]

            if temp[i] != -1 and temp[i] != 1:
                temp[i] = -1
                possible_states.append(temp)
                ii = ii + 1

        for i in range(0, 9):
            # For some reason Kivy reverses the order of the buttons after they are added
            if i < len(possible_states):
                self.main_box.children[2].children[9-i].text = str(possible_states[i])
            else:
                self.main_box.children[2].children[9-i].text = 'No more possible states'

        self.possible_states = possible_states
        return possible_states


    def draw_possible_state(self, btn):
        try:
            possible_state_selected = btn.text.replace('[', ' ').replace(']', ' ').replace(',', ' ')
            possible_state_selected = possible_state_selected.split()
            possible_state_selected = map(int, possible_state_selected)

            for i in range(0, 9):
                if possible_state_selected[i] == 1:
                    # For some reason Kivy reverses the order of the buttons after they are added
                    self.main_box.children[0].children[8-i].text = 'X'
                elif possible_state_selected[i] == -1:
                    self.main_box.children[0].children[8-i].text = 'O'
                elif possible_state_selected[i] == 0:
                    self.main_box.children[0].children[8-i].text = ''
        except:
            print "Haven't started yet"


    def end_of_game(self, winner):
        popup = ModalView(size_hint=(None, None), size=(400, 400))
        victory_label = Label(text='Winner', font_size=50)
        popup.add_widget(victory_label)
        popup.open()

    def all_possible_states(self):
        states = []
        for p in itertools.product([-1, 0, 1], repeat=9):
            states.append(p)

        x = [0] * len(states)
        o = [0] * len(states)

        for index in range(0, len(states)):
            x[index] = states[index].count(1)  # Get the number of X's in the state
            o[index] = states[index].count(-1) # Get the number of O's in the state

        difference = map(abs,([a_i - b_i for a_i, b_i in zip(x, o)]))

        remove_indices = []
        # Remove states that there are two X's or two O's more than O's and X's respectively #Remove 10730 states
        for index, value in enumerate(difference):
            if value >= 2:
                remove_indices.append(index)

        states = [states[i] for i in range(1, len(states)) if i not in remove_indices]
        self.all_states = states

    def reset_game(self, btn):
        for i in range(0, 9):
            self.main_box.children[0].children[8-i].text = ''
            self.main_box.children[1].children[8-i].text = ''
            self.main_box.children[2].children[9-i].text = 'Possible state: '+str(i)

        self.current_state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        print 'Reset'

MyApp().run()
#MyApp().all_possible_states()
