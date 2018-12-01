from q_learning import *
from game import *
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import json
import sys
import datetime

# Usage: python state_of_nature.py BOARD_SIZE PLAYER_0_TYPE PLAYER_1_TYPE N_STEPS TRIALS VERBOSE
# Example: python state_of_nature.py 3 R 10000 1 False

assert(len(sys.argv) == 7)
board_size = int(sys.argv[1])
player_0_type = sys.argv[2]
player_1_type = sys.argv[3]
trials = int(sys.argv[4])
n_steps = int(sys.argv[5])

if sys.argv[6] == "True":
    verbose = True
else:
    verbose = False

# n_steps = 10000
# trials = 5
# board_size = 3

def main():

    scores = []

    for trial in range(trials):

        game = StateOfNature(board_size)
        # game = BeamGame()

        if isinstance(game, BeamGame):
            player_1 = QLPlayer("P0", game.get_actions())
            rewards = defaultdict(list)

            for step in range(n_steps):
                state = game.get_state()

                a = player_1.simple_act(state)

                r, state_next = game.move(a)

                player_1.update_Q(state, r, a, state_next)

                print player_1.get_Q()

                rewards[player_1].append(r)

            p1_score = sum(list(rewards[player_1]))

            metrics = game.get_metrics()
            print metrics
            print p1_score

            return

        # ----------------------------------------------

        if isinstance(game, StateOfNature):

            if player_0_type == "Q":
                player_0_name = "Q-Learning"
                player_0 = QLPlayer("P0", game.get_actions())
            elif player_0_type == "R":
                player_0_name = "Random"
                player_0 = RandomPlayer("P0")
            elif player_0_type == "L":
                player_0_name = "Lateral"
                player_0 = LateralPlayer("P0")

            if player_1_type == "Q":
                player_1_name = "Q-Learning"
                player_1 = QLPlayer("P1", game.get_actions())
            elif player_1_type == "R":
                player_1_name = "Random"
                player_1 = RandomPlayer("P1")
            elif player_1_type == "L":
                player_1_name = "Lateral"
                player_1 = LateralPlayer("P1")


            players = [player_0, player_1]
            player_names = [player_0_name, player_1_name]
            player_ids = ["P0", "P1"]

            rewards = defaultdict(list)

            for step in range(n_steps):
                state = game.get_cur_state()
                turn = game.get_cur_turn()
                player = players[turn]

                a = player.act(state, player_ids, board_size)

                r, state_next = game.move(a)

                if verbose:
                    print "{} Player {} moved {} and earned {} reward" \
                        .format(player_names[turn], turn, a, r)
                    print "Metadata: ", state[(game.size ** 2):]
                    print game

                if isinstance(player, QLPlayer):
                    player.update_Q(state, r, a, state_next)

                rewards[player].append(r)

            p0_score = sum(list(rewards[player_0]))
            p1_score = sum(list(rewards[player_1]))
            score = (p0_score, p1_score)
            scores.append(score)
            metrics = game.get_metrics()

            print "----------------------------"
            print "Trial {} results".format(trial + 1)
            print "----------------------------"
            print "Player {} won!\n".format(score.index(max(score)))
            
            print "{} Player Results:".format(player_0_name)
            print "Player 0 total score: ", p0_score
            print "Player 0 invasions: ", metrics["P0"]["num_invasions"]
            print "Player 0 actions: ", metrics["P0"]
            print "\n"
            print "{} Player Results:".format(player_1_name)
            print "Player 1 total score: ", p1_score
            print "Player 1 invasions: ", metrics["P1"]["num_invasions"]
            print "Player 1 actions: ", metrics["P1"]
            print "\n"

    return

    trace1 = {
                "y": [score[0] for score in scores], 
                "x": ["Trial " + str(trial) for trial in range(trials)], 
                "marker": {"color": "pink", "size": 12}, 
                "mode": "markers", 
                "name": "{} Player".format(player_0_name), 
                "type": "scatter"
            }       

    trace2 = {
                "y": [score[1] for score in scores], 
                "x": ["Trial " + str(trial) for trial in range(trials)], 
                "marker": {"color": "blue", "size": 12}, 
                "mode": "markers", 
                "name": "{} Player".format(player_1_name), 
                "type": "scatter"
            }   

    data = [trace1, trace2]
    layout = {"title": "{} vs {} Player on {}x{} Board" \
                .format(player_0_name, player_1_name, board_size, board_size), 
              "xaxis": {"title": "Trial", }, 
              "yaxis": {"title": "Total Score over {} Steps".format(n_steps)}}

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")

    print "Producing plots..."
    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, filename='{} vs {} ({})'.format(player_0_name, player_1_name, date))
    print "Finished"

if __name__ == "__main__":
    main()
