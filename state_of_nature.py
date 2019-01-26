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

# Usage: python state_of_nature.py PLAYER_0_TYPE PLAYER_1_TYPE [-s] [-t] [-v] [-w] [-hp]

PARAMS = {
        'plot_type': 'scatter_penalty',
        'plot_params': {
            'box_n_steps': {
                'metric': 'Percent Invasions of Total Moves',
                # 'Average Score per Move'
                'hyperparameters': [500, 1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000],
                'no_hp_runs': 100000,
                'invade_bonus': 10,
                'invaded_penalty': -20,
                'farming': True
            },
            'scatter_penalty': {
                'hyperparameters': [-1,-2,-3,-4,-5],
                'no_hp_runs': -2,
                'n_steps': 10000,
                'invade_bonus': 10,
                'farming': True
            },
        }
    }

parser = argparse.ArgumentParser(description = "Parses Game arguments")
parser.add_argument("player_0_type", default = "")
parser.add_argument("player_1_type", default = "")
parser.add_argument("-3", "--player_2", required = False, default = "")
parser.add_argument("-4", "--player_3", required = False, default = "")
parser.add_argument("-s", "--size", required = False, default = 3)
parser.add_argument("-t", "--trials", required = False, default = 1)
parser.add_argument("-v", "--verbose", required = False, action='store_true', default = False)
parser.add_argument("-w", "--write", required = False, action='store_true', default = False)
parser.add_argument("-hp", "--hyperparameters", required = False, action='store_true', default = False)

argument = parser.parse_args()

board_size = int(argument.size)
trials = int(argument.trials)
player_names_map = {'Q': 'Q-Learning', 'R': 'Random', 'L': 'Lateral'}
player_0_type = player_names_map[argument.player_0_type]
player_1_type = player_names_map[argument.player_1_type]

if argument.hyperparameters:
    hyperparameters = PARAMS['plot_params'][PARAMS['plot_type']]['hyperparameters']
else:
    hyperparameters = [PARAMS['plot_params'][PARAMS['plot_type']]['no_hp_runs']]

def run_state_of_nature(n_steps, player_0_type, player_1_type, board_size, bonus, penalty, farming):

    game_params = {
        'invade_bonus': bonus, 
        'invaded_penalty': penalty, 
        'farming': farming,
    }

    game = StateOfNature(board_size, game_params)

    if player_0_type == "Q-Learning":
        player_0 = QLPlayer("P0", game.get_actions())
    elif player_0_type == "Random":
        player_0 = RandomPlayer("P0")
    elif player_0_type == "Lateral":
        player_0 = LateralPlayer("P0")

    if player_1_type == "Q-Learning":
        player_1 = QLPlayer("P1", game.get_actions())
    elif player_1_type == "Random":
        player_1 = RandomPlayer("P1")
    elif player_1_type == "Lateral":
        player_1 = LateralPlayer("P1")


    players = [player_0, player_1]
    player_ids = ["P0", "P1"]
    player_type = [player_0_type, player_1_type]

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

    p0_score = sum(list(rewards[player_0]))
    p1_score = sum(list(rewards[player_1]))
    score = (p0_score, p1_score)
    metrics = game.get_metrics()

    print "Player {} won!\n".format(score.index(max(score)))
    
    print "{} Player Results:".format(player_0_type)
    print "Player 0 total score: ", p0_score
    print "Player 0 invasions: ", metrics["P0"]["num_invasions"]
    print "Player 0 actions: ", metrics["P0"]
    print "\n"
    print "{} Player Results:".format(player_1_type)
    print "Player 1 total score: ", p1_score
    print "Player 1 invasions: ", metrics["P1"]["num_invasions"]
    print "Player 1 actions: ", metrics["P1"]
    print "\n"

    if player_0_type == "Q-Learning":
        f = open("q_network.json", "w+")

        q = player_0.get_Q()
        q_table = {}
        for key in q:
            new_key = key[0] + "-" + key[1]
            q_table[new_key] = q[key]
        q_table = json.dumps(q_table)
        f.write(q_table)

    metrics["P0"]["total_score"] = p0_score
    metrics["P1"]["total_score"] = p1_score

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

            metrics = run_state_of_nature(n_steps, player_0_type, player_1_type, board_size, bonus, penalty, farming)
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
                n_steps = hyperparameters[i]
                if PARAMS['plot_params']['box_n_steps']['metric'] == 'Average Score per Move':
                    data.append(go.Box(y = hyper_scores_avg[i], name=n_steps))
                    mids.append(median(hyper_scores_avg[i]))
                elif PARAMS['plot_params']['box_n_steps']['metric'] == 'Percent Invasions of Total Moves':
                    data.append(go.Box(y = hyper_invasions_pct[i], name=n_steps))
                    mids.append(median(hyper_invasions_pct[i]))

            data.append(go.Scatter(x = hyperparameters, y = [mids], mode = 'markers'))

            layout = {"title": "{} vs {} Player on {}x{} Board" \
                        .format(player_0_type, player_1_type, board_size, board_size), 
                      "xaxis": {"title": "Number of Game steps".format(hyperparameters)}, 
                      "yaxis": {"title": PARAMS['plot_params']['box_n_steps']['metric']}}

        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M")

        print "Producing plots..."
        filename = "{} vs {} (Bonus: {}, Penalty: {}, {})".format(
            player_0_type, 
            player_1_type, 
            bonus,
            penalty,
            date)
        fig = go.Figure(data=data, layout=layout)
        py.plot(fig, filename=filename)
        
        if not os.path.exists('plots'):
            os.mkdir('plots')

        print "Writing {}.png...".format(filename)
        pio.write_image(fig, 'plots/{}.png'.format(filename))

        print "Finished"

if __name__ == "__main__":
    main()
