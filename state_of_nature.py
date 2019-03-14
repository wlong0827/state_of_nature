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
parser.add_argument("-n", "--n_steps", required = False, default = 100000)

argument = parser.parse_args()

PARAMS['board_size'] = int(argument.size)
trials = int(argument.trials)
player_names_map = {'Q': 'Q-Learning', 'R': 'Random', 'L': 'Lateral', 'LOLA': 'LOLA'}
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

def replace(alist, a, b):
    tmp = ["temp" if x == a else x for x in alist]
    tmp = [a if x == b else x for x in tmp]
    tmp = [b if x == "temp" else x for x in tmp]
    return tmp

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
        elif player_type == "LOLA":
            players.append(LOLAPlayer("P" + str(i), game.get_actions()))

    rewards = defaultdict(list)
    cum_rewards = []
    bin_rewards = 0
    bin_actions = defaultdict(list)
    last_actions = defaultdict(int)
    num_successful_defers = []

    batched_moves = []
    batched_prev_states = []
    override_moves = []
    defer_is_legal = True

    for step in range(1, n_steps + 1):
        cur_state = game.get_cur_state()
        # This line is needed to deepcopy the state!
        cur_state = cur_state[:]

        num_successful_defers.append(0)
        successful_defer = False

        # Strategy 1: Majoritarian voting for the Sovereign
        if len(batched_moves) == len(players):
            num_defers = batched_moves.count("defer")
            batched_moves = []

            if num_defers > len(players) / 2:
                num_successful_defers.pop()
                num_successful_defers.append(1)
                successful_defer = True

                # Give everyone a bonus
                for player, prev_state in zip(players, batched_prev_states):
                    # Remove unnecessary metadata
                    was_invaded = prev_state[(board_size ** 2):][prev_state[-1]]
                    ind_prev_state = prev_state[:(board_size ** 2)] + [was_invaded]
                    was_invaded = cur_state[(board_size ** 2):][cur_state[-1]]
                    ind_cur_state = cur_state[:(board_size ** 2)] + [was_invaded]

                    # Strategy 2: Punishment / Reward by the Sovereign
                    if isinstance(player, QLPlayer) and not isinstance(player, LOLAPlayer):
                        delta = player.update_Q(ind_prev_state, 3.25, "defer", ind_cur_state, verbose=argument.verbose)
                    elif isinstance(player, LOLAPlayer):
                        delta = player.update_Q(ind_prev_state, 25, "defer", ind_cur_state, verbose=argument.verbose)

                    rewards[player].append(25)

                if argument.verbose:
                    print "Majority of Players deferred and each earned 25 reward"

                bin_rewards += 25 * len(players)

            batched_prev_states = []

        turn = game.get_cur_turn()
        player = players[turn]
        player_id = player_ids[turn]

        # Initial vote to determine whether defer will be legal
        # all_lola_players = bool(player_types.count("LOLA") == len(player_types))
        # if player_id == "P0" and all_lola_players:
        #     players_who_deferred = 0
        #     for p in players:
        #         a = p.act(cur_state, player_ids, board_size, True)
        #         if a == "defer":
        #             players_who_deferred += 1

        #     if players_who_deferred > len(players) / 2:
        #         defer_is_legal = True
        #     else:
        #         defer_is_legal = False
        # elif player_id == "P0" and all_lola_players == False:
        #     defer_is_legal = True

        a = player.act(cur_state, player_ids, board_size, defer_is_legal)

        batched_moves.append(a)
        batched_prev_states.append(cur_state)

        r, state_next = game.move(a)

        if argument.verbose:
            print "{} Player {} moved {} and earned {} reward" \
                .format(player_types[turn], turn, a, r)
            print "Metadata: ", cur_state[(game.size ** 2):]
            print game

        bin_rewards += r
        rewards[player].append(r)

        if step % bin_size == 0:
            latest_metrics = game.get_metrics()

            for a in game.get_actions():
                total_actions = 0
                for pid in player_ids:
                    total_actions += latest_metrics[pid][a]
                
                last_actions[a] = total_actions - last_actions[a]
                bin_actions[a].append(last_actions[a])
                last_actions[a] = total_actions

            cum_rewards.append(bin_rewards)
            bin_rewards = 0

        # Remove unnecessary metadata
        was_invaded = cur_state[(game.size ** 2):][cur_state[-1]]
        cur_state = cur_state[:(game.size ** 2)] + [was_invaded]

        if isinstance(player, QLPlayer) and not isinstance(player, LOLAPlayer):
            delta = player.update_Q(cur_state, r, a, state_next, verbose=argument.verbose)
        elif isinstance(player, LOLAPlayer) and not successful_defer:
            delta = player.update_Q(cur_state, r, a, state_next, verbose=argument.verbose)
    
            # Strategy 3: Opponent Learning Awareness
            for p, pid in zip(players, player_ids):
                if not p == player: 
                    alternate_reality = replace(cur_state, player_id, pid)
                    p.manual_update_Q(alternate_reality, a, delta, verbose=argument.verbose)

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

    if player_types[0] == "Q-Learning" or player_types[0] == "LOLA":
        f = open("{}.json".format(player_types[0]), "w+")

        q = players[0].get_Q()
        q_table = {}
        for key in q:
            new_key = key[0] + "-" + key[1]
            q_table[new_key] = q[key]
        q_table = json.dumps(q_table)
        f.write(q_table)

    metrics['cum_rewards'] = cum_rewards
    metrics['cum_invades'] = []
    metrics['cum_stays'] = []
    metrics['cum_defers'] = []
    metrics['cum_successful_defers'] = []
    metrics['cum_actions'] = bin_actions

    for i in range(0, n_steps, bin_size):
        binned_invasions = metrics['invasions'][i:(i+bin_size)]
        binned_stays = metrics['stays'][i:(i+bin_size)]
        binned_defers = metrics['defers'][i:(i+bin_size)]
        binned_successful_defers = num_successful_defers[i:(i+bin_size)]
        metrics['cum_invades'].append(binned_invasions.count(True))
        metrics['cum_stays'].append(binned_stays.count(1))
        metrics['cum_defers'].append(binned_defers.count(1))
        metrics['cum_successful_defers'].append(binned_successful_defers.count(1))

    for i in range(num_players):
        metrics["P" + str(i)]["total_score"] = player_scores[i]

    return metrics

def main():

    global player_types
    hyper_scores_avg = []
    hyper_invasions_pct = []
    hyper_cum_rewards = []
    hyper_cum_invades = []
    hyper_cum_stays = []
    hyper_cum_defers = []
    hyper_cum_successful_defers = []

    for hyperparameter in hyperparameters:

        print "\n################################"
        print "New Hyperparameter is {}".format(hyperparameter)
        print "################################"

        scores = []
        invasions = []
        cum_rewards = []
        cum_invades = []
        cum_stays = []
        cum_defers = []
        cum_successful_defers = []

        farming = PARAMS['plot_params'][PARAMS['plot_type']]['farming'] 
        bonus = PARAMS['plot_params'][PARAMS['plot_type']]['invade_bonus']

        if PARAMS['plot_type'] == 'box_n_steps':
            n_steps = hyperparameter
            bin_size = int(n_steps * PARAMS['plot_params']['learning_curve']['sample_rate'])
            penalty = PARAMS['plot_params']['box_n_steps']['invaded_penalty']
        elif PARAMS['plot_type'] == 'scatter_penalty':
            multiplier = hyperparameter
            n_steps = PARAMS['plot_params']['scatter_penalty']['n_steps'] 
            penalty = bonus * multiplier
            bin_size = int(n_steps * PARAMS['plot_params']['scatter_penalty']['sample_rate'])
        elif PARAMS['plot_type'] == 'learning_curve':
            penalty = PARAMS['plot_params'][PARAMS['plot_type']]['invaded_penalty']
            n_steps = PARAMS['plot_params']['learning_curve']['n_steps']
            bin_size = int(n_steps * PARAMS['plot_params']['learning_curve']['sample_rate'])
            player_types = hyperparameter
        elif PARAMS['plot_type'] == 'action_breakdown':
            n_steps = PARAMS['plot_params']['action_breakdown']['n_steps']
            bin_size = int(n_steps * PARAMS['plot_params']['action_breakdown']['sample_rate'])
            penalty = PARAMS['plot_params'][PARAMS['plot_type']]['invaded_penalty']
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
            cum_stays.append(metrics['cum_stays'])
            cum_defers.append(metrics['cum_defers'])
            cum_successful_defers.append(metrics['cum_successful_defers'])

        hyper_cum_successful_defers.append(cum_successful_defers)
        hyper_cum_defers.append(cum_defers)
        hyper_cum_stays.append(cum_stays)
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
            elif PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Collective Stays':
                write_line_plot(PARAMS, hyperparameters, player_types, hyper_cum_stays)
            elif PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Collective Defers':
                write_line_plot(PARAMS, hyperparameters, player_types, hyper_cum_defers)
            elif PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Successful Defers':
                write_line_plot(PARAMS, hyperparameters, player_types, hyper_cum_successful_defers)
        elif PARAMS['plot_type'] == 'action_breakdown':
            write_stack_plot(PARAMS, hyperparameters, player_types, metrics['cum_actions'])
        else:
            write_box_plot(PARAMS, hyperparameters, hyper_scores_avg, hyper_invasions_pct, player_types)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print "--- Executed in {} seconds ---".format(time.time() - start_time)
