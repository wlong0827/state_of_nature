# Escaping the State of Nature
Thesis Project 2018-2019 Code: Escaping the State of Nature

## Game

![State of Nature SSD](https://raw.githubusercontent.com/wlong0827/state_of_nature/master/assets/game.png)

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

Q-Learning vs Q-Learning Average Score

![avg_score](https://github.com/wlong0827/state_of_nature/blob/master/assets/avg_score.png)

Q-Learning vs LOLA Collective Score

![learning_curve](https://github.com/wlong0827/state_of_nature/blob/master/assets/learning_curve.png)

### Social Dilemma Matrix Game

|   |               C              |               D              |
|---|:----------------------------:|:----------------------------:|
| C | (R = 0.458575, R = 0.458575) | (S = 0.42601, T = 0.48632)   |
| D | (T = 0.48632, S = 0.42601)   | (P = 0.455065, P = 0.455065) |
 
Criteria R > P, R > S, 2R > T + S, T > R or P > S
Fear = P - S (+0.029055), Greed = T - R (+0.027745)

Both Fear and Greed exist in the Civilization Game social dilemma, consequently, it represents a Prisoner's Dilemma matrix game


