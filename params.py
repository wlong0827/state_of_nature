PARAMS = {
    'plot_type': 'action_breakdown',
    'plot_params': {
        'box_n_steps': {
            'metric': 'Percent Invasions of Total Moves',
            'hyperparameters': [500, 1000, 5000, 10000, 25000, 50000, 100000],
            'no_hp_runs': 100000,
            'invade_bonus': 10,
            'invaded_penalty': -20,
            'farming': True,
            'plot_x_name': 'Average Score per Move',
        },
        'scatter_penalty': {
            'hyperparameters': [-1,-1.5, -2, -2.5],
            'no_hp_runs': -2,
            'n_steps': 100000,
            'invade_bonus': 10,
            'sample_rate': 0.01,
            'farming': True,
            'metric': 'Average Score per Move',
            'plot_x_name': 'Average Score per Move',
        },
        'learning_curve': {
            'hyperparameters': [
                ['LOLA', 'LOLA', 'LOLA', 'LOLA'], 
                ['Q-Learning', 'Q-Learning', 'Q-Learning', 'Q-Learning'], 
                ['Random', 'Random', 'Random', 'Random'],
            ],
            'no_hp_runs': ['LOLA', 'LOLA', 'LOLA', 'LOLA'],
            'n_steps': 250000,
            'sample_rate': 0.01,
            'invade_bonus': 10,
            'invaded_penalty': -25,
            'farming': True,
            'plot_x_name': 'Number of Game Steps',
            'metric': 'Collective Score',
        },
        'action_breakdown': {
            'no_hp_runs': ['Q-Learning', 'Q-Learning', 'Q-Learning', 'Q-Learning'],
            'n_steps': 250000,
            'sample_rate': 0.01,
            'invade_bonus': 10,
            'invaded_penalty': -25,
            'farming': True,
            'plot_x_name': 'Number of Actions',
            'metric': 'Action Breakdown',
        },
    }
}