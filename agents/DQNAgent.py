from agents.utils.baseAgent import BaseAgent
from .utils.dqn import DQNOracle

from time import time
from random import choice, randint, random
import numpy as np
class DQNAgent(BaseAgent):
  def __init__(self, memory_len, in_features, layer_dims, out_features,
      train_every, eps, device):
    self.dqn_oracle = DQNOracle(memory_len, in_features, layer_dims, out_features, train_every, device, 
                                epoches=1, memory_batch_size=1000)

    self.action = None
    self.last_state = None
    self.eps = eps

    for i in range(800):
      self.dqn_oracle.update(np.random.randint(0, 4, 54, dtype=np.uint8), "End", 54, -0.5)

  def get_action(self, state, possible_actions):
    state = state[0]
    self.last_state = state.copy()

    if random() < self.eps:
      action = choice(possible_actions)
    else:
      q = self.dqn_oracle.get_Q(state)
      valid_idx = np.array(possible_actions, dtype = np.uint8)
      
      valid_q = np.zeros_like(valid_idx, dtype=np.float)
      valid_q[np.arange(len(valid_idx))] = q[valid_idx]

      action_idx = np.argmax(valid_q)
      action = valid_idx[action_idx]

    self.action = action

    return [action, randint(0, 3)]

  def receive_next_state(self, next_state, reward):
    if self.action:
      self.dqn_oracle.update(self.last_state, next_state, self.action, reward)

    