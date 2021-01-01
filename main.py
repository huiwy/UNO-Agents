from os import times
from agents import *
from agents.utils import mcts
import game
import numpy as np
a1 = MCTSAgent(5, 100)
a2 = GreedyAgent()

import time
t=time.time()
o = np.zeros(100)
for i in range(100):
  g = game.UNO([a1, a2], "fin", False, False)
  o[i] = game.play(g)
  print("finished one")
print(o)
print(time.time()-t)
