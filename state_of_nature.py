from players import *
from game import *
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import json
import sys
import datetime

# Usage: python state_of_nature.py 
# BOARD_SIZE PLAYER_0_TYPE PLAYER_1_TYPE N_STEPS TRIALS VERBOSE WRITE_TO_PLOTLY
# Example: python state_of_nature.py 3 R 10000 1 False False

assert(len(sys.argv) == 8)
board_size = int(sys.argv[1])
player_0_type = sys.argv[2]
player_1_type = sys.argv[3]
trials = int(sys.argv[4])
n_steps = int(sys.argv[5])

if sys.argv[6] == "True":
    verbose = True
else:
    verbose = False

if sys.argv[7] == "True":
    write_to_plotly = True
else:
    write_to_plotly = False

hyperparameters = [10000]

def run_beam_game(n_steps):
    game = BeamGame()
    player_1 = QLPlayer("P0", game.get_actions())
    rewards = defaultdict(list)

    for step in range(n_steps):
        state = game.get_state()

        a = player_1.simple_act(state)

        r, state_next = game.move(a)

        player_1.update_Q(state, r, a, state_next)

        if verbose:
            print player_1.get_Q()
            print "took action {} and got reward {}".format(a, r)

        rewards[player_1].append(r)

    p1_score = sum(list(rewards[player_1]))

    metrics = game.get_metrics()
    print metrics
    print p1_score

def run_state_of_nature(n_steps, player_0_type, player_1_type, board_size):

    game = StateOfNature(board_size)

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

        if verbose:
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
        q_table = dict(player_0.get_Q())
        f.write(str(q_table))

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
        n_steps = hyperparameter

        for trial in range(trials):

            # run_beam_game(n_steps)

            print "----------------------------"
            print "Trial {} results".format(trial + 1)
            print "----------------------------"

            metrics = run_state_of_nature(n_steps, player_0_type, player_1_type, board_size)
            score = metrics["P0"]["total_score"]
            invasion = metrics["P0"]["num_invasions"]
            scores.append(float(score) / float(n_steps))
            invasions.append(float(invasion) / float(n_steps))

        hyper_scores_avg.append(scores)
        hyper_invasions_pct.append(invasions)

    if write_to_plotly:

        if len(hyperparameters) == 1:
            trace1 = {
                        "y": [score[0] for score in scores], 
                        "x": ["Trial " + str(trial) for trial in range(trials)], 
                        "marker": {"color": "pink", "size": 12}, 
                        "mode": "markers", 
                        "name": "{} Player".format(player_0_type), 
                        "type": "scatter"
                    }       

            trace2 = {
                        "y": [score[1] for score in scores], 
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
            for i in range(len(hyperparameters)):
                data.append(go.Box(y = hyper_invasions_pct[i]))

            layout = {"title": "{} vs {} Player on {}x{} Board over {}" \
                        .format(player_0_type, player_1_type, board_size, board_size, hyperparameters), 
                      "xaxis": {"title": "Number of Game Steps", }, 
                      "yaxis": {"title": "Total Invasions"}}

        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d %H:%m")

        print "Producing plots..."
        fig = go.Figure(data=data, layout=layout)
        py.iplot(fig, filename='{} vs {} ({})'.format(player_0_type, player_1_type, date))
        print "Finished"

if __name__ == "__main__":
    main()
