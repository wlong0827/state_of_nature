from players import *
from game import *
from graph import *
from params import PARAMS

import json
import sys
import argparse
import time

# Usage: python state_of_nature.py PLAYER_0_TYPE PLAYER_1_TYPE [-s] [-t] [-v] [-w] [-hp]

parser = argparse.ArgumentParser(description = "Parses Game arguments")
parser.add_argument("player_0_type", default = "")
parser.add_argument("player_1_type", default = "")
parser.add_argument("-3", "--player_2_type", required = False, default = "")
parser.add_argument("-4", "--player_3_type", required = False, default = "")
parser.add_argument("-s", "--size", required = False, default = 3)
parser.add_argument("-t", "--trials", required = False, default = 1)
parser.add_argument("-v", "--verbose", required = False, action='store_true', default = False)
parser.add_argument("-w", "--write", required = False, action='store_true', default = False)
parser.add_argument("-hp", "--hyperparameters", required = False, action='store_true', default = False)

argument = parser.parse_args()

PARAMS['board_size'] = int(argument.size)
trials = int(argument.trials)
player_names_map = {'Q': 'Q-Learning', 'R': 'Random', 'L': 'Lateral'}
player_types = [player_names_map[argument.player_0_type],
           player_names_map[argument.player_1_type]]

if argument.player_2_type:
    player_types.append(player_names_map[argument.player_2_type])
if argument.player_3_type:
    player_types.append(player_names_map[argument.player_3_type])

num_players = len(player_types)

if argument.hyperparameters:
    hyperparameters = PARAMS['plot_params'][PARAMS['plot_type']]['hyperparameters']
else:
    hyperparameters = [PARAMS['plot_params'][PARAMS['plot_type']]['no_hp_runs']]

def run_state_of_nature(n_steps, bin_size, player_types, board_size, bonus, penalty, farming):

    game_params = {
        'invade_bonus': bonus, 
        'invaded_penalty': penalty, 
        'farming': farming,
    }

    game = StateOfNature(board_size, game_params, num_players)

    player_ids = ["P" + str(i) for i in range(num_players)]
    players = []
    for i, player_type in enumerate(player_types):
        if player_type == "Q-Learning":
            players.append(QLPlayer("P" + str(i), game.get_actions()))
        elif player_type == "Random":
            players.append(RandomPlayer("P" + str(i)))
        elif player_type == "Lateral":
            players.append(LateralPlayer("P" + str(i)))

    rewards = defaultdict(list)
    cum_rewards = []
    bin_rewards = 0

    for step in range(1, n_steps + 1):
        cur_state = game.get_cur_state()
        # This line is needed to deepcopy the state!
        cur_state = cur_state[:]
        
        turn = game.get_cur_turn()
        player = players[turn]

        a = player.act(cur_state, player_ids, board_size)

        r, state_next = game.move(a)

        if argument.verbose:
            print "{} Player {} moved {} and earned {} reward" \
                .format(player_types[turn], turn, a, r)
            print "Metadata: ", cur_state[(game.size ** 2):]
            print game

        if isinstance(player, QLPlayer):
            player.update_Q(cur_state, r, a, state_next)

        bin_rewards += r
        rewards[player].append(r)

        if step % bin_size == 0:
            cum_rewards.append(bin_rewards)
            bin_rewards = 0

    player_scores = [sum(list(rewards[p])) for p in players]
    metrics = game.get_metrics()

    print "Player {} won!\n".format(player_scores.index(max(player_scores)))
    
    for i in range(len(players)):
        player_type = player_types[i]
        player_score = player_scores[i]
        print "{} Player Results:".format(player_type)
        print "Player {} total score: {}".format(i, player_score)
        print "Player {} invasions: {}".format(i, metrics["P" + str(i)]["num_invasions"])
        # print "Player {} actions: {}".format(i, metrics["P" + str(i)])
        print "\n"

    if player_types[0] == "Q-Learning":
        f = open("q_network.json", "w+")

        q = players[0].get_Q()
        q_table = {}
        for key in q:
            new_key = key[0] + "-" + key[1]
            q_table[new_key] = q[key]
        q_table = json.dumps(q_table)
        f.write(q_table)

    metrics['cum_rewards'] = cum_rewards
    metrics['cum_invades'] = []

    for i in range(0, len(metrics['invasions']), bin_size):
        binned_invasions = metrics['invasions'][i:(i+bin_size)]
        metrics['cum_invades'].append(binned_invasions.count(True))

    for i in range(num_players):
        metrics["P" + str(i)]["total_score"] = player_scores[i]

    return metrics

def main():

    global player_types
    hyper_scores_avg = []
    hyper_invasions_pct = []
    hyper_cum_rewards = []
    hyper_cum_invades = []

    for hyperparameter in hyperparameters:

        print "\n################################"
        print "New Hyperparameter is {}".format(hyperparameter)
        print "################################"

        scores = []
        invasions = []
        cum_rewards = []
        cum_invades = []

        farming = PARAMS['plot_params'][PARAMS['plot_type']]['farming'] 
        bonus = PARAMS['plot_params'][PARAMS['plot_type']]['invade_bonus']

        if PARAMS['plot_type'] == 'box_n_steps':
            n_steps = hyperparameter
            penalty = PARAMS['plot_params']['box_n_steps']['invaded_penalty']
        elif PARAMS['plot_type'] == 'scatter_penalty':
            multiplier = hyperparameter
            n_steps = PARAMS['plot_params']['scatter_penalty']['n_steps'] 
            penalty = bonus * multiplier
        elif PARAMS['plot_type'] == 'learning_curve':
            penalty = PARAMS['plot_params'][PARAMS['plot_type']]['invaded_penalty']
            n_steps = PARAMS['plot_params']['learning_curve']['n_steps']
            bin_size = int(n_steps * PARAMS['plot_params']['learning_curve']['sample_rate'])
            player_types = hyperparameter

        for trial in range(trials):

            print "----------------------------"
            print "Trial {} results".format(trial + 1)
            print "----------------------------"

            metrics = run_state_of_nature(n_steps, bin_size, player_types, PARAMS['board_size'], bonus, penalty, farming)
            score = metrics["P0"]["total_score"]
            invasion = metrics["P0"]["num_invasions"]
            scores.append(float(score) / float(n_steps))
            invasions.append(float(invasion) / float(n_steps))
            cum_rewards.append(metrics['cum_rewards'])
            cum_invades.append(metrics['cum_invades'])

        hyper_cum_invades.append(cum_invades)
        hyper_scores_avg.append(scores)
        hyper_invasions_pct.append(invasions)
        hyper_cum_rewards.append(cum_rewards)

    if argument.write:
        if PARAMS['plot_type'] == 'learning_curve':
            if PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Collective Score':
                write_line_plot(PARAMS, hyperparameters, player_types, hyper_cum_rewards)
            elif PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Collective Invasions':
                write_line_plot(PARAMS, hyperparameters, player_types, hyper_cum_invades)
        else:
            write_box_plot(PARAMS, hyperparameters, hyper_scores_avg, hyper_invasions_pct, player_types)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print "--- Executed in {} seconds ---".format(time.time() - start_time)
