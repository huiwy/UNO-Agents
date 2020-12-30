import numpy as np
import pickle
from game import UNO

from agents.greedyAgent import GreedyAgent

all_actions = []
all_prev = []
all_hands = []

agent_1 = GreedyAgent()
agent_2 = GreedyAgent()

for i in range(10000):
  action_list = [[],[]]
  hands_list = [[],[]]
  prev_list = [[],[]]

  uno = UNO([agent_1, agent_2], "finite_deck", forced_draw_only=False)
  while True:
    while True:
      action = uno.get_action()
      current_player = uno.current_player
      hands_list[current_player].append(uno.hands[current_player].copy())
      prev_list[current_player].append(uno.previous_card)
      action_list[current_player].append(action)
      if uno.apply_action(action):
        break
    if uno.current_win():
      winner = uno.current_player
      break
    uno.next_player()
    uno.penalize()
  all_actions.append(action_list[0])
  all_actions.append(action_list[1])
  all_prev.append(prev_list[0])
  all_prev.append(prev_list[1])
  all_hands.append(hands_list[0])
  all_hands.append(hands_list[1])

with open('hands.pkl','wb') as f:
  pickle.dump(all_hands, f)

with open('prev.pkl','wb') as f:
  pickle.dump(all_prev, f)

with open('actions.pkl','wb') as f:
  pickle.dump(all_actions, f)

