from .utils.baseAgent import BaseAgent
from .constants import DECK, INT2CARD, CARD2INT, COLORS


class HumanAgent(BaseAgent):
  def __init__(self):
    super().__init__()

  def get_action(self, state, possible_actions):
    print("Owned cards: ")
    for i, j in enumerate(state[0]):
      if j > 0:
        print("\t"+str(INT2CARD[i]) +':' + str(j) + ',', end = " ")
    
    print("\nValid actions: \n \t", end="")
    for i in possible_actions[:-1]:
      print(INT2CARD[i], end =", ")
    print("Draw")

    if state[1] in COLORS:
      print("previous color :", state[1])
    elif state[1]:
      print("previous card :", INT2CARD[state[1]])

    a = int(input("the index of card :"))
    b = int(input("color, if necessary :"))

    return possible_actions[a], b