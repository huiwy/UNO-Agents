from agents.utils.baseAgent import BaseAgent
from agents.greedyAgent import GreedyAgent
from utils.constants import DECK, INT2CARD, CARD2INT, COLORS

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

        des_max, eval_max = self.find_max_action_and_eval(self.game, depth_count=1)

        return des_max
        # return possible_actions[0], choice(range(4))

    def find_max_action_and_eval(self, game, depth_count):
        if depth_count > self.max_depth:
            return None, self.evaluateFunc(game)

        actions = game.get_valid_actions()
        possible_drawn_cards = game.get_possible_drawn_cards()
        extended_actions = extend_actions(actions, possible_drawn_cards)

        action_deses = []
        action_evals = []
        if len(extended_actions['other']) > 0:
            count = 0
            for action in extended_actions['other']:
                action_des, action_eval = self.evaluate_other(game, action, depth_count)
                action_deses.append(action_des)
                action_evals.append(action_eval+game.turns*0.5)
                count += 1

        if len(extended_actions['draw']) > 0:
            action_des, action_eval = self.evaluate_draw(game, extended_actions['draw'], depth_count)
            action_deses.append(action_des)
            action_evals.append(action_eval)
    
        eval_max = max(action_evals)
        
        des_max = action_deses[action_evals.index(eval_max)]

        # if depth_count == 1:
            # print('     action_deses:', action_deses)
            # print('     action_evals:', action_evals)
        return des_max, eval_max

    def evaluate_draw(self, game, draw_actions, depth_count):
        action_des = (54, None)
        action_evals = []

        count = 0
        for draw_action in draw_actions:
            tmp_game = create_game(game)
            eval_score = 0
            is_over, winner = simulate_one_round(tmp_game, draw_action)
            if is_over:
                if winner == game.current_player:
                    eval_score = 100
                else:
                    eval_score = -100
            else:
                eval_des, eval_score = self.find_max_action_and_eval(tmp_game, depth_count+1)
            action_evals.append(eval_score)
            count += 1

        action_eval = sum(action_evals)/len(action_evals)
        return action_des, action_eval

    def evaluate_other(self, game, other_action, depth_count):
        action_des = other_action
        tmp_game = create_game(game)
        eval_score = 0
        is_over, winner = simulate_one_round(tmp_game, other_action)
        if is_over:
            if winner == game.current_player:
                action_eval = 100
            else:
                action_eval = -10
        else:
            _, action_eval = self.find_max_action_and_eval(tmp_game, depth_count+1)
            
        return action_des, action_eval

def create_game(game):
    """
    In this function, we create a new game from game.
    And we also randomly shuffle opponents' hands.
    """
    new_game = deepcopy(game)
    new_agents = [GreedyAgent() for i in range(len(new_game.agents))]
    for i, agent in enumerate(new_agents):
        agent.id = i
    new_game.agents = new_agents

    opponent_ids = new_game.players.copy()
    opponent_ids.remove(new_game.current_player)

    # Randomly distribute opponents' hands
    opponent_hands = []
    for i in new_game.hands:
        if i != new_game.current_player:
            # Firstly take the hands back
            new_game.hands[i] = np.zeros(54, dtype=np.uint8)
            opponent_hands += inthand2card(new_game.hands[i])

    for card in opponent_hands:
        # Reassign the cards
        assign_to = choice(opponent_ids)
        new_game.hands[assign_to][CARD2INT[card]] += 1

    return new_game

def simulate_one_round(game, action):
    """
    Return (if the game is terminated, winner)
    """
    # Current agent's turn
    current_agent_id = game.current_player
    game.simulate_action(action)
    if game.current_win():
        winner = current_agent_id
        return (True, winner)
    game.next_player()
    game.penalize()

    # Opponents' turns
    while (game.current_player != current_agent_id):
        while True:
            action = game.get_action()
            if game.apply_action(action):
                break
        if game.current_win():
            winner = game.current_player
            return (True, winner)
        game.next_player()
        game.penalize()

    return (False, None)

def inthand2card(hand):
  cards = []
  for i in range(len(hand)):
    for _ in range(hand[i]):
      cards.append(INT2CARD[i])

  return cards

def extend_actions(actions, possible_drawn_cards):
    extended_actions = {
        'draw': [],
        'other': []
    }
    if len(possible_drawn_cards) > 4:
        possible_drawn_cards = sample(possible_drawn_cards, 4)
    for action in actions:
        if action == 54:
            for c in possible_drawn_cards:
                extended_actions['draw'].append((action, c))
        elif action in [52, 53]: # Wild, +4
            for color in range(len(COLORS)):
                temp = (action, color)
                extended_actions['other'].append(temp)
        else:
            extended_actions['other'].append((action, None))
    return extended_actions