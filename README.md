# Escaping the State of Nature
Thesis Project 2018-2019 Code: Escaping the State of Nature

## Game

![State of Nature SSD](https://raw.githubusercontent.com/wlong0827/state_of_nature/master/game.png)

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

![ql](https://github.com/wlong0827/state_of_nature/blob/master/assets/random.png)

Q-Learning vs Q-Learning Invasions per Turn

![ql](https://github.com/wlong0827/state_of_nature/blob/master/assets/pct_invade.png)

Q-Learning vs Q-Learning Average Score per Turn

![ql](https://github.com/wlong0827/state_of_nature/blob/master/assets/avg_score.png)
