import plotly.io as pio
import plotly.plotly as py
import plotly.graph_objs as go
import datetime
from statistics import median
import os

def write_plot(adversaries, data, layout):
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M")

    print "Producing plots..."
    filename = "{} ({})".format(
        adversaries,
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

    layout = {"title": "{} Player on {}x{} Board (bonus: {}, penalty: {})" \
                .format(adversaries, PARAMS['board_size'], PARAMS['board_size'], bonus, penalty), 
              "xaxis": {"title": "{}: {}".format(PARAMS['plot_x_name'], hyperparameters)}, 
              "yaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['metric']}}

    write_plot(adversaries, data, layout)

def write_line_plot(PARAMS, hyperparameters, hyper_cum_rewards, player_types):

    bonus = PARAMS['plot_params'][PARAMS['plot_type']]['invade_bonus']
    penalty = PARAMS['plot_params'][PARAMS['plot_type']]['invaded_penalty']
    n_steps = PARAMS['plot_params'][PARAMS['plot_type']]['n_steps']

    data = []

    for hp in range(len(hyperparameters)):
        medians = []
        maxs = []
        mins = []

        cum_rewards = hyper_cum_rewards[hp]

        xs = range(len(cum_rewards[0]))
        for n in xs:
            scores = [s[n] for s in cum_rewards]
            maxs.append(max(scores))
            mins.append(min(scores))
            medians.append(median(scores))

        mid = go.Scattergl(x=xs, y=medians, mode='lines', name='median-({})'.format(hyperparameters[hp]))

        bounds = go.Scattergl(
            x=xs+xs[::-1],
            y=maxs+mins[::-1],
            fill='tozerox',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False,
            name='bounds-({})'.format(hyperparameters[hp]),
        )
        
        data.append(mid)
        data.append(bounds)

    adversaries = "Comparative"

    layout = {"title": "{} Player on {}x{} Board (bonus: {}, penalty: {})" \
                .format(adversaries, PARAMS['board_size'], PARAMS['board_size'], bonus, penalty), 
              "xaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['plot_x_name']}, 
              "yaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['metric']}}

    write_plot(adversaries, data, layout)


