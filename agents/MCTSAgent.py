from random import choice
from utils.constants import INT2CARD
from agents.utils.baseAgent import BaseAgent
import numpy as np
from utils import util
from utils.util import *
from copy import copy, deepcopy


class OpponentSimulator:
  def __init__(self, current_hand, num_opponent):
    deck = util.initialize_deck(current_hand, True)
    self.opponents = [Opponent(deck) for _ in range(num_opponent)]

  def do_action(self, action, valid, visible_cards, draw):
    deck = util.initialize_deck(visible_cards, True)
    weights = np.zeros(len(self.opponents))

    # m = 0

    for i, o in enumerate(self.opponents):
      w = o.do_action(action, valid, deck, draw)
      weights[i] = w
    #   if w > m:
    #     mo = o
    #     m = w

    weights /= weights.sum()

    # print(m)
    # print(mo)

    self.weights = weights

    self.resample(weights)

  def resample(self, weights):
    samples = np.random.choice(len(self.opponents), len(self.opponents), p=weights)
    new_opponents = [deepcopy(self.opponents[i]) for i in samples]

    self.opponents = new_opponents
    self.weights = [self.weights[i] for i in samples]

    for i in range(20):
      print(self.opponents[i], self.weights[i])

  def sample(self, size):
    choices = np.random.choice(len(self.opponents), size)
    return [self.opponents[c] for c in choices]

class Opponent:
  def __init__(self, initial_deck):
    self.hand = np.zeros(54, dtype=np.int8)
    choice = np.random.choice(len(initial_deck), 7, replace=False)
    for i in choice:
      self.hand[initial_deck[i]] += 1
    
  def do_action(self, action, valid, deck, draw):
    idx = np.random.choice(deck, draw, replace=False)
    np.add.at(self.hand, idx, 1)

    if action[0] != 54:
      if self.hand[action[0]] > 0:
        self.hand[action[0]] -= 1
        weight = 1
      else:
        indices = np.argwhere(self.hand > 0)
        sampled = np.random.choice(len(indices), 1)
        self.hand[indices[sampled]] -= 1
        weight = 0.1

    elif action[0] == 54:
      valid > 0
      owned = self.hand > 0
      inconsistency = (owned * valid).sum()
      weight = 1/(1+2*inconsistency)
      d = choice(deck)
      self.hand[d] += 1

    return weight

  def __str__(self):
    s = ''
    for i in range(54):
      if self.hand[i] != 0:
        s += INT2CARD[i] + 'x' + str(self.hand[i]) + '  '
    return s

class MCTSAgent(BaseAgent):
  def __init__(self):
    pass

  def receive_availiable_cards(self, available, i):
    if i != self.id:
      self.available_cards[i] = available

  def receive_action(self, action, i):
    if i != self.id:  
      visible_cards = self.game.get_visible_cards(self.id)

      print('start simulation')
      self.opponents[i].do_action(action, self.available_cards[i], 
                                  visible_cards, self.draw[i])
      
      self.draw[i] = 0

  def init_game(self, hand, id, players, game):
    self.hand = hand
    self.id = id
    self.players = players
    self.game = game
    self.opponents = {i: OpponentSimulator(hand, 1000) 
                      for i in set(players) - {id}}
    self.available_cards = {i: None 
                      for i in set(players) - {id}}
    self.draw = {i: 0
                      for i in set(players) - {id}}

  def get_action(self, state, possible_actions):
    return possible_actions[0], 0

  def receive_draw(self, id, d):
    if id != self.id:
      self.draw[id] = d