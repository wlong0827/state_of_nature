import json
from players import *
from game import *
from collections import defaultdict

cooperative = open('assets/LOLA.json', 'r').read()
defective = open('assets/Q-Learning.json', 'r').read()

coop_player_network_load = json.loads(cooperative)
defect_player_network_load = json.loads(defective)

num_coop_network_states = 0
coop_player_network = defaultdict(lambda: random.random())
for key in coop_player_network_load:
	num_coop_network_states += 1
	coop_player_network[key] = coop_player_network_load[key]

num_defect_network_states = 0
defect_player_network = defaultdict(lambda: random.random())
for key in defect_player_network_load:
	num_defect_network_states += 1
	defect_player_network[key] = defect_player_network_load[key]

print "Cooperative Network has {} Q-values".format(num_coop_network_states)
print "Defective Network has {} Q-values".format(num_defect_network_states)

game_params = {
        'invade_bonus': 10, 
        'invaded_penalty': -25, 
        'farming': True,
    }
n_steps = 100000
board_size = 4
num_players = 2

defer_is_legal = True
setups = [
		["Cooperative", "Defective"],
		["Cooperative", "Cooperative"],
		["Defective", "Defective"],
		["Defective", "Cooperative"],
	]

matchups = {}
for i, players in enumerate(setups):
	rewards = {players[0]: 0.0, players[1]: 0.0}
	player_ids = ["P0", "P1"]

	print "Playing game {} vs {} now...".format(players[0], players[1])
	game = StateOfNature(board_size, game_params, num_players)

	player_types = []

	if players[0] == "Cooperative":
		coop_player = QLPlayer("P0", game.get_actions())
		coop_player.set_Q(coop_player_network)
		player_types.append(coop_player)
	else:
		defect_player = QLPlayer("P0", game.get_actions())
		defect_player.set_Q(defect_player_network)
		player_types.append(defect_player)
	if players[1] == "Cooperative":
		coop_player = QLPlayer("P1", game.get_actions())
		coop_player.set_Q(coop_player_network)
		player_types.append(coop_player)
	else:
		defect_player = QLPlayer("P1", game.get_actions())
		defect_player.set_Q(defect_player_network)
		player_types.append(defect_player)


	last_two_moves = []
	for step in range(1, n_steps + 1):
	    cur_state = game.get_cur_state()
	    cur_state = cur_state[:]

	    turn = game.get_cur_turn()
	    player_name = players[turn]
	    player = player_types[turn]
	    player_id = player_ids[turn]

	    if len(last_two_moves) == 2:
	    	if last_two_moves.count("defer") == 2:
	    		rewards[players[0]] += 25
	    		rewards[players[1]] += 25
	    	last_two_moves = []

	    a = player.act(cur_state, player_ids, board_size, defer_is_legal)
	    r, state_next = game.move(a)

	    rewards[player_name] += r

	matchups[(players[0], players[1])] = \
		(rewards[players[0]] / n_steps, rewards[players[1]] / n_steps)

	if players[0] == players[1]:
		matchups[(players[0], players[1])] = (matchups[(players[0], players[1])][0] / 2.0, matchups[(players[0], players[1])][1] / 2.0)

print "---------------------------------------------"
print "             C                        D           "
print " C  {}        {} ".format(matchups[("Cooperative", "Cooperative")], matchups[("Cooperative", "Defective")])
print " D  {}        {}  ".format(matchups[("Defective", "Cooperative")], matchups[("Defective", "Defective")])
print "---------------------------------------------"
