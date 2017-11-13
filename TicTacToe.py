from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.config import Config
from kivy.app import App
from kivy.uix.button import Button
import itertools
import random
import numpy as np
import pickle
import os.path


Config.set('graphics', 'width', '1500')
Config.set('graphics', 'height', '450')


class TicTacToeApp(App):
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
            btn3 = Button(text='Possible State: '+str(i), background_color=[0, 0.3, 0.2, 1],
                          font_size=15, color=[0.6, 0.7, 0.6, 1])
            the_possible_states_button.add_widget(btn3)
            btn3.bind(on_press=self.draw_possible_state)

        btn = Button(text='Reset Game', background_color=[1, 0, 0, 1], font_size=20)
        btn.bind(on_press=self.reset_game)

        the_possible_states_button.add_widget(btn)

        self.main_box.add_widget(the_possible_states_button)
        self.main_box.add_widget(layout_current)
        self.main_box.add_widget(layout_possible)

        self.all_possible_states()  # Initialize
        self.policy_evaluation()
        self.current_state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        return self.main_box

    def callback(self, btn):
        if btn.text != 'O' and btn.text != 'X':
            if sum(map(abs, self.current_state)) == 0:
                self.reset_game()
            btn.text = 'X'
            self.current_state[int(btn.id)] = 1
            self.get_possible_states()
            self.is_game_over()

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
            print "Haven't started yet or No state to display"

    def all_possible_states(self):

        if not(os.path.isfile('unique_states.pkl')):
            # If needed to be computed again, run this - Total number: 1952
            states = []
            for p in itertools.product([-1, 0, 1], repeat=9):
                states.append(p)

            print 'All possible combination states: ' + str(len(states))

            x = [0] * len(states)
            o = [0] * len(states)

            for index in range(0, len(states)):
                x[index] = states[index].count(1)  # Get the number of X's in the state
                o[index] = states[index].count(-1) # Get the number of O's in the state

            difference = map(abs, ([a_i - b_i for a_i, b_i in zip(x, o)]))

            remove_indices = []
            # Remove states that there are two X's or two O's more than O's and X's respectively #Remove 10730 states
            for index, value in enumerate(difference):
                if value >= 2:
                    remove_indices.append(index)

            states = [states[i] for i in range(0, len(states)) if i not in remove_indices]

            print "States that don't violate number of turns: " + str(len(states))



            # Get rid of states where both players won
            remove_both_won = []

            for i in range(0, len(states)):
                realState = list(states[i])
                # Get rid of the states that can't happen cause the game already finished
                s = realState
                if (((([s[0],s[1],s[2]] == [1,1,1] or [s[3],s[4],s[5]] == [1,1,1] or [s[6],s[7],s[8]] == [1,1,1] or
                       [s[0],s[3],s[6]] == [1,1,1] or [s[1],s[4],s[7]] == [1,1,1] or [s[2],s[5],s[8]] == [1,1,1] or
                       [s[0],s[4],s[8]] == [1,1,1] or [s[2],s[4],s[6]] == [1,1,1]) and s.count(-1)>s.count(1))) or
                    ((([s[0],s[1],s[2]] == [-1,-1,-1] or [s[3],s[4],s[5]] == [-1,-1,-1] or [s[6],s[7],s[8]] == [-1,-1,-1] or
                       [s[0],s[3],s[6]] == [-1,-1,-1] or [s[1],s[4],s[7]] == [-1,-1,-1] or [s[2],s[5],s[8]] == [-1,-1,-1] or
                       [s[0],s[4],s[8]] == [-1,-1,-1] or [s[2],s[4],s[6]] == [-1,-1,-1]) and s.count(1)>s.count(-1)))) or \
                      ([s[0],s[1],s[2]] == [1,1,1] or [s[3],s[4],s[5]] == [1,1,1] or [s[6],s[7],s[8]] == [1,1,1] or
                       [s[0],s[3],s[6]] == [1,1,1] or [s[1],s[4],s[7]] == [1,1,1] or [s[2],s[5],s[8]] == [1,1,1] or
                       [s[0],s[4],s[8]] == [1,1,1] or [s[2],s[4],s[6]] == [1,1,1]) and \
                      ([s[0],s[1],s[2]] == [-1,-1,-1] or [s[3],s[4],s[5]] == [-1,-1,-1] or [s[6],s[7],s[8]] == [-1,-1,-1] or
                       [s[0],s[3],s[6]] == [-1,-1,-1] or [s[1],s[4],s[7]] == [-1,-1,-1] or [s[2],s[5],s[8]] == [-1,-1,-1] or
                       [s[0],s[4],s[8]] == [-1,-1,-1] or [s[2],s[4],s[6]] == [-1,-1,-1]):
                    remove_both_won.append(i)

            states = [states[i] for i in range(0, len(states)) if i not in remove_both_won]
            print 'States after both won removed: ' + str(len(states))


            '''
            # Get rid of rotations or reflections
            rotated_states_indices = []

            self.rot90_indices = [6, 3, 0, 7, 4, 1, 8, 5, 2]
            self.rot180_indices = [8, 7, 6, 5, 4, 3, 2, 1, 0]
            self.rot270_indices = [2, 5, 8, 1, 4, 7, 0, 3, 6]

            self.reflection_x_indices = [2, 1, 0, 5, 4, 3, 8, 7, 6]
            self.reflection_y_indices = [6, 7, 8, 3, 4, 5, 0, 1, 2]

            for i in range(0, len(states)):

                realState = list(states[i])
                rotated90_State = tuple(
                    [realState[self.rot90_indices[internal_index]] for internal_index in range(len(realState))])
                rotated180_State = tuple(
                    [realState[self.rot180_indices[internal_index]] for internal_index in range(len(realState))])
                rotated270_State = tuple(
                    [realState[self.rot270_indices[internal_index]] for internal_index in range(len(realState))])

                reflection_x_State = tuple(
                    [realState[self.reflection_x_indices[internal_index]] for internal_index in range(len(realState))])
                reflection_y_State = tuple(
                    [realState[self.reflection_y_indices[internal_index]] for internal_index in range(len(realState))])

                for j in range(i + 1, len(states)):
                    if states[j] == rotated90_State or states[j] == rotated180_State or states[j] == rotated270_State or \
                                    states[j] == reflection_x_State or states[j] == reflection_y_State:
                        rotated_states_indices.append(j)

            rotated_states_indices = sorted(set(rotated_states_indices))
            states = [states[i] for i in range(0, len(states)) if i not in rotated_states_indices]

            print "States that are not rotations or reflections or after game over: " + str(len(states))
            '''


            # Save
            with open('unique_states.pkl', 'w') as f:
                pickle.dump(states, f)
                print 'Saved a new one'
        else:
            # Load
            with open('unique_states.pkl') as f:
                states = pickle.load(f)
                print 'Loaded the one already saved'

        self.all_states = states


    def policy_evaluation(self):

        rewards_matrix = [0] * len(self.all_states)

        for iState in range(0, len(self.all_states)):
            s = self.all_states[iState]

            # Winner X
            if ([s[0], s[1], s[2]] == [1, 1, 1] or [s[3], s[4], s[5]] == [1, 1, 1] or [s[6], s[7], s[8]] == [1, 1, 1] or
                [s[0], s[3], s[6]] == [1, 1, 1] or [s[1], s[4], s[7]] == [1, 1, 1] or [s[2], s[5], s[8]] == [1, 1, 1] or
                [s[0], s[4], s[8]] == [1, 1, 1] or [s[2], s[4], s[6]] == [1, 1, 1]):
                rewards_matrix[iState] = 1
            # Winner O
            elif ([s[0], s[1], s[2]] == [-1, -1, -1] or [s[3], s[4], s[5]] == [-1, -1, -1] or [s[6], s[7], s[8]] == [-1, -1, -1] or
                  [s[0], s[3], s[6]] == [-1, -1, -1] or [s[1], s[4], s[7]] == [-1, -1, -1] or [s[2], s[5], s[8]] == [-1, -1, -1] or
                  [s[0], s[4], s[8]] == [-1, -1, -1] or [s[2], s[4], s[6]] == [-1, -1, -1]):
                rewards_matrix[iState] = -1

        print rewards_matrix.count(-1)  # 181 ?????
        print rewards_matrix.count(1)  # 226  ?????

        # All transitions will have reward=0, winning X state will return +1, winning O state will return -1
        # Discounting will be set to 0

        theta = 0.01  # End of iterations condition
        delta = 0.1  # Difference among value functions

        state_value_function = [0] * len(self.all_states)
        updated_state_value_function = [0] * len(self.all_states)


        # Get transition matrix
        transition_matrix = np.zeros((len(self.all_states), len(self.all_states)))
        for i in range(0, len(self.all_states)):
            for j in range(i+1, len(self.all_states)):
                different_positions = np.not_equal(self.all_states[i], self.all_states[j])
                blank_that_got_filled = [index for index, x in enumerate(different_positions) if x]
                if sum(different_positions) == 1:
                    blank_that_got_filled = blank_that_got_filled[0]

                    if self.all_states[i][blank_that_got_filled] == 0:  # The previous state had an empty spot
                        transition_matrix[i, j] = 1

        print 'Done'
        '''
        while delta > theta:
            for iState in range(0, len(self.all_states)):
                x = self.all_states[iState].count(1)
                o = self.all_states[iState].count(-1)
                empty_spots = self.all_states[iState].count(0)

                updated_state_value_function[iState] = 1/(2*empty_spots)*([rewards_matrix[iState] + state_value_function])
        '''


    def announce_winner(self, winner):
        if winner == 1:
            winner = 'Winner X'
        elif winner == -1:
            winner = 'Winner O'
        elif winner == 0:
            winner = 'Draw'
        popup = ModalView(size_hint=(None, None), size=(400, 200))
        victory_label = Button(text=winner, font_size=50, background_color=[0, 1, 0, 1])
        popup.add_widget(victory_label)
        popup.open()
        self.reset_game()


        if not (os.path.isfile('winner_count.pkl')):
            winner_count = dict()
            winner_count['Winner O'] = 0
            winner_count['Winner X'] = 0
            winner_count['Draw'] = 0

            print winner_count
            winner_count[str(winner)] = 1
            print winner_count

            with open('winner_count.pkl', 'w') as f:
                pickle.dump(winner_count, f)
                print 'Saved a new winner_count'

        else:
            with open('winner_count.pkl') as f:
                winner_count = pickle.load(f)
                print 'Loaded the winner_count'

            print winner
            print winner_count
            winner_count[winner] = winner_count[winner] + 1

            with open('winner_count.pkl', 'w') as f:
                pickle.dump(winner_count, f)
                print 'Saved a new winner_count'

            print winner_count



    def is_game_over(self):

        s = self.current_state

        if ([s[0],s[1],s[2]]==[1,1,1] or [s[3],s[4],s[5]]==[1,1,1] or [s[6],s[7],s[8]]==[1,1,1] or
            [s[0],s[3],s[6]]==[1,1,1] or [s[1],s[4],s[7]]==[1,1,1] or [s[2],s[5],s[8]]==[1,1,1] or
            [s[0],s[4],s[8]]==[1,1,1] or [s[2],s[4],s[6]]==[1,1,1]):
            self.announce_winner(1)
        elif ([s[0],s[1],s[2]]==[-1,-1,-1] or [s[3],s[4],s[5]]==[-1,-1,-1] or [s[6],s[7],s[8]]==[-1,-1,-1] or
              [s[0],s[3],s[6]]==[-1,-1,-1] or [s[1],s[4],s[7]]==[-1,-1,-1] or [s[2],s[5],s[8]]==[-1,-1,-1] or
              [s[0],s[4],s[8]]==[-1,-1,-1] or [s[2],s[4],s[6]]==[-1,-1,-1]):
            self.announce_winner(-1)

        elif s.count(0) == 0:
            self.announce_winner(0)


    def reset_game(self):
        for i in range(0, 9):
            self.main_box.children[0].children[8-i].text = ''
            self.main_box.children[1].children[8-i].text = ''
            self.main_box.children[2].children[9-i].text = 'Possible state: '+str(i)

        player_starts = random.randint(0, 1)

        if player_starts:  # Computer starts
            starting_random_point = random.randint(0, 8)
            self.current_state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.current_state[starting_random_point] = -1
            self.main_box.children[1].children[8-starting_random_point].text = 'O'

        else:
            self.current_state = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        print 'Reset'

TicTacToeApp().run()
