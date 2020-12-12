from .utils.baseAgent import BaseAgent

from .constants import DECK, INT2CARD, CARD2INT, COLORS
from numpy.random import choice

class RandomAgent(BaseAgent):
  def __init__(self, name='RandomAgent'):
    super().__init__()
    self.name = name

  def get_action(self, state, possible_actions):
    return choice(possible_actions), choice(4)