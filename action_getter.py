import numpy as np

class ActionGetter:
    """Determines an action according to an epsilon greedy strategy with annealing epsilon"""
    def __init__(self, n_actions, eps_initial=1, eps_final=0.1, eps_final_frame=0.01, 
                 eps_evaluation=0.0, eps_annealing_frames=1000000, 
                 replay_memory_start_size=50000, max_frames=25000000):
        """
        Args:
            n_actions: Integer, number of possible actions
            eps_initial: Float, Exploration probability for the first 
                replay_memory_start_size frames
            eps_final: Float, Exploration probability after 
                replay_memory_start_size + eps_annealing_frames frames
            eps_final_frame: Float, Exploration probability after max_frames frames
            eps_evaluation: Float, Exploration probability during evaluation
            eps_annealing_frames: Int, Number of frames over which the 
                exploration probabilty is annealed from eps_initial to eps_final
            replay_memory_start_size: Integer, Number of frames during 
                which the agent only explores
            max_frames: Integer, Total number of frames shown to the agent
        """
        self.n_actions = n_actions
        self.eps_initial = eps_initial
        self.eps_final = eps_final
        self.eps_final_frame = eps_final_frame
        self.eps_evaluation = eps_evaluation
        self.eps_annealing_frames = eps_annealing_frames
        self.replay_memory_start_size = replay_memory_start_size
        self.max_frames = max_frames
        
        # Slopes and intercepts for exploration decrease
        self.slope = -(self.eps_initial - self.eps_final)/self.eps_annealing_frames
        self.intercept = self.eps_initial - self.slope*self.replay_memory_start_size
        self.slope_2 = -(self.eps_final - self.eps_final_frame)/(self.max_frames - self.eps_annealing_frames - self.replay_memory_start_size)
        self.intercept_2 = self.eps_final_frame - self.slope_2*self.max_frames

    def get_action(self, session, frame_number, state, main_dqn, evaluation=False):
        """
        Args:
            session: A tensorflow session object
            frame_number: Integer, number of the current frame
            state: A (84, 84, 4) sequence of frames of an Atari game in grayscale
            main_dqn: A DQN object
            evaluation: A boolean saying whether the agent is being evaluated
        Returns:
            An integer between 0 and n_actions - 1 determining the action the agent perfoms next
        """
        if evaluation:
            eps = self.eps_evaluation
        elif frame_number < self.replay_memory_start_size:
            eps = self.eps_initial
        elif frame_number >= self.replay_memory_start_size and frame_number < self.replay_memory_start_size + self.eps_annealing_frames:
            eps = self.slope*frame_number + self.intercept
        elif frame_number >= self.replay_memory_start_size + self.eps_annealing_frames:
            eps = self.slope_2*frame_number + self.intercept_2
        
        if np.random.rand(1) < eps:
            return np.random.randint(0, self.n_actions)
        return session.run(main_dqn.best_action, feed_dict={main_dqn.input:[state]})[0]