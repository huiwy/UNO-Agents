from numpy.core.fromnumeric import argmax
from agents.utils.baseAgent import BaseAgent
from agents.greedyAgent import GreedyAgent
from utils.constants import DECK, INT2CARD, CARD2INT, COLORS, INTACT2TUPLE, TUPLEACT2INT, VALIDACTION

from .utils.evaluationFunc import naiveEvaluate
from utils import util

from copy import copy, deepcopy
from random import choice
from random import shuffle
from random import sample

import numpy as np

class ExpectimaxAgent(BaseAgent):
    def __init__(self, name="ExpectimaxAgent", max_depth=3, evaluateFunc=naiveEvaluate):
        super().__init__()
        self.name = name
        self.max_depth = max_depth
        self.evaluateFunc = evaluateFunc
    
    def init_game(self, hand, id, players, game):
        self.id = id
        self.players = players
        self.game = game
    
    def get_action(self, state, possible_actions):
        """get_action
        Args:
            state (([int],int)): (hands[current_player], previous_card)
            possible_actions ([int]): valid_actions of the current player
            aux (dict):
                possible_cards ([str]): possible cards when drawing
                current_player (int): the index of current player
                hands ({i:np.zeros(54)...}): all agents' hands
        Return:
            des_max: [int, int]: [action, color(when necessary)]
        """
        if len(possible_actions) == 1:
            return possible_actions[0], 0

        invisible = self.invisible_cards()
        other_hand = [hand.sum() for _, hand in self.game.hands.items()]
        other_hand.pop(self.id)
        action = expectimax(self.game.hands[self.id], other_hand, invisible, possible_actions)

        if action[0] == 54:
            return possible_actions[0], 0
        return action

    def invisible_cards(self):
        visible = self.game.hands[self.id].copy()
        for i in self.game.wasted:
            visible[CARD2INT[i]] += 1
        invisible = 4 - visible
        return invisible
        
def expectimax(curr_hand, other_hand, invisible, possible_actions):

    num_cards = invisible.sum()
    hand = np.zeros(60)
    old_actions = []
    new_actions = []
    for i, n in enumerate(invisible):
        if i < 52:
            hand[i] = n
        else:
           for j in range(4):
                hand[TUPLEACT2INT[(i, j)]] = n

    hand /= num_cards

    scores = np.ones(60) * -100
    Pas = []
    for action in possible_actions:
        a = np.zeros(60)
        if action < 52:
            a[action] = 1
            Pas.append(a)
            old_actions.append(action)
            new_actions.append(action)
        elif action == 54:
            pass
        else:
           for i in range(4):
                a[TUPLEACT2INT[(action, i)]] = 1
                Pas.append(a)
                old_actions.append(action)
                new_actions.append(TUPLEACT2INT[(action, i)])
    
    Pas = np.array(Pas)
    for num_cards in other_hand:
        T = np.zeros([60, 60])
        for i in range(60):
            tmp = (1 - (1 - hand))**num_cards * VALIDACTION[i]
            T[i,:] = tmp / tmp.sum()
            
        Pas = Pas@T

    for i in range(Pas.shape[0]):
        scores[i] = 0
        for j in range(60):
            scores[old_actions[i]] += Pas[i,j]*value(curr_hand.copy(), old_actions[i], j)

    idx = np.argmax(scores)
    return INTACT2TUPLE[new_actions[idx]]

def value(hand, old_action, prev_act):
    card = INTACT2TUPLE[old_action][0]
    hand[card] -= 1

    avaliable_cards = VALIDACTION[prev_act]
    avaliable_cards[53] = avaliable_cards[57]

    avaliable_cards = avaliable_cards[:54] * hand
    
    score = 0

    if avaliable_cards.sum() == 0:
        score -= 5
    
    score += hand[52] + hand[53]

    for i in range(4):
        score += hand[i*13 :13*(1+i)].sum() > 0

    return score
    
