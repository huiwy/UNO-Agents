from agents.greedyAgent import GreedyAgent
from agents.utils.mcts import MCTS
from random import choice
from utils.constants import INT2CARD, INTACT2TUPLE
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

    for i, o in enumerate(self.opponents):
      w = o.do_action(action, valid, deck, draw)
      weights[i] = w

    weights /= weights.sum()
    self.weights = weights

    self.resample(weights)

  def resample(self, weights):
    samples = np.random.choice(len(self.opponents), len(self.opponents), p=weights)
    new_opponents = [deepcopy(self.opponents[i]) for i in samples]

    self.opponents = new_opponents
    self.weights = [self.weights[i] for i in samples]

    # for i in range(20):
      # print(self.opponents[i], self.weights[i])

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
  def __init__(self, tree_number, mcts_iter):
    self.tree_number = tree_number
    self.mcts_iter = mcts_iter

  def receive_availiable_cards(self, available, i):
    if i != self.id:
      self.available_cards[i] = available

  def receive_action(self, action, i):
    if i != self.id:  
      visible_cards = self.game.get_visible_cards(self.id)

      self.opponents[i].do_action(action, self.available_cards[i], 
                                  visible_cards, self.draw[i])
      
      self.draw[i] = 0

  def receive_draw(self, id, d):
    if id != self.id:
      self.draw[id] = d

  def init_game(self, hand, id, players, game):
    self.hand = hand
    self.id = id
    self.players = players
    self.game = game
    self.opponents = {i: OpponentSimulator(hand, 200) 
                      for i in set(players) - {id}}
    self.available_cards = {i: None 
                      for i in set(players) - {id}}
    self.draw = {i: 0
                      for i in set(players) - {id}}

  def get_action(self, state, possible_actions, _):
    if len(possible_actions) == 1 or (len(possible_actions) == 2 and possible_actions[1] == 54):
      return possible_actions[0], 0
    results_summation = np.zeros(61)
    for i in range(self.tree_number):
      opponents_hands = {i: j.sample(1)[0].hand for i, j in self.opponents.items()}
      try: 
        new_game = create_game(self.game, opponents_hands)
      except ValueError:
        return possible_actions[0], 0
      mcts = MCTS(new_game, self.id)
      results = mcts.search(self.mcts_iter)
    results_summation += results

    action = np.argmax(results)
    return INTACT2TUPLE[action]

def create_game(game, opponent_hands):
  new_game = deepcopy(game)
  tmp_deck = new_game.deck
  new_agents = [GreedyAgent() for i in range(len(new_game.agents))]
  new_game.agents = new_agents
  for i in new_game.hands:
    if i in opponent_hands.keys():
      tmp_deck += inthand2card(new_game.hands[i])
      new_game.hands[i] = opponent_hands[i]
  
  for hand in opponent_hands.values():
    for i in range(len(hand)):
      for _ in range(hand[i]):
        tmp_deck.remove(INT2CARD[i])
  
  shuffle(tmp_deck)
  new_game.deck = tmp_deck
  return new_game

def inthand2card(hand):
  cards = []
  for i in range(len(hand)):
    for _ in range(hand[i]):
      cards.append(INT2CARD[i])

  return cards



