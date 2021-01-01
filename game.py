# Game logic of UNO

# 2 options 
# Call UNO implemented by rlcard
# Implement UNO ourselves

# What can rlcard provide
# A toolkit for Reinforcement Learning (RL) in card games.
# Implemented algorithms as references.
# Implemented game environment.
# Moderate visualization.

# What is the advantage of implement the game outselves
# The information provided by the environment is not sufficient
# Add more restrictions to make the game simpler.

from numpy.lib.arraysetops import isin
from agents.dqnAgent import DQNAgent
from itertools import cycle
from random import choice, shuffle
import numpy as np

from utils.constants import DECK, INT2CARD, CARD2INT, COLORS

# class UNOState:
#   def __init__(self, agents, mode = "infinite deck"):
#     self.unogame = UNOGame(agents, mode)
#     self.agent_iterator = cycle(agents)
#     self.current_agent = next(self.agent_iterator)

#     self.agents = agents

#   def get_next_state(self, ):
#     pass
  
class IsoMappedState:
  def __init__(self, hand):
    """
    Given a hand, map it to a isomorphic hand with predetermined order:
      color of maximum number of cards -> Red
      ...
      number with maximum number of cards -> 1
      ...
      
    Note:
      Only the color of functional cards and 0 will change.
      Wild cards are not included in the map

    eg.
      B1, B2, Y2, B+2 -> R1, R2, R+2, Y1
    """
    self.hand = hand
    colored_cards = hand[:52].copy()

    color_axis = colored_cards.reshape((4, 13))
    number_axis = color_axis.transpose()

    color_order = np.argsort(color_axis @ np.ones(13))[::-1]
    number_order = np.argsort(number_axis @ np.ones(4))[9:0:-1]

    new = number_axis.copy()
    new[np.arange(1, 10)] = number_axis[number_order]
    new = new.transpose()

    new_new = np.empty_like(color_axis)
    new_new[np.arange(4)] = new[color_order]

    new_new = new_new.reshape(-1)

    isomorphic_hand = np.zeros(54, dtype=np.int64)
    isomorphic_hand[:52] = new_new
    isomorphic_hand[52:] = hand[52:]

    self.isomorphic_hand = isomorphic_hand

class UNO:
  def __init__(self, agents, mode = "infinite deck", state_map = False, forced_draw_only = True):
    """
    UNO class contains the game logic, hold the basic information of the game,
    can be made to contain more inforamtion to better policies.
    """
    self.agents = agents
    self.state_map = state_map
    self.forced_draw_only = forced_draw_only

    self.players = list(range(len(agents)))
    self.current_player = self.players[0]
    self.direction = 1

    self.init_dealer(mode)
    self.hands = {i:np.zeros(54, dtype=np.uint8) for i in range(len(agents))}
    self.penalty = None
    self.mode = mode

    for i in self.players:
      for _ in range(7):
        self.draw(i)

    for i in self.players:
      self.agents[self.players[i]].init_game(self.hands[i], 
                                             i, self.players, self)

    self.previous_card = None

  def draw(self, player):
    """draw
    give the player a card
    """
    card = self.dealer()
    idx = CARD2INT[card]

    self.hands[player][idx] += 1

  def get_action(self):
    """get_action
    Call the current agent to give the action.

    :Return:
      tuple[int, int]
    """
    state = self.get_state()
    possible_actions = self.get_valid_actions()

    possible_cards = DECK if self.mode == 'infinite deck' else self.wasted

    aux = {"current_player": self.current_player, \
          "hands": self.hands, \
          "possible_cards": possible_cards
    }
    action = self.agents[self.current_player].get_action(state, possible_actions, aux)
    return action

  def get_state(self):
    """get_state
    Get the state representation of the current player
    """
    # Current version:
    # memoryless agents, blind to the history of the game
    if self.state_map:
      raise NotImplementedError
    else:
      if isinstance(self.agents[self.current_player], DQNAgent):
        self.agents[self.current_player].receive_next_state(
                        self.hands[self.current_player], 0)

      return (self.hands[self.current_player], self.previous_card)

  def apply_action(self, action):
    """apply_action
    Apply action i to current player.
    
    Parameters
    ---
    Action: tuple[int, int]

      the first int is the card to play 54 means draw, the second is wild color if necessary.

    Returns
    ---
      Boolean:

        Whether this player decides to draw.
    """

    for a in self.agents:
      a.receive_action(action, self.current_player)

    if action[0] == 54:
      # draw 1 card
      idx = CARD2INT[self.dealer()]
      self.hands[self.current_player][idx] += 1
      # if draw, it is still the current player's turn.
      return False

    if action[0] in [52, 53]:
      # Wild or +4
      self.previous_card = COLORS[action[1]]
      self.penalty = '+4' if action[0] == 53 else None
    elif action[0] % 13 == 10:
      # +2
      self.previous_card = action[0]
      self.penalty = '+2'
    elif action[0] % 13 == 11:
      # skip
      self.previous_card = action[0]
      self.penalty = 'skip'
    elif action[0] % 13 == 12:
      # reverse
      self.previous_card = action[0] 
      self.direction *= -1
    else:
      # normal card
      self.previous_card = action[0]

    if self.mode != "infinite deck":
      self.wasted.append(INT2CARD[action[0]])
    # remove the card
    self.hands[self.current_player][action[0]] -= 1
    return True
  
  def current_win(self):
    """current_win
    Returns
    ---
    Boolean: whether the current player is a winner.
    """

    win = self.hands[self.current_player].sum() == 0
    if win and isinstance(self.agents[0], DQNAgent):
      self.agents[0].receive_next_state("End", int(win)*2 - 1)

    return win

  def get_valid_actions(self):
    """
    get the valid actions of the current player.
    return a list of actions (indices of cards)
    """
    owned_cards = self.hands[self.current_player] > 0
    available_cards = np.zeros(54)
    # the wild cards must be available
    available_cards[52:] = 1
    # wild card cases
    if self.previous_card == 'r':
      available_cards[:13] = 1
    elif self.previous_card == 'y':
      available_cards[13:26] = 1
    elif self.previous_card == 'g':
      available_cards[26:39] = 1
    elif self.previous_card == 'b':
      available_cards[39:52] = 1
    elif self.previous_card == None:
      # no card is played
      available_cards[:] = 1
    else:
      # normal case
      num = self.previous_card % 13
      color = self.previous_card // 13
      available_cards[13*color:13*(1+color)] = 1
      available_cards[num] = 1
      available_cards[num+13] = 1
      available_cards[num+26] = 1
      available_cards[num+39] = 1
    valid_actions = np.nonzero(available_cards * owned_cards)[0].tolist()
    # add the last draw action
    if not self.forced_draw_only or len(valid_actions) == 0:
      valid_actions.append(54)
    
    for a in self.agents:
      a.receive_availiable_cards(available_cards, self.current_player)

    return valid_actions

  def init_dealer(self, mode):
    """
    initialize the dealer.
    """
    if mode == "infinite deck":
      self.dealer = self.inf_dealer
    else:
      self.dealer = self.finite_dealer
      deck = DECK.copy()
      shuffle(deck)
      self.deck = deck
      self.wasted = []

  def inf_dealer(self):
    """
    Inifinite dealer. The size of DECK is infinite
    """
    return choice(DECK)

  def finite_dealer(self):
    """
    Finite dealer. The size of DECK is finite
    """
    if len(self.deck) == 0:
      shuffle(self.wasted)
      self.deck = self.wasted
      self.wasted = []
    return self.deck.pop()
  
  def next_player(self):
    """
    move control to next player
    """
    self.current_player += self.direction
    # start a new cycle
    if self.current_player == len(self.players):
      self.current_player = 0
    elif self.current_player == -1:
      self.current_player = len(self.players) - 1

  def penalize(self):
    """
    penalize the current player
    """
    if self.penalty == 'skip':
      self.next_player()
    elif self.penalty == "+2":
      self.draw(self.current_player)
      self.draw(self.current_player)
      for a in self.agents:
        a.receive_draw(self.current_player, 2)
    elif self.penalty == "+4":
      self.draw(self.current_player)
      self.draw(self.current_player)
      self.draw(self.current_player)
      self.draw(self.current_player)
      for a in self.agents:
        a.receive_draw(self.current_player, 4)
    self.penalty = None

  def get_visible_cards(self, id):
    if self.mode == "infinite deck":
      return self.hands
    else: 
      visible = self.hands[id].copy()
      for i in self.wasted:
        visible[CARD2INT[i]] += 1
      return visible

def play(game):
  """
  play a game

  Parameters
  ---
  Agents:

  A list of agents to play the game.

  mode:

  Whether the deck is "infinite deck" or "finite deck", default "infinite deck".
  """
  while True:
    while True:
      action = game.get_action()
      if game.apply_action(action):
        break
    if game.current_win():
      winner = game.current_player
      return winner
    game.next_player()
    game.penalize()