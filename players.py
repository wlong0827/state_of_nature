from collections import defaultdict
import random
from game import *
from math import sqrt
import numpy as np

class Player():

    def __init__(self, _id):
        self.actions = ["up", "down", "left", "right", "stay", "defer"]
        self.id = _id

    def get_legal_actions(self, player_id, players, state, size, defer_is_legal):
        
        legal_actions = []
        if defer_is_legal:
            legal_actions.append("defer")

        grid = state[:(size ** 2)]
        player_pos = grid.index(player_id)

        # Check if player is on top row
        if player_pos >= size and (player_pos - size) >= 0:
            if not grid[player_pos - size] in players:
                legal_actions.append("up")
        # Check if player is on bottom row
        if (player_pos < size ** 2 - size) and (player_pos + size) < size ** 2:
            if not grid[player_pos + size] in players:
                legal_actions.append("down")
        # Check if player is on right hand side
        if (player_pos + 1) % size is not 0 and (player_pos + 1) < size ** 2:
            if not grid[player_pos + 1] in players:
                legal_actions.append("right")
        # Check if player is on left hand side
        if player_pos % size is not 0 and (player_pos - 1) >= 0:
            if not grid[player_pos - 1] in players:
                legal_actions.append("left")

        if legal_actions == []:
            legal_actions.append("stay")

        return legal_actions

    def lateral_act(self, player_id, players, state, size):
        legal_actions = self.get_legal_actions(player_id, players, state, size)
        p = random.random()

        if "left" in legal_actions and p < 0.5:
            return "left"
        elif "right" in legal_actions:
            return "right"
        else:
            return "stay"

    def random_act(self, player_id, players, state, size, defer_is_legal):

        legal_actions = self.get_legal_actions(player_id, players, state, size, defer_is_legal)
        legal_actions = np.random.permutation(legal_actions)
        action = random.randint(0, len(legal_actions) - 1)

        return legal_actions[action]

    def simple_random_act(self, actions):
        action = random.randint(0, len(actions) - 1)
        return actions[action]

    def get_id(self):
        return self.id

class NoopPlayer(Player):

    def act(self, state, players, size):
        return "stay"

class RandomPlayer(Player):

    def act(self, state, players, size, defer_is_legal):
        player_id = self.get_id()
        player_pos = state.index(player_id)

        return self.random_act(player_id, players, state, size, defer_is_legal)

class LateralPlayer(Player):

    def act(self, state, players, size):
        player_id = self.get_id()
        return self.lateral_act(player_id, players, state, size)

class QLPlayer(Player):

    def __init__(self, _id, actions):
        self.Q = defaultdict(lambda: random.random())
        self.gamma = 0.99  # Discounting factor (0.99)
        self.alpha = 0.5  # soft update param (0.5)
        self.actions= actions
        self.epsilon = 0.1 # discovery param (0.1)
        self.id = _id

    def set_Q(self, Q):
        self.Q = Q

    def get_legal_actions(self, player_id, players, state, size, defer_is_legal):
        
        legal_actions = []
        if defer_is_legal:
            legal_actions.append("defer")

        grid = state[:(size ** 2)]
        player_pos = grid.index(player_id)

        # Check if player is on top row
        if player_pos >= size and (player_pos - size) >= 0:
            if not grid[player_pos - size] in players:
                legal_actions.append("up")
        # Check if player is on bottom row
        if (player_pos < size ** 2 - size) and (player_pos + size) < size ** 2:
            if not grid[player_pos + size] in players:
                legal_actions.append("down")
        # Check if player is on right hand side
        if (player_pos + 1) % size is not 0 and (player_pos + 1) < size ** 2:
            if not grid[player_pos + 1] in players:
                legal_actions.append("right")
        # Check if player is on left hand side
        if player_pos % size is not 0 and (player_pos - 1) >= 0:
            if not grid[player_pos - 1] in players:
                legal_actions.append("left")

        if legal_actions == []:
            return ["stay"]

        return legal_actions

    def update_Q(self, s, r, a, s_next, verbose=False):
        # Pretend as if it's still the player's turn next
        s_next = str(s_next[:-1] + [s[-1]])
        s = str(s)
        max_q_next = max([self.Q[s_next, act] for act in self.actions]) 
        # Do not include the next state's value if currently at the terminal state.
        old_score = (1 - self.alpha) * self.Q[s,a]
        delta = self.alpha * (r + self.gamma * max_q_next - self.Q[s, a])
        self.Q[s, a] = float(old_score + delta)

        # if verbose:
        #     print "updating Q[{}, {}] from {} to {} for {}\n".format(s, a, old_score, self.Q[s,a], self.id)
        self.epsilon = self.epsilon * 0.9999 # Annealing

        return delta

    def simple_act(self, state):
        if random.random() < self.epsilon:
            return self.simple_random_act(self.actions)
        
        state = str(state)
        qvals = {a: self.Q[state, a] for a in self.actions}
        max_q = max(qvals.values())

        actions_with_max_q = [a for a, q in qvals.items() if q == max_q]
        
        # Permute the list of actions in case random values are skewed
        actions_with_max_q = np.random.permutation(actions_with_max_q)
        action = random.randint(0, len(actions_with_max_q) - 1)
        
        return actions_with_max_q[action]

    def act(self, state, players, size, defer_is_legal):

        player_id = self.get_id()
        player_pos = state.index(player_id)

        if random.random() < self.epsilon:
            action = self.random_act(player_id, players, state, size, defer_is_legal)
            return action

        # Pick the action with highest q value.
        legal_actions = self.get_legal_actions(player_id, players, state, size, defer_is_legal)

        # Remove unnecessary metadata
        if len(state) == size * size + len(players) + 1:
            was_invaded = state[(size ** 2):][state[-1]]
            state = state[:(size ** 2)] + [was_invaded]
            state = str(state)

        qvals = {a: self.Q[state, a] for a in self.actions if a in legal_actions}
        max_q = max(qvals.values())

        # In case multiple actions have the same maximum q value.
        actions_with_max_q = [a for a, q in qvals.items() if q == max_q]
        
        # Permute the list of actions in case random values are skewed
        actions_with_max_q = np.random.permutation(actions_with_max_q)
        action = random.randint(0, len(actions_with_max_q) - 1)

        return actions_with_max_q[action]

    def get_Q(self):
        return self.Q

class LOLAPlayer(QLPlayer):

    def get_invade_actions(self, player_id, state, size, legal_actions):
        invade_actions = []
        grid = state[:(size ** 2)]
        player_pos = grid.index(player_id)

        possible_new_pos = {
            "up": player_pos - size,
            "down": player_pos + size,
            "right": player_pos + 1,
            "left": player_pos - 1,
            "stay": player_pos,
            "defer": player_pos,
        }

        num_players = len([spot for spot in grid if "P" in str(spot)])
        other_territory = set(range(num_players)) - set([int(player_id.strip("P"))])
        for action in legal_actions:
            prev_tenant = grid[possible_new_pos[action]]
            
            if prev_tenant in other_territory:
                invade_actions.append(action)

        return invade_actions

    def manual_update_Q(self, s, a, delta, verbose=False):
        s = str(s)
        # if verbose:
        #     print "LOLA Q {} action {} manually changed by {}".format(self.Q[s, a], a, delta)
        self.Q[s, a] = (1 - self.alpha) * self.Q[s, a] + delta
