from numpy.lib.function_base import place
from utils.constants import TUPLEACT2INT, INTACT2TUPLE
from game import *
from agents.greedyAgent import GreedyAgent

from copy import deepcopy
import numpy as np
import math

c = 5

class MCTSNode:
  def __init__(self, a, parent, id):
    self.action = a
    self.visited_times = 0
    self.value = 0
    self.parent = parent
    self.id = id
    self.children = []

    if a == 60:
      self.value = -10
      self.visited_times = 5

  def UCBscore(self, t):
    if self.visited_times == 0:
      return float("inf")
    return self.value + c*(math.log(t) / self.visited_times)**0.5

  def select(self, game, t):
    valid_actions = game.get_valid_actions()
    valid_actions = set((TUPLEACT2INT[(a, i)] for i in range(4) for a in valid_actions))
    valid_children = [self.children[a] for a in valid_actions]

    selected = max(valid_children, key=lambda x: x.UCBscore(t))
    
    reward = till_next_turn(game, INTACT2TUPLE[selected.action], self.id)
  
    if reward == 1:
      self.backprop(1)
    elif reward == -1:
      self.backprop(-1)

    if len(selected.children) == 0:
      selected.expand(game)
    else:
      selected.select(game, t)

  def expand(self, game):
    if len(self.children) == 0:
      for i in range(61):
        self.children.append(MCTSNode(i, self, self.id))

    game.agents[self.id] = GreedyAgent()
    result = (play(game) == self.id)
    
    result = result*2-1
    self.backprop(result)

  def backprop(self, result):
    self.visited_times += 1
    self.update(result)
    if self.parent == None:
      return
    self.parent.backprop(result)

  def update(self, value):
    self.value = self.value + (value - self.value) / (self.visited_times)

class MCTS:
  def __init__(self, game, id):
    self.game = deepcopy(game)
    self.root = MCTSNode(game, None, id)
    self.root.expand(deepcopy(game))

    valid_actions = game.get_valid_actions()
    valid_actions = set((TUPLEACT2INT[(a, i)] for i in range(4) for a in valid_actions))
    valid_children = [self.root.children[a] for a in valid_actions]

    for child in self.root.children:
      if not child in valid_children:
        child.value = float("-inf")

  def search(self, iterations):
    for t in range(1, iterations+1):
      shuffle(self.game.deck)
      self.root.select(deepcopy(self.game), t)

    return np.array([s.value for s in self.root.children])

def till_next_turn(game, action, id):
  if not game.apply_action(action):
    return 0
  if game.current_win():
    return 1

  game.next_player()
  game.penalize()
  
  while game.current_player != id:
    while True:
      action = game.get_action()
      if game.apply_action(action):
        break
    if game.current_win():
      return -1
    game.next_player()
    game.penalize()