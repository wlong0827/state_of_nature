import random

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
		action = random.randint(0, len(legal_actions) - 1)

		return legal_actions[action]

	def get_id(self):
		return self.id

class StateOfNature():
	
	def __init__(self, board_size):
		self.size = board_size
		self.state = [0 for _ in range(board_size ** 2)]
		self.territory = {"P1": 1, "P2": 2}
		self.players = ["P1", "P2"]
		self.turn = 0

		self.state[0] = "P1"
		self.state[board_size ** 2 - 1] = "P2"

	def move(self, action):

		player_id = self.players[self.turn]
		self.turn = (self.turn + 1) % len(self.players)
		player_pos = self.state.index(player_id)

		if action == "up":
			new_pos = player_pos - self.size
		elif action == "down":
			new_pos = player_pos + self.size
		elif action == "right":
			new_pos = player_pos + 1
		elif action == "left":
			new_pos = player_pos - 1
		elif action == "stay":
			new_pos = player_pos
		
		marker = self.territory[player_id]

		self.state[player_pos] = marker
		self.state[new_pos] = player_id

		return (self.state.count(marker), self.state)

	def get_player_pos(self, player_id):
		return self.state.index(player_id)

	def get_cur_state(self):
		return self.state

	def get_cur_turn(self):
		return self.turn

	def __str__(self):
		string = ""
		for i in range(self.size):
			start = i * self.size
			end = start + self.size
			string += str(self.state[start:end]) + "\n"
		
		return string

