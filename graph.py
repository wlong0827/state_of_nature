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
    n_steps = PARAMS['plot_params']['box_n_steps']['no_hp_runs']
    bin_size = int(n_steps * PARAMS['plot_params']['learning_curve']['sample_rate'])

    for i, hyp in enumerate(range(0, n_steps, bin_size)):
        if PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Average Score per Move':
            data.append(go.Box(y = hyper_scores_avg[i], name=hyp))
            mids.append(median(hyper_scores_avg[i]))
        elif PARAMS['plot_params'][PARAMS['plot_type']]['metric'] == 'Percent Invasions of Total Moves':
            data.append(go.Box(y = hyper_invasions_pct[i], name=hyp))
            mids.append(median(hyper_invasions_pct[i]))

    data.append(go.Scatter(x = hyperparameters, y = mids, mode = 'markers', name='median'))

    adversaries = " vs ".join(player_types).replace('Q-Learning', 'QL').replace('Random', 'R')

    layout = {"title": "{} Player on {}x{} Board (bonus: {}, penalty: {})" \
                .format(adversaries, PARAMS['board_size'], PARAMS['board_size'], bonus, penalty), 
              "xaxis": {"title": "{}: {}".format(PARAMS['plot_params'][PARAMS['plot_type']]['plot_x_name'], hyperparameters)}, 
              "yaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['metric']}}

    write_plot(adversaries, data, layout)

def write_line_plot(PARAMS, hyperparameters, player_types, hyper_data):

    bonus = PARAMS['plot_params'][PARAMS['plot_type']]['invade_bonus']
    penalty = PARAMS['plot_params'][PARAMS['plot_type']]['invaded_penalty']
    n_steps = PARAMS['plot_params'][PARAMS['plot_type']]['n_steps']
    bin_size = int(n_steps * PARAMS['plot_params']['learning_curve']['sample_rate'])

    data = []

    for hp in range(len(hyperparameters)):
        medians = []
        maxs = []
        mins = []
        xs = range(0, n_steps, bin_size)

        cum_data = hyper_data[hp]

        for i, n in enumerate(xs):
            metric = [s[i] for s in cum_data]
            maxs.append(max(metric))
            mins.append(min(metric))
            medians.append(median(metric))

        mid = go.Scattergl(x=xs, y=medians, mode='lines', name='{}'.format(hyperparameters[hp]))

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

def write_stack_plot(PARAMS, hyperparameters, player_types, cum_actions):

    bonus = PARAMS['plot_params'][PARAMS['plot_type']]['invade_bonus']
    penalty = PARAMS['plot_params'][PARAMS['plot_type']]['invaded_penalty']
    n_steps = PARAMS['plot_params'][PARAMS['plot_type']]['n_steps']
    bin_size = int(n_steps * PARAMS['plot_params']['learning_curve']['sample_rate'])

    data = []
    xs = range(0, n_steps, bin_size)

    actions = cum_actions.keys()
    actions.insert(0, actions.pop(actions.index('defer')))
    actions.insert(0, actions.pop(actions.index('stay')))

    for act in actions:
        y = cum_actions[act]
        data.append(dict(
            x=xs,
            y=y,
            hoverinfo='x+y',
            mode='lines',
            name=act,
            stackgroup='one'
        ))

    adversaries = PARAMS['plot_params'][PARAMS['plot_type']]['no_hp_runs'][0]

    layout = {"title": "{} Player on {}x{} Board (bonus: {}, penalty: {})" \
                .format(adversaries, PARAMS['board_size'], PARAMS['board_size'], bonus, penalty), 
              "xaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['plot_x_name']}, 
              "yaxis": {"title": PARAMS['plot_params'][PARAMS['plot_type']]['metric']}}

    write_plot(adversaries, data, layout)


