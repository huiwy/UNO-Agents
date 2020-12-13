from agents.utils.baseAgent import BaseAgent
from utils.constants import DECK, INT2CARD, CARD2INT, COLORS

from agents.utils.evaluationFunc import naiveEvaluate

class ExpectimaxAgent(BaseAgent):
    def __init__(self, name="ExpectimaxAgent", maxDepth=10, evaluateFunc=naiveEvaluate):
        super().__init__()
        self.name = name
        self.maxDepth = 10
        self.evaluateFunc = evaluateFunc
    
    def get_action(self, state, possible_actions, aux):
        """get_action
        Args:
            state (([int],int)): (hands[current_player], previous_card)
            possible_actions ([int]): valid_actions of the current player
            aux (dict):
                possible_cards ([str]): possible cards when drawing
                current_player (int): the index of current player
                hands ({i:np.zeros(54)...}): all agents' hands
        Return:
            [int, int]: [action, color(when necessary)]
        """
        hands = aux['hands']
        current_player = aux['current_player']
        possible_cards = aux['possible_cards']

        card2Prob = {}
        for card in possible_cards:
            if card in card2Prob:
                card2Prob[card] += 1
            else:
                card2Prob[card] = 1
        card2Prob.update({k: card2Prob[k]/len(possible_cards) \
            for k in card2Prob.keys()})

        optimalEvalVal = float('-inf')
        optimalAction = None
        optimalColor = None

        # It it necessary to copy the hands in case of the change of hands in UNO
        # when trying every single possible result under possible actions.
        # Also, dict.copy() is not a deep copy. Directly performing hands.copy() is no use.
        for action in possible_actions:
            if action == 54: # Draw
                evalVal = 0
                for card in possible_cards:
                    tempHands = {i:hands[i].copy() for i in range(len(hands))}

                    tempHands[current_player][CARD2INT[card]] += 1
                    evalVal += self.evaluateFunc(current_player, tempHands) * card2Prob[card]
            elif action in [52, 53]: # wild, +4
                tempHands = {i:hands[i].copy() for i in range(len(hands))}
                
                tempHands[current_player][action] -= 1

                evalVal = self.evaluateFunc(current_player, tempHands)
                optimalColor = 0 # This should be implemented.
            else:
                tempHands = {i:hands[i].copy() for i in range(len(hands))}

                tempHands[current_player][action] -= 1
                evalVal = self.evaluateFunc(current_player, hands)
            
            if evalVal > optimalEvalVal:
                optimalEvalVal = evalVal
                optimalAction = action
        # print('optimalEvalVal:%s, optimalAction: %s' % (optimalEvalVal, optimalAction))

        # only implemented searching with depth=0
        return optimalAction, optimalColor





