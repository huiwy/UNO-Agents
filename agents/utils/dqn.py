from collections import deque
import numpy as np

import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

class EXPDataset(Dataset):
  def __init__(self, state, act, val):
    super().__init__()
    self.state = state
    self.val = val
    self.act = act

  def __len__(self):
    return len(self.state)

  def __getitem__(self, index):
      return self.state[index],self.act[index], self.val[index]


class DQNetwork(nn.Module):
  def __init__(self, in_features, layer_dims, out_features):
    super(DQNetwork, self).__init__()

    layers = [nn.Linear(in_features, layer_dims[0]), 
              nn.BatchNorm1d(layer_dims[0]), nn.ReLU(inplace=True)]

    for i in range(1, len(layer_dims)):
      layers.append(nn.Linear(layer_dims[i-1], layer_dims[i]))
      layers.append(nn.BatchNorm1d(layer_dims[i]))
      layers.append(nn.ReLU(inplace=True))
    
    layers.append(nn.Linear(layer_dims[-1], out_features))

    self.fc = nn.Sequential(*layers)
  
  def forward(self, x):
    return torch.tanh(self.fc(x))

class DQNOracle:
  def __init__(self, memory_len, in_features, layer_dims, out_features,
   train_every, device, epoches = 5, lr = 1e-3, memory_batch_size = 1000, lam = 0.9):
  
    self.state_memory = deque(maxlen=memory_len)
    self.action_memory = deque(maxlen=memory_len)
    self.value_memory = deque(maxlen=memory_len)

    self.dqn = DQNetwork(in_features, layer_dims, out_features).to(device).float()

    self.optimizer = optim.Adam(self.dqn.parameters(), lr = lr)

    self.device = device
    self.train_every = train_every
    self.epoches = epoches
    self.memory_batch_size = memory_batch_size
    self.lam = lam

    self.counter = train_every

  def get_Q(self, state):
    with torch.no_grad():
      self.dqn.eval()
      last_Q = self.dqn(torch.Tensor(state).to(self.device)
                             .view([1, *state.shape]))[0]
      
      return last_Q.cpu().numpy()

  def update(self, prev_state, state, action, reward):
    with torch.no_grad():
      if isinstance(state, np.ndarray):
        self.dqn.eval()
        Q = self.dqn(torch.Tensor(state).to(self.device)
                    .view([1, *state.shape]))
        Q_star = Q.max()
        new_Q = reward + self.lam * Q_star
      else:
        new_Q = reward

    self.state_memory.append(prev_state)
    self.value_memory.append(float(new_Q))
    self.action_memory.append(action)


    self.counter -= 1
    if self.counter == 0:
      self.counter = self.train_every
      if len(self.state_memory) > self.memory_batch_size:
        self.train()
      
  def train(self):
    self.dqn.train()
    
    sample_idx = np.random.choice(len(self.state_memory), self.memory_batch_size, replace=False)

    state_arr = np.array(self.state_memory)[sample_idx]
    action_arr = np.array(self.action_memory, dtype=np.int32)[sample_idx]
    value_arr = np.array(self.value_memory)[sample_idx]

    exp_dataset = EXPDataset(state_arr, action_arr, value_arr)
    exp_loader = DataLoader(exp_dataset, batch_size=4, shuffle=True, drop_last=True)

    device = self.device
    criterion = nn.MSELoss()

    for _ in range(self.epoches):
      for _, data in enumerate(exp_loader):
        state, action, value = data

        state = state.float().to(device)
        value = value.to(device)
        self.optimizer.zero_grad()

        pred_value = self.dqn(state)
        # calculate the loss
        loss = criterion(pred_value[torch.arange(state.size(0)), action.long()], value.float()).float()
        # loss = dir_loss(head_pos, gt_gaze, pred_dir)
        loss.backward()

        # nn.utils.clip_grad_norm_(model.parameters(), 0.001)
        self.optimizer.step()
    
    self.dqn.train()