import numpy as np
import copy
from random import shuffle
from utils import constants

def initialize_deck(current_hand, shuff = True):
  deck = [constants.CARD2INT[c] for c in constants.DECK]
  shuffle(deck)
  for i in range(len(current_hand)):
    for _ in range(current_hand[i]):
      deck.remove(i)

  # print(deck)
  # print(current_hand)
  return deck
