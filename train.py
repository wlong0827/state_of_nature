from deep_q_learning import *
from atari import *
from action_getter import *
from replay_memory import *

import tensorflow as tf

TRAIN = True
TEST = False

def train():
    """Contains the training and evaluation loops"""
    my_replay_memory = ReplayMemory(size=MEMORY_SIZE, batch_size=BS)
    network_updater = TargetNetworkUpdater(MAIN_DQN_VARS, TARGET_DQN_VARS)
    action_getter = ActionGetter(atari.env.action_space.n, 
                                 replay_memory_start_size=REPLAY_MEMORY_START_SIZE, 
                                 max_frames=MAX_FRAMES)

    with tf.Session() as sess:
        sess.run(init)
        
        frame_number = 0
        rewards = []
        loss_list = []
        
        while frame_number < MAX_FRAMES:
            
            ########################
            ####### Training #######
            ########################
            epoch_frame = 0
            while epoch_frame < EVAL_FREQUENCY:
                terminal_life_lost = atari.reset(sess)
                episode_reward_sum = 0
                for _ in range(MAX_EPISODE_LENGTH):
                    
                    action = action_getter.get_action(sess, frame_number, atari.state, MAIN_DQN)   
                    
                    processed_new_frame, reward, terminal, terminal_life_lost, _ = atari.step(sess, action)  
                    frame_number += 1
                    epoch_frame += 1
                    episode_reward_sum += reward
                    
                    my_replay_memory.add_experience(action=action, 
                                                    frame=processed_new_frame[:, :, 0],
                                                    reward=reward, 
                                                    terminal=terminal_life_lost)   
                    
                    if frame_number % UPDATE_FREQ == 0 and frame_number > REPLAY_MEMORY_START_SIZE:
                        loss = learn(sess, my_replay_memory, MAIN_DQN, TARGET_DQN,
                                     BS, gamma = DISCOUNT_FACTOR)
                        loss_list.append(loss)
                    if frame_number % NETW_UPDATE_FREQ == 0 and frame_number > REPLAY_MEMORY_START_SIZE:
                        network_updater.update_networks(sess)
                    
                    if terminal:
                        terminal = False
                        break

                rewards.append(episode_reward_sum)
                
                # Output the progress:
                if len(rewards) % 10 == 0:
                    # Scalar summaries for tensorboard
                    if frame_number > REPLAY_MEMORY_START_SIZE:
                        summ = sess.run(PERFORMANCE_SUMMARIES, 
                                        feed_dict={LOSS_PH:np.mean(loss_list), 
                                                   REWARD_PH:np.mean(rewards[-100:])})
                        
                        SUMM_WRITER.add_summary(summ, frame_number)
                        loss_list = []
                    # Histogramm summaries for tensorboard
                    summ_param = sess.run(PARAM_SUMMARIES)
                    SUMM_WRITER.add_summary(summ_param, frame_number)
                    
                    print(len(rewards), frame_number, np.mean(rewards[-100:]))
                    with open('rewards.dat', 'a') as reward_file:
                        print(len(rewards), frame_number, np.mean(rewards[-100:]), file=reward_file)
            
            ########################
            ###### Evaluation ######
            ########################
            terminal = True
            gif = True
            frames_for_gif = []
            eval_rewards = []
            evaluate_frame_number = 0
            
            for _ in range(EVAL_STEPS):
                if terminal:
                    terminal_life_lost = atari.reset(sess, evaluation=True)
                    episode_reward_sum = 0
                    terminal = False
               
                # Fire (action 1), when a life was lost or the game just started, 
                # so that the agent does not stand around doing nothing. When playing 
                # with other environments, you might want to change this...
                action = 1 if terminal_life_lost else action_getter.get_action(sess, frame_number,
                                                                               atari.state, 
                                                                               MAIN_DQN,
                                                                               evaluation=True)
                processed_new_frame, reward, terminal, terminal_life_lost, new_frame = atari.step(sess, action)
                evaluate_frame_number += 1
                episode_reward_sum += reward

                if gif: 
                    frames_for_gif.append(new_frame)
                if terminal:
                    eval_rewards.append(episode_reward_sum)
                    gif = False # Save only the first game of the evaluation as a gif
                     
            print("Evaluation score:\n", np.mean(eval_rewards))       
            try:
                generate_gif(frame_number, frames_for_gif, eval_rewards[0], PATH)
            except IndexError:
                print("No evaluation game finished")
            
            #Save the network parameters
            saver.save(sess, PATH+'/my_model', global_step=frame_number)
            frames_for_gif = []
            
            # Show the evaluation score in tensorboard
            summ = sess.run(EVAL_SCORE_SUMMARY, feed_dict={EVAL_SCORE_PH:np.mean(eval_rewards)})
            SUMM_WRITER.add_summary(summ, frame_number)
            with open('rewardsEval.dat', 'a') as eval_reward_file:
                print(frame_number, np.mean(eval_rewards), file=eval_reward_file)

if TRAIN:
    train()

if TEST:
    
    gif_path = "GIF/"
    os.makedirs(gif_path,exist_ok=True)

    if ENV_NAME == 'BreakoutDeterministic-v4':
        trained_path = "trained/breakout/"
        save_file = "my_model-15845555.meta"
    
    elif ENV_NAME == 'PongDeterministic-v4':
        trained_path = "trained/pong/"
        save_file = "my_model-3217770.meta"

    action_getter = ActionGetter(atari.env.action_space.n, 
                                 replay_memory_start_size=REPLAY_MEMORY_START_SIZE, 
                                 max_frames=MAX_FRAMES)
    
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(trained_path+save_file)
        saver.restore(sess,tf.train.latest_checkpoint(trained_path))
        frames_for_gif = []
        terminal_live_lost = atari.reset(sess, evaluation = True)
        episode_reward_sum = 0
        while True:
            atari.env.render()
            action = 1 if terminal_live_lost else action_getter.get_action(sess, 0, atari.state, 
                                                                           MAIN_DQN, 
                                                                           evaluation = True)
            processed_new_frame, reward, terminal, terminal_live_lost, new_frame = atari.step(sess, action)
            episode_reward_sum += reward
            frames_for_gif.append(new_frame)
            if terminal == True:
                break
        
        atari.env.close()
        print("The total reward is {}".format(episode_reward_sum))
        print("Creating gif...")
        generate_gif(0, frames_for_gif, episode_reward_sum, gif_path)
        print("Gif created, check the folder {}".format(gif_path))
