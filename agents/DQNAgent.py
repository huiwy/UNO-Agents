import torch
from agents.utils.baseAgent import BaseAgent
from .utils.dqn import DQNOracle

from time import time
from random import choice, randint, random
import numpy as np
class DQNAgent(BaseAgent):
  def __init__(self, memory_len, in_features, layer_dims, out_features,
      train_every, eps, device):
    self.dqn_oracle = DQNOracle(memory_len, in_features, layer_dims, out_features, train_every, device, 
                                epoches=1, memory_batch_size=32)

    self.action = None
    self.last_state = None
    self.eps = eps
    self.exploit = False


  def get_action(self, state, possible_actions, _):
    astate = state[0]

    
    state = np.zeros(54*5)
    state[np.arange(54)+54*astate] = 1

    if not self.exploit:
      self.last_state = state
      if random() < self.eps:
        action = choice(possible_actions)
      else:
        q = self.dqn_oracle.get_Q(self.last_state)
        valid_idx = np.array(possible_actions, dtype = np.uint8)
        
        valid_q = np.zeros_like(valid_idx, dtype=np.float)
        valid_q[np.arange(len(valid_idx))] = q[valid_idx]

        action_idx = np.argmax(valid_q)
        action = valid_idx[action_idx]
    else:
      q = self.dqn_oracle.get_Q(state)
      valid_idx = np.array(possible_actions, dtype = np.uint8)
      
      valid_q = np.zeros_like(valid_idx, dtype=np.float)
      valid_q[np.arange(len(valid_idx))] = q[valid_idx]

      action_idx = np.argmax(valid_q)
      action = valid_idx[action_idx]

    if action == 54 and len(possible_actions) > 1:
      action = possible_actions[0]

    self.action = action

    return [action, 0]

  def receive_next_state(self, next_state, reward):
    if not self.exploit:
      layers_next_state = np.zeros(54*5)
      layers_next_state[np.arange(54)+54*next_state] = 1
      if self.action:
        self.dqn_oracle.update(self.last_state, layers_next_state, self.action, reward)

  def save(self):
    torch.save(self.dqn_oracle.dqn.state_dict(), "DQN.torch")

  def load(self):
    self.dqn_oracle.dqn.load_state_dict(torch.load("DQN.torch"))
  
  def toexploit(self):
    self.exploit = True