import tensorflow as tf
import imageio
from skimage.transform import resize

class DQN:
    """Implements a Deep Q Network"""
    
    # pylint: disable=too-many-instance-attributes
    
    def __init__(self, n_actions, hidden=1024, learning_rate=0.00001, 
                 frame_height=84, frame_width=84, agent_history_length=4):
        """
        Args:
            n_actions: Integer, number of possible actions
            hidden: Integer, Number of filters in the final convolutional layer. 
                    This is different from the DeepMind implementation
            learning_rate: Float, Learning rate for the Adam optimizer
            frame_height: Integer, Height of a frame of an Atari game
            frame_width: Integer, Width of a frame of an Atari game
            agent_history_length: Integer, Number of frames stacked together to create a state
        """
        self.n_actions = n_actions
        self.hidden = hidden
        self.learning_rate = learning_rate
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.agent_history_length = agent_history_length
        
        self.input = tf.placeholder(shape=[None, self.frame_height, 
                                           self.frame_width, self.agent_history_length], 
                                    dtype=tf.float32)
        # Normalizing the input
        self.inputscaled = self.input/255
        
        # Convolutional layers
        self.conv1 = tf.layers.conv2d(
            inputs=self.inputscaled, filters=32, kernel_size=[8, 8], strides=4,
            kernel_initializer=tf.variance_scaling_initializer(scale=2),
            padding="valid", activation=tf.nn.relu, use_bias=False, name='conv1')
        self.conv2 = tf.layers.conv2d(
            inputs=self.conv1, filters=64, kernel_size=[4, 4], strides=2, 
            kernel_initializer=tf.variance_scaling_initializer(scale=2),
            padding="valid", activation=tf.nn.relu, use_bias=False, name='conv2')
        self.conv3 = tf.layers.conv2d(
            inputs=self.conv2, filters=64, kernel_size=[3, 3], strides=1, 
            kernel_initializer=tf.variance_scaling_initializer(scale=2),
            padding="valid", activation=tf.nn.relu, use_bias=False, name='conv3')
        self.conv4 = tf.layers.conv2d(
            inputs=self.conv3, filters=hidden, kernel_size=[7, 7], strides=1, 
            kernel_initializer=tf.variance_scaling_initializer(scale=2),
            padding="valid", activation=tf.nn.relu, use_bias=False, name='conv4')
        
        # Splitting into value and advantage stream
        self.valuestream, self.advantagestream = tf.split(self.conv4, 2, 3)
        self.valuestream = tf.layers.flatten(self.valuestream)
        self.advantagestream = tf.layers.flatten(self.advantagestream)
        self.advantage = tf.layers.dense(
            inputs=self.advantagestream, units=self.n_actions,
            kernel_initializer=tf.variance_scaling_initializer(scale=2), name="advantage")
        self.value = tf.layers.dense(
            inputs=self.valuestream, units=1, 
            kernel_initializer=tf.variance_scaling_initializer(scale=2), name='value')
        
        # Combining value and advantage into Q-values as described above
        self.q_values = self.value + tf.subtract(self.advantage, tf.reduce_mean(self.advantage, axis=1, keepdims=True))
        self.best_action = tf.argmax(self.q_values, 1)
        
        # The next lines perform the parameter update. This will be explained in detail later.
        
        # targetQ according to Bellman equation: 
        # Q = r + gamma*max Q', calculated in the function learn()
        self.target_q = tf.placeholder(shape=[None], dtype=tf.float32)
        # Action that was performed
        self.action = tf.placeholder(shape=[None], dtype=tf.int32)
        # Q value of the action that was performed
        self.Q = tf.reduce_sum(tf.multiply(self.q_values, tf.one_hot(self.action, self.n_actions, dtype=tf.float32)), axis=1)
        
        # Parameter updates
        self.loss = tf.reduce_mean(tf.losses.huber_loss(labels=self.target_q, predictions=self.Q))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
        self.update = self.optimizer.minimize(self.loss)

class TargetNetworkUpdater:
    """Copies the parameters of the main DQN to the target DQN"""
    def __init__(self, main_dqn_vars, target_dqn_vars):
        """
        Args:
            main_dqn_vars: A list of tensorflow variables belonging to the main DQN network
            target_dqn_vars: A list of tensorflow variables belonging to the target DQN network
        """
        self.main_dqn_vars = main_dqn_vars
        self.target_dqn_vars = target_dqn_vars

    def _update_target_vars(self):
        update_ops = []
        for i, var in enumerate(self.main_dqn_vars):
            copy_op = self.target_dqn_vars[i].assign(var.value())
            update_ops.append(copy_op)
        return update_ops
            
    def update_networks(self, sess):
        """
        Args:
            sess: A Tensorflow session object
        Assigns the values of the parameters of the main network to the 
        parameters of the target network
        """
        update_ops = self._update_target_vars()
        for copy_op in update_ops:
            sess.run(copy_op)

def learn(session, replay_memory, main_dqn, target_dqn, batch_size, gamma):
    """
    Args:
        session: A tensorflow sesson object
        replay_memory: A ReplayMemory object
        main_dqn: A DQN object
        target_dqn: A DQN object
        batch_size: Integer, Batch size
        gamma: Float, discount factor for the Bellman equation
    Returns:
        loss: The loss of the minibatch, for tensorboard
    Draws a minibatch from the replay memory, calculates the 
    target Q-value that the prediction Q-value is regressed to. 
    Then a parameter update is performed on the main DQN.
    """
    # Draw a minibatch from the replay memory
    states, actions, rewards, new_states, terminal_flags = replay_memory.get_minibatch()    
    # The main network estimates which action is best (in the next 
    # state s', new_states is passed!) 
    # for every transition in the minibatch
    arg_q_max = session.run(main_dqn.best_action, feed_dict={main_dqn.input:new_states})
    # The target network estimates the Q-values (in the next state s', new_states is passed!) 
    # for every transition in the minibatch
    q_vals = session.run(target_dqn.q_values, feed_dict={target_dqn.input:new_states})
    double_q = q_vals[range(batch_size), arg_q_max]
    # Bellman equation. Multiplication with (1-terminal_flags) makes sure that 
    # if the game is over, targetQ=rewards
    target_q = rewards + (gamma*double_q * (1-terminal_flags))
    # Gradient descend step to update the parameters of the main network
    loss, _ = session.run([main_dqn.loss, main_dqn.update], 
                          feed_dict={main_dqn.input:states, 
                                     main_dqn.target_q:target_q, 
                                     main_dqn.action:actions})
    return loss

class ProcessFrame:
    """Resizes and converts RGB Atari frames to grayscale"""
    def __init__(self, frame_height=84, frame_width=84):
        """
        Args:
            frame_height: Integer, Height of a frame of an Atari game
            frame_width: Integer, Width of a frame of an Atari game
        """
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.frame = tf.placeholder(shape=[210, 160, 3], dtype=tf.uint8)
        self.processed = tf.image.rgb_to_grayscale(self.frame)
        self.processed = tf.image.crop_to_bounding_box(self.processed, 34, 0, 160, 160)
        self.processed = tf.image.resize_images(self.processed, 
                                                [self.frame_height, self.frame_width], 
                                                method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    
    def process(self, session, frame):
        """
        Args:
            session: A Tensorflow session object
            frame: A (210, 160, 3) frame of an Atari game in RGB
        Returns:
            A processed (84, 84, 1) frame in grayscale
        """
        return session.run(self.processed, feed_dict={self.frame:frame})

def generate_gif(frame_number, frames_for_gif, reward, path):
    """
        Args:
            frame_number: Integer, determining the number of the current frame
            frames_for_gif: A sequence of (210, 160, 3) frames of an Atari game in RGB
            reward: Integer, Total reward of the episode that es ouputted as a gif
            path: String, path where gif is saved
    """
    for idx, frame_idx in enumerate(frames_for_gif): 
        frames_for_gif[idx] = resize(frame_idx, (420, 320, 3), 
                                     preserve_range=True, order=0).astype(np.uint8)
        
    imageio.mimsave(f'{path}{"ATARI_frame_{0}_reward_{1}.gif".format(frame_number, reward)}', 
                    frames_for_gif, duration=1/30)