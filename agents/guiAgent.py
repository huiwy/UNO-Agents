from .utils.baseAgent import BaseAgent
from utils.constants import DECK, INT2CARD, CARD2INT, COLORS
from time import sleep

class GUIAgent(BaseAgent):
  def __init__(self, scope, name="HumanAgent"):
    super().__init__()
    self.name = name
    self.scope = scope

  def get_action(self, state, possible_actions):
    self.scope["require_action"] = True
    self.scope["action"] = None
    self.scope["selected_color"] = None
    while True:
      if self.scope["action"] in possible_actions:
        action = self.scope["action"]
        self.scope["action"] = None
        self.scope["require_action"] = False
        break
      if self.scope["action"] != None:
        self.scope["invalid_action"] = True
      sleep(0.1)
    color = 0
    if action in [52, 53]:
      self.scope["select_color"] = True
      while self.scope["selected_color"] == None:
        sleep(0.1)
      color = self.scope["selected_color"]
      self.scope["selected_color"] = None

      print(color)

    self.scope["invalid_action"] = False

    return action, color