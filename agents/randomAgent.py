from .utils.baseAgent import BaseAgent

from .constants import DECK, INT2CARD, CARD2INT, COLORS
from numpy.random import choice

class RandomAgent(BaseAgent):
  def __init__(self):
    super().__init__()

  def get_action(self, state, possible_actions):
    return choice(len(possible_actions)), choice(4)