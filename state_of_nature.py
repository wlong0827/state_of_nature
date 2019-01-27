from players import *
from game import *
import plotly
import plotly.io as pio
import plotly.plotly as py
import plotly.graph_objs as go

import json
import sys
import datetime
import argparse
import os
from statistics import median
import time

# Usage: python state_of_nature.py PLAYER_0_TYPE PLAYER_1_TYPE [-s] [-t] [-v] [-w] [-hp]

PARAMS = {
        'plot_type': 'scatter_penalty',
        'plot_x_name': 'Average Score per Move',
        'plot_params': {
            'box_n_steps': {
                'metric': 'Average Score per Move',
                # 'Percent Invasions of Total Moves'
                'hyperparameters': [500, 1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000],
                'no_hp_runs': 100000,
                'invade_bonus': 10,
                'invaded_penalty': -20,
                'farming': True
            },
            'scatter_penalty': {
                'hyperparameters': [-1,-2,-3],
                'no_hp_runs': -2,
                'n_steps': 50000,
                'invade_bonus': 10,
                'farming': True,
                'metric': 'Average Score per Move'
            },
        }
    }

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

board_size = int(argument.size)
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

def run_state_of_nature(n_steps, player_types, board_size, bonus, penalty, farming):

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

    for step in range(n_steps):
        cur_state = game.get_cur_state()
        # This line is needed to deepcopy the state!
        cur_state = cur_state[:]
        
        turn = game.get_cur_turn()
        player = players[turn]

        a = player.act(cur_state, player_ids, board_size)

        r, state_next = game.move(a)

        if argument.verbose:
            print "{} Player {} moved {} and earned {} reward" \
                .format(player_type[turn], turn, a, r)
            print "Metadata: ", cur_state[(game.size ** 2):]
            print game

        if isinstance(player, QLPlayer):
            player.update_Q(cur_state, r, a, state_next)

        rewards[player].append(r)

    player_scores = [sum(list(rewards[p])) for p in players]
    metrics = game.get_metrics()

    print "Player {} won!\n".format(player_scores.index(max(player_scores)))
    
    for i in range(len(players)):
        player_type = player_types[i]
        player_score = player_scores[i]
        print "{} Player Results:".format(player_type)
        print "Player {} total score: {}".format(i, player_score)
        print "Player {} invasions: {}".format(i, metrics["P" + str(i)]["num_invasions"])
        print "Player {} actions: {}".format(i, metrics["P" + str(i)])
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

    for i in range(num_players):
        metrics["P" + str(i)]["total_score"] = player_scores[i]

    return metrics

def main():

    hyper_scores_avg = []
    hyper_invasions_pct = []

    for hyperparameter in hyperparameters:

        print "\n################################"
        print "New Hyperparameter is {}".format(hyperparameter)
        print "################################"

        scores = []
        invasions = []

        farming = PARAMS['plot_params'][PARAMS['plot_type']]['farming'] 
        bonus = PARAMS['plot_params'][PARAMS['plot_type']]['invade_bonus']

        if PARAMS['plot_type'] == 'box_n_steps':
            n_steps = hyperparameter
            penalty = PARAMS['plot_params']['box_n_steps']['invaded_penalty']
        elif PARAMS['plot_type'] == 'scatter_penalty':
            multiplier = hyperparameter
            n_steps = PARAMS['plot_params']['scatter_penalty']['n_steps'] 
            penalty = bonus * multiplier

        for trial in range(trials):

            # run_beam_game(n_steps)

            print "----------------------------"
            print "Trial {} results".format(trial + 1)
            print "----------------------------"

            metrics = run_state_of_nature(n_steps, player_types, board_size, bonus, penalty, farming)
            # Consider all results from one arbitrary player's view
            score = metrics["P0"]["total_score"]
            invasion = metrics["P0"]["num_invasions"]
            scores.append(float(score) / float(n_steps))
            invasions.append(float(invasion) / float(n_steps))

        hyper_scores_avg.append(scores)
        hyper_invasions_pct.append(invasions)

    if argument.write:

        if len(hyperparameters) == 1:
            trace1 = {
                        "y": [score for score in scores], 
                        "x": ["Trial " + str(trial) for trial in range(trials)], 
                        "marker": {"color": "pink", "size": 12}, 
                        "mode": "markers", 
                        "name": "{} Player".format(player_0_type), 
                        "type": "scatter"
                    }       

            trace2 = {
                        "y": [score for score in scores], 
                        "x": ["Trial " + str(trial) for trial in range(trials)], 
                        "marker": {"color": "blue", "size": 12}, 
                        "mode": "markers", 
                        "name": "{} Player".format(player_1_type), 
                        "type": "scatter"
                    }   
            data = [trace1, trace2]

            layout = {"title": "{} vs {} Player on {}x{} Board" \
                    .format(player_0_type, player_1_type, board_size, board_size), 
                  "xaxis": {"title": "Trial", }, 
                  "yaxis": {"title": "Total Score over {} Steps".format(n_steps)}}

        else:
            data = []
            mids = []

            for i in range(len(hyperparameters)):
                hyp = hyperparameters[i]
                if PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Average Score per Move':
                    data.append(go.Box(y = hyper_scores_avg[i], name=hyp))
                    mids.append(median(hyper_scores_avg[i]))
                elif PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Percent Invasions of Total Moves':
                    data.append(go.Box(y = hyper_invasions_pct[i], name=hyp))
                    mids.append(median(hyper_invasions_pct[i]))

            data.append(go.Scatter(x = hyperparameters, y = mids, mode = 'markers'))

            adversaries = " vs ".join(player_types)

            layout = {"title": "{} Player on {}x{} Board" \
                        .format(adversaries, board_size, board_size), 
                      "xaxis": {"title": "{}: {}".format(PARAMS['plot_x_name'], hyperparameters)}, 
                      "yaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['metric']}}

        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M")

        print "Producing plots..."
        filename = "{} (Bonus: {}, Penalty: {}, {})".format(
            adversaries,
            bonus,
            penalty,
            date)
        fig = go.Figure(data=data, layout=layout)
        py.plot(fig, filename=filename, auto_open=True)
        
        if not os.path.exists('plots'):
            os.mkdir('plots')

        print "Writing {}.png...\n".format(filename)
        pio.write_image(fig, 'plots/{}.png'.format(filename))

if __name__ == "__main__":
    start_time = time.time()
    main()
    print "--- Executed in {} seconds ---".format(time.time() - start_time)
