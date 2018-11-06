import random
import numpy as np

class Player():

	def __init__(self, _id):
		self.actions = ["up", "down", "left", "right", "stay"]
		self.id = _id

	def get_legal_actions(self, player_id, players, state, size):
		legal_actions = ["stay"]
		player_pos = state.index(player_id)

		# Check if player is on top row
		if player_pos >= size and (player_pos - size) >= 0:
			if not state[player_pos - size] in players:
				legal_actions.append("up")
		# Check if player is on bottom row
		if (player_pos < size ** 2 - size) and (player_pos + size) < size ** 2:
			if not state[player_pos + size] in players:
				legal_actions.append("down")
		# Check if player is on right hand side
		if (player_pos + 1) % size is not 0 and (player_pos + 1) < size ** 2:
			if not state[player_pos + 1] in players:
				legal_actions.append("right")
		# Check if player is on left hand side
		if player_pos % size is not 0 and (player_pos - 1) >= 0:
			if not state[player_pos - 1] in players:
				legal_actions.append("left")

		return legal_actions

	def random_act(self, player_id, players, state, size):

		legal_actions = self.get_legal_actions(player_id, players, state, size)
		legal_actions = np.random.permutation(legal_actions)
		action = random.randint(0, len(legal_actions) - 1)

		return legal_actions[action]

	def simple_random_act(self, actions):
		action = random.randint(0, len(actions) - 1)
		return actions[action]

	def get_id(self):
		return self.id

class BeamGame():

	def __init__(self):
		self.players = ["P1"]
		self.state = [0, 1]
		self.actions = ["right", "left"]
		self.metrics = {
				"right": 0,
				"left": 0
			}

	def move(self, action):

		if action == "right":
			self.metrics["right"] += 1
			return (0, self.state)
		elif action == "left":
			self.metrics["left"] += 1
			return (1, self.state)

	def get_metrics(self):
		return self.metrics

	def get_actions(self):
		return self.actions

	def get_state(self):
		return self.state

class StateOfNature():
	
	def __init__(self, board_size):
		self.size = board_size
		self.state = [0 for _ in range(board_size ** 2)]
		self.territory = {"P1": 1, "P2": 2}
		self.players = ["P1", "P2"]
		self.actions = ["up", "down", "left", "right", "stay"]
		self.turn = 0

		self.state[0] = "P1"
		self.state[board_size ** 2 - 1] = "P2"
		self.was_invaded = {"P1": False, "P2": False}
		self.metrics = {
			"P1": {
					"num_invasions": 0
				},
			"P2": {
					"num_invasions": 0
				}
			}
		for act in self.actions:
			for player in self.players:
				self.metrics[player][act] = 0

	def move(self, action):

		player_id = self.players[self.turn]
		self.turn = (self.turn + 1) % len(self.players)
		player_pos = self.state.index(player_id)

		if action == "up":
			new_pos = player_pos - self.size
			self.metrics[player_id]["up"] += 1
		elif action == "down":
			new_pos = player_pos + self.size
			self.metrics[player_id]["down"] += 1
		elif action == "right":
			new_pos = player_pos + 1
			self.metrics[player_id]["right"] += 1
		elif action == "left":
			new_pos = player_pos - 1
			self.metrics[player_id]["left"] += 1
		elif action == "stay":
			new_pos = player_pos
			self.metrics[player_id]["stay"] += 1
		
		marker = self.territory[player_id]
		prev_tenant = self.state[new_pos]
		reward = 0

		if action == "up":
			reward += 10
		else:
			reward -= 10

		if prev_tenant in self.territory.values() and prev_tenant is not marker:
			# Player has invaded another player's territory
			# reward += 100
			if prev_tenant == "1":
				assert(player_id == "P2")
			if prev_tenant == "2":
				assert(player_id == "P1")

			self.was_invaded[self.players[self.turn]]
			self.metrics[player_id]["num_invasions"] += 1

		self.state[player_pos] = marker
		self.state[new_pos] = player_id
		reward += self.state.count(marker)

		if self.was_invaded[player_id]:
			reward -= 10
			self.was_invaded[player_id] = False

		return (reward, self.state)

	def get_actions(self):
		return self.actions

	def get_player_pos(self, player_id):
		return self.state.index(player_id)

	def get_cur_state(self):
		return self.state

	def get_cur_turn(self):
		return self.turn

	def get_metrics(self):
		return self.metrics

	def get_actions(self):
		return self.actions

	def __str__(self):
		string = ""
		for i in range(self.size):
			start = i * self.size
			end = start + self.size
			string += str(self.state[start:end]) + "\n"
		
		return string

