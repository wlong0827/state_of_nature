from collections import defaultdict
import json

f = open("q_network.json")
q_str = f.read()
q_table = json.loads(q_str)

formatted_q_table = defaultdict(list)

for key in q_table.keys():
	state = key.split("-")[0][1:-1].split(",")
	if state[-1] == " 0":
		state = "".join(state[:-3])
		formatted_q_table[state].append((key[1], q_table[key]))

print len(formatted_q_table)

state_values = defaultdict(list)
for key in formatted_q_table.keys():
	state = key.split(" ")
	state_values[state.index("'P0'")] += formatted_q_table[key]

for key in state_values.keys():
	state_values[key] = max(state_values[key])

state_values = [(val[0], round(val[1], 4)) for val in state_values.values()]

string = ""
for i in range(3):
	start = i * 3
	end = start + 3
	string += str(state_values[start:end]) + "\n"

print string