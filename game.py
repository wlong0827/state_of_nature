import random
import numpy as np
from imgcat import imgcat
from PIL import Image
import os
import time

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
	
	def __init__(self, board_size, params, num_players):
		self.size = board_size
		# Randomly assign initial territory and include indicators for
		# "P0 was invaded" and "P1 was invaded" and game turn
		self.players = ["P" + str(num) for num in range(num_players)]
		self.state = [random.randint(0, num_players - 1) for _ in range(board_size ** 2)] \
						+ [False for _ in range(len(self.players))] + [0]
		self.actions = ["up", "down", "left", "right", "stay", "defer"]
		
		# Contains parameters for incentive structure
		self.params = params

		# Set initial player positions
		self.state[0] = "P0"
		self.state[board_size ** 2 - 1] = "P1"
		if num_players > 2:
			self.state[board_size - 1] = "P2"
		if num_players > 3:
			self.state[board_size ** 2 - board_size] = "P3"

		# Initialize action metrics
		metrics = {'invasions': [], 'stays': [], 'defers': []}
		for p in self.players:
			metrics[p] = {'num_invasions': 0}
		self.metrics = metrics

		for act in self.actions:
			for player in self.players:
				self.metrics[player][act] = 0

	def generate_image(self):
		grid = self.state[:(self.size ** 2)]

		p1 = Image.open('assets/player_1.png').copy()
		p1.thumbnail((75,75))
		p2 = Image.open('assets/player_2.png').copy()
		p2.thumbnail((75,75))
		p1_terr = Image.open('assets/p1_territory.png').copy()
		p1_terr.thumbnail((50,50))
		p2_terr = Image.open('assets/p2_territory.png').copy()
		p2_terr.thumbnail((50,50))
		board = Image.open('assets/board.png').copy()
		board.thumbnail((400, 400))

		for row in range(20, 420, 100):
			for col in range(20, 420, 100):
				pos = (row, col)
				obj = grid.pop(0)
				obj_img = None

				if obj == "P1":
					obj_img = p1
					pos = (pos[0]-10, pos[1]-10)
				elif obj == "P0":
					obj_img = p2
					pos = (pos[0], pos[1]-10)
				elif obj == 0:
					obj_img = p1_terr
				elif obj == 1:
					obj_img = p2_terr

				if obj_img:
					board.paste(obj_img, pos, obj_img)

		return board

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
		elif action == "defer":
			new_pos = player_pos
			self.metrics[player_id]["defer"] += 1

		# Metric updates
		self.metrics["stays"].append(int(action == "stay"))
		self.metrics["defers"].append(int(action == "defer"))

		marker = self.players.index(player_id)
		prev_tenant = self.state[new_pos]
		reward = 0

		# Has Player invaded another player's territory
		if prev_tenant in range(len(self.players)) and prev_tenant is not marker:
			reward += self.params['invade_bonus']

			self.state[self.size ** 2 + prev_tenant] = True
			self.metrics[player_id]["num_invasions"] += 1
			self.metrics["invasions"].append(True)
		else:
			self.metrics["invasions"].append(False)

		grid = self.state[:(self.size ** 2)]
		img = self.generate_image()
		imgcat(img)
		print "\n\n"
		# time.sleep(5)

		# Update positions
		self.state[player_pos] = marker
		self.state[new_pos] = player_id

		if self.params['farming']:
			reward += grid.count(marker)

		# If you defer, but others don't (no compensation later), you lose out
		# if action == "defer":
		# 	reward -= 10

		# Apply invaded penalty if applicable
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

