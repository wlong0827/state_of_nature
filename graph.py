import plotly.io as pio
import plotly.plotly as py
import plotly.graph_objs as go
import datetime
from statistics import median
import os

def write_plot(adversaries, bonus, penalty, data, layout):
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

def write_box_plot(PARAMS, hyperparameters, hyper_scores_avg, hyper_invasions_pct, player_types):

    data = []
    mids = []

    bonus = PARAMS['plot_params'][PARAMS['plot_type']]['invade_bonus']
    penalty = PARAMS['plot_params']['box_n_steps']['invaded_penalty']

    for i in range(len(hyperparameters)):
        hyp = hyperparameters[i]
        if PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Average Score per Move':
            data.append(go.Box(y = hyper_scores_avg[i], name=hyp))
            mids.append(median(hyper_scores_avg[i]))
        elif PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Percent Invasions of Total Moves':
            data.append(go.Box(y = hyper_invasions_pct[i], name=hyp))
            mids.append(median(hyper_invasions_pct[i]))

    data.append(go.Scatter(x = hyperparameters, y = mids, mode = 'markers'))

    adversaries = " vs ".join(player_types).replace('Q-Learning', 'QL').replace('Random', 'R')

    layout = {"title": "{} Player on {}x{} Board" \
                .format(adversaries, PARAMS['board_size'], PARAMS['board_size']), 
              "xaxis": {"title": "{}: {}".format(PARAMS['plot_x_name'], hyperparameters)}, 
              "yaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['metric']}}

    write_plot(adversaries, bonus, penalty, data, layout)

def write_line_plot(PARAMS, hyperparameters, cum_rewards, player_types):

    bonus = PARAMS['plot_params'][PARAMS['plot_type']]['invade_bonus']
    penalty = PARAMS['plot_params'][PARAMS['plot_type']]['invaded_penalty']
    n_steps = hyperparameters[0]

    scatter = go.Scatter(x=range(len(cum_rewards)), y=cum_rewards, mode='lines', name='lines')
    data = [scatter]

    adversaries = " vs ".join(player_types).replace('Q-Learning', 'QL').replace('Random', 'R')

    layout = {"title": "{} Player on {}x{} Board" \
                .format(adversaries, PARAMS['board_size'], PARAMS['board_size']), 
              "xaxis": {"title": "{}: {}".format(PARAMS['plot_params'][PARAMS['plot_type']]['plot_x_name'], n_steps)}, 
              "yaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['metric']}}

    write_plot(adversaries, bonus, penalty, data, layout)


