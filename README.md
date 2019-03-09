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
2. Run trials with 
```
python state_of_nature.py 
```

## Initial Findings:

Q-Learning vs Lateral Agent

![ql](https://github.com/wlong0827/state_of_nature/blob/master/assets/ql.png)

Random vs Lateral Agent

![random](https://github.com/wlong0827/state_of_nature/blob/master/assets/random.png)

Q-Learning vs Q-Learning Invasions per Turn

![pct_invade](https://github.com/wlong0827/state_of_nature/blob/master/assets/pct_invade.png)

Q-Learning vs Q-Learning Average Score per Turn

![avg_score](https://github.com/wlong0827/state_of_nature/blob/master/assets/avg_score.png)

### Social Dilemma Matrix Game

   C                                        D

C  (R = 0.458575, R = 0.458575)   (S = 0.42601,  T = 0.48632)

D  (T = 0.48632,  S = 0.42601)    (P = 0.455065, P = 0.455065)
 
Criteria R > P, R > S, 2R > T + S, T > R or P > S
Fear = P - S (0.029055 is >0), Greed = T - R (0.027745 is >0)
Both Fear and Greed exist in the Civilization Game social dilemma, consequently, it represents a Prisoner's Dilemma matrix game


