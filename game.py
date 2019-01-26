import random
import numpy as np

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
	
	def __init__(self, board_size, params):
		self.size = board_size
		# Randomly assign initial territory and include indicators for
		# "P0 was invaded" and "P1 was invaded" and game turn
		self.players = ["P0", "P1"]
		self.state = [random.randint(0,1) for _ in range(board_size ** 2)] \
						+ [False for _ in range(len(self.players))] + [0]
		self.actions = ["up", "down", "left", "right", "stay"]
		
		# Contains parameters for incentive structure
		self.params = params

		# Set initial player positions
		self.state[0] = "P0"
		self.state[board_size ** 2 - 1] = "P1"

		# Initialize action metrics
		self.metrics = {
			"P0": {
					"num_invasions": 0
				},
			"P1": {
					"num_invasions": 0
				}
			}
		for act in self.actions:
			for player in self.players:
				self.metrics[player][act] = 0

	def move(self, action):

		turn = self.state[-1] 
		self.state[-1] = (turn + 1) % len(self.players)
		player_id = self.players[turn]
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
		
		marker = self.players.index(player_id)
		prev_tenant = self.state[new_pos]
		reward = 0

		if prev_tenant in range(len(self.players)) and prev_tenant is not marker:
			# Player has invaded another player's territory
			reward += self.params['invade_bonus']

			self.state[self.size ** 2 + prev_tenant] = True
			self.metrics[player_id]["num_invasions"] += 1

		self.state[player_pos] = marker
		self.state[new_pos] = player_id
		
		grid = self.state[:(self.size ** 2)]
		
		if self.params['farming']:
			reward += grid.count(marker)

		if self.state[self.size ** 2 + turn]:
			reward += self.params['invaded_penalty']
			self.state[self.size ** 2 + turn] = False

		return (reward, self.state)

	def get_actions(self):
		return self.actions

	def get_player_pos(self, player_id):
		return self.state.index(player_id)

	def get_cur_state(self):
		return self.state

	def get_cur_turn(self):
		return self.state[-1]

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

