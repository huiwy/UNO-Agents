from agents.dqnAgent import DQNAgent
from agents.expectimaxAgent import ExpectimaxAgent
from os import times
from agents import *
from agents.utils import mcts
import game
import numpy as np
# a1 = ExpectimaxAgent()
# a2 = RandomAgent()

a1 = DQNAgent(10000, 54*5, [512, 512], 55, 2, 0.1, "cuda")
# a2 = GreedyAgent()
# import time
# t=time.time()
# o = np.zeros(1000)
# for i in range(1000):
#   g = game.UNO([a2, a1], "fin", False, False)
#   o[i] = game.play(g)
#   if i == 20:
#     print('win rate in 10', o.mean() * 50)
#   elif i == 100:
#     print('win rate in 100', o.mean()*10)
#   elif i == 300:
#     print('win rate in 300', o.mean()*3.33)
#   elif i == 500:
#     print('win rate in 500', o.mean()*2)

# print(o.mean())
# print(o)
# print(time.time()-t)
# a1.toexploit()

# for i in range(500):
#   g = game.UNO([a2, a1], "fin", False, False)
#   o[i] = game.play(g)
# print('win rate:', o[:500].mean())



# a1 = MCTSAgent(5, 100)
a1.load()
a1.toexploit()
a2 = RandomAgent()
o = np.zeros(200)
for i in range(200):
  g = game.UNO([a1, a2, a2, a2], "fin", False, False)
  o[i] = game.play(g)
  print(o[i])
print((o==0).mean())