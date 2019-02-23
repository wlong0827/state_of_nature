PARAMS = {
        'plot_type': 'learning_curve',
        'board_size': 0,
        'plot_params': {
            'box_n_steps': {
                'metric': 'Average Score per Move',
                'hyperparameters': [500, 1000, 5000, 10000, 25000, 50000, 100000],
                'no_hp_runs': 100000,
                'invade_bonus': 10,
                'invaded_penalty': -20,
                'farming': True,
                'plot_x_name': 'Average Score per Move',
            },
            'scatter_penalty': {
                'hyperparameters': [-1,-2],
                'no_hp_runs': -2,
                'n_steps': 10000,
                'invade_bonus': 10,
                'farming': True,
                'metric': 'Average Score per Move',
                'plot_x_name': 'Average Score per Move',
            },
            'learning_curve': {
                'hyperparameters': [
                    ['Q-Learning', 'Q-Learning', 'Q-Learning', 'Q-Learning'], 
                    ['Random', 'Random', 'Random', 'Random'],
                ],
                'no_hp_runs': ['Q-Learning', 'Q-Learning'],
                'n_steps': 500000,
                'sample_rate': 0.01,
                'invade_bonus': 10,
                'invaded_penalty': -20,
                'farming': True,
                'plot_x_name': 'Number of Game Steps',
                'metric': 'Collective Score',
            },
        }
    }