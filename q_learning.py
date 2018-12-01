from collections import defaultdict
import random
from game import *
from math import sqrt
import numpy as np

class NoopPlayer(Player):

    def act(self, state, players, size):
        return "stay"

class RandomPlayer(Player):

    def act(self, state, players, size):
        player_id = self.get_id()
        player_pos = state.index(player_id)

        return self.random_act(player_id, players, state, size)

class LateralPlayer(Player):

    def act(self, state, players, size):
        player_id = self.get_id()
        return self.lateral_act(player_id, players, state, size)

class QLPlayer(Player):

    def __init__(self, _id, actions):
        self.Q = defaultdict(lambda: 0)
        self.gamma = 0.3  # Discounting factor (0.99)
        self.alpha = 0.5  # soft update param (0.5)
        self.actions= actions
        self.epsilon = 0.2 # discovery param (0.1)
        self.id = _id

    def update_Q(self, s, r, a, s_next):
        s_next = str(s_next)
        s = str(s)
        max_q_next = max([self.Q[s_next, act] for act in self.actions]) 
        # Do not include the next state's value if currently at the terminal state.
        old_score = self.Q[s,a]
        self.Q[s, a] += self.alpha * (r + self.gamma * max_q_next - self.Q[s, a])
        # print "updating Q[{}, {}] from {} to {}".format(s, a, old_score, self.Q[s,a])

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

    def act(self, state, players, size):

        player_id = self.get_id()
        player_pos = state.index(player_id)

        if random.random() < self.epsilon:
            action = self.random_act(player_id, players, state, size)
            return action

        # Pick the action with highest q value.
        legal_actions = self.get_legal_actions(player_id, players, state, size)
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
