from .utils.baseAgent import BaseAgent

from utils.constants import DECK, INT2CARD, CARD2INT, COLORS
from numpy.random import choice

class GreedyAgent(BaseAgent):
  def __init__(self):
    super().__init__()

  def get_action(self, state, possible_actions):
    return possible_actions[0], choice(4)
    
class GreedierAgent(BaseAgent):
  def __init__(self):
    super().__init__()

  def get_action(self, state, possible_actions):

    if possible_actions[0] % 13 == 12 and len(possible_actions) != 1:
      return possible_actions[1], choice(4)

    return possible_actions[0], choice(4)