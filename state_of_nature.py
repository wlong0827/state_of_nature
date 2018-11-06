from q_learning import *
from game import *
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

n_steps = 50000
trials = 1
board_size = 3

def main():

    scores = []

    for trial in range(trials):

        game = StateOfNature(board_size)

        if isinstance(game, BeamGame):
            player_1 = QLPlayer("P1", game.get_actions())
            rewards = defaultdict(list)

            for step in range(n_steps):
                state = game.get_state()

                a = player_1.simple_act(state)

                r, state_next = game.move(a)

                player_1.update_Q(state, r, a, state_next)

                rewards[player_1].append(r)

            p1_score = sum(list(rewards[player_1]))

            metrics = game.get_metrics()
            print metrics
            print p1_score

            return

        # ----------------------------------------------

        if isinstance(game, StateOfNature):
            player_1 = QLPlayer("P1", game.get_actions())
            player_2 = RandomPlayer("P2")
            players = [player_1, player_2]
            player_ids = ["P1", "P2"]

            rewards = defaultdict(list)

            for step in range(n_steps):
                state = game.get_cur_state()
                turn = game.get_cur_turn()
                player = players[turn]

                a = player.act(state, player_ids, board_size)

                r, state_next = game.move(a)

                # print player
                # print r
                # print game

                if isinstance(player, QLPlayer):
                    # print player
                    # print r
                    # print game
                    player.update_Q(state, r, a, state_next)

                rewards[player].append(r)

            p1_score = sum(list(rewards[player_1]))
            p2_score = sum(list(rewards[player_2]))

            metrics = game.get_metrics()

            print "Trial {} results".format(trial)
            print "----------------------------"
            print "Player 1 total score: ", p1_score
            print "Player 1 invasions: ", metrics["P1"]["num_invasions"]
            print "Player 1 actions: ", metrics["P1"]
            print "\n"
            print "Player 2 total score: ", p2_score
            print "Player 2 invasions: ", metrics["P2"]["num_invasions"]
            print "Player 2 actions: ", metrics["P2"]
            print "\n"
            scores.append((p1_score, p2_score))

    return

    trace1 = {
                "y": [score[0] for score in scores], 
                "x": ["Trial " + str(trial) for trial in range(trials)], 
                "marker": {"color": "pink", "size": 12}, 
                "mode": "markers", 
                "name": "Q-Learning Player", 
                "type": "scatter"
            }       

    trace2 = {
                "y": [score[1] for score in scores], 
                "x": ["Trial " + str(trial) for trial in range(trials)], 
                "marker": {"color": "blue", "size": 12}, 
                "mode": "markers", 
                "name": "Q-Learning Player", 
                "type": "scatter"
            }   

    data = [trace1, trace2]
    layout = {"title": "Q-Learning vs Q-Learning Player", 
              "xaxis": {"title": "Trial", }, 
              "yaxis": {"title": "Total Score over 10000 Steps"}}

    print "Producing plots..."
    fig = go.Figure(data=data, layout=layout)
    py.iplot(fig, filename='QLearn vs QLearn')
    print "Finished"

if __name__ == "__main__":
    main()
