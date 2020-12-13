from utils.constants import DECK, INT2CARD, CARD2INT, COLORS
from agents.utils.baseAgent import BaseAgent

class HumanAgent(BaseAgent):
  def __init__(self, name="HumanAgent"):
    super().__init__()
    self.name = name

  def get_action(self, state, possible_actions, aux=None):
    print("="*20 + " %s\'s turn " % self.name + "="*20)

    if state[1] in COLORS:
      print("Previous color: \n\t%s" % state[1] + '\n----------')
    elif state[1]:
      print("Previous card: \n\t%s" % INT2CARD[state[1]] + '\n----------')

    print("Owned cards: ", end = "\n\t")
    for i, j in enumerate(state[0]):
      if j > 0:
        print("[%s]*%s"% (INT2CARD[i], j), end = "\t")
  
    print("\nValid actions: \n \t", end = "")
    count = 0
    for i in possible_actions:
      if i == 54:
        print('%s:[%s]' % (count, "draw"), end = "\t")
      else:
        print('%s:[%s]' % (count, INT2CARD[i]), end = "\t")
      count += 1

    print("\n----------\nYour action: ")
    a = int(input("\tthe index of card: "))
    b = None
    if possible_actions[a] in [52, 53]:
      b = int(input("\tcolor (0:%s, 1:%s, 2:%s, 3:%s): " % tuple(COLORS)))

    return possible_actions[a], b