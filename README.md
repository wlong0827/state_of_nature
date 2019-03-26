# Escaping the State of Nature
Thesis Project 2018-2019 Code: Escaping the State of Nature

## Game

![State of Nature SSD](https://raw.githubusercontent.com/wlong0827/state_of_nature/master/assets/civ_game.png)

Players capture territory in a gridlike environment and can choose to cultivate their land or invade other players' territory for some bonus reward, but also accrue penalties when being invaded themselves.

## Install Instructions

1. Download the primary dependencies with
```
pip install -r requirements.txt
```
2. Set the desired game parameters in `params.py` and then run trials with 
```
python state_of_nature.py Q Q -3 Q -4 Q -s 4 -t 3 -hp -w 
```
You'll need to login with a plot.ly account to write graphs

3. Find matrix game Q-networks in `assets/` with
```
python play_matrix_game.py
```

## Initial Findings:

### Q-Learning in naive settings 
Q-Learning vs Q-Learning Average Score

![avg_score](https://github.com/wlong0827/state_of_nature/blob/master/assets/avg_score.png)

Q-Learnning vs Q-Learning Percent Invasions

![pct_invades](https://github.com/wlong0827/state_of_nature/blob/master/assets/pct_invade.png)

Q-Learning vs HQ-Learning Collective Score

![learning_curve](https://github.com/wlong0827/state_of_nature/blob/master/assets/collective_score.png)

Q-Learning vs HQ-Learning Action Breakdown

![ql_actions](https://github.com/wlong0827/state_of_nature/blob/master/assets/q_breakdown.png)
![lola_actions](https://github.com/wlong0827/state_of_nature/blob/master/assets/hq_breakdown.png)

Comparative Collective Invasions

![invasions](https://github.com/wlong0827/state_of_nature/blob/master/assets/collective_invasions.png)

Comparative Successful Defers

![defers](https://github.com/wlong0827/state_of_nature/blob/master/assets/collective_defers.png)

### Social Dilemma Matrix Game

|   |               C              |               D              |
|---|:----------------------------:|:----------------------------:|
| C | (R = 0.459, R = 0.459) | (S = 0.426, T = 0.446)   |
| D | (T = 0.446, S = 0.426)   | (P = 0.455, P = 0.455) |
 
Criteria: 
1. R > P
2. R > S
3. 2R > T + S
4. T > R or P > S

Fear = P - S (+0.029), Greed = T - R (-0.013)

If both Fear and Greed exist in the Civilization Game social dilemma, it represents a Prisoner's Dilemma matrix game. If just Fear, then a Stag Hunt. 

![matrix](https://github.com/wlong0827/state_of_nature/blob/master/assets/matrix.png)


