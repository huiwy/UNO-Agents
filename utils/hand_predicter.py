import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim

from tqdm import tqdm
import numpy as np
import pickle

class GameHistoryDataset:
  def __init__(self, device = "cpu"):
    with open('hands.pkl', 'rb') as f:
      self.all_hands = pickle.load(f)

    with open('prev.pkl', 'rb') as f:
      self.all_prev = pickle.load(f)
    
    with open('actions.pkl', 'rb') as f:
      self.all_actions = pickle.load(f)

    self.device = device
  
  def __len__(self):
    return len(self.all_actions)

  def __getitem__(self, index):
    return GameHistory(self.all_hands[index],
                       self.all_prev[index],
                       self.all_actions[index],
                       self.device)

class GameHistory:
  def __init__(self, hands, prev, actions, device):
    self.hand = np.zeros([len(hands), 54*5])
    self.prev = np.zeros([len(prev), 57])
    self.action = np.zeros([len(actions), 61])

    for j in range(len(hands)):
      hand = hands[j]
      self.hand[j][np.arange(54)+54*hand] = 1

      if isinstance(prev[j], int):
        self.prev[j][prev[j]] = 1
      elif prev[j] == 'R':
        self.prev[j][52] = 1
      elif prev[j] == 'Y':
        self.prev[j][53] = 1
      elif prev[j] == 'G':
        self.prev[j][54] = 1
      elif prev[j] == 'B':
        self.prev[j][55] = 1
      elif prev[j] == None:
        self.prev[j][56] = 1

      a, c = actions[j]
      if a < 52:
        self.action[j][a] = 1
      elif a == 54:
        self.action[j][60] = 1
      else:
        self.action[j][(a-52)*4+c] = 1
    
  def pad(self, length):
    pad_len = -self.hand.shape[0] + length + 1
    self.hand = np.concatenate((self.hand, np.zeros([pad_len, 54*5])), axis=0)
    self.prev = np.concatenate((self.prev, np.zeros([pad_len, 57])), axis=0)
    self.action = np.concatenate((self.action, np.zeros([pad_len, 61])), axis=0)

  def __len__(self):
    return len(self.action)

  def __getitem__(self, index):
    # return (self.hand[index], self.action[index], self.prev[index])
    return 0

class GameHistoryBatchSampler:
  def __init__(self, batch_size, device):
    self.dataset = GameHistoryDataset()
    self.len = len(self.dataset) // 10 // batch_size * batch_size

    indices = np.random.choice(self.len, self.len, replace=False)
    self.len //= batch_size
    self.indices = indices.reshape([-1, batch_size])
    self.device = device

  def __len__(self):
    return self.len

  def __getitem__(self, index):
    batch_idx = self.indices[index]
    data_list = [self.dataset[i] for i in batch_idx]
    len_list = [len(data) for data in data_list]
    max_len = max(len_list)

    for data in data_list:
      data.pad(max_len)

    return data_list

# GRU
class HMM_Network(nn.Module):
  def __init__(self):
    super().__init__()
    self.in_layer = nn.Sequential(nn.Linear(57 + 61, 256),
                                  nn.ReLU(),
                                  nn.BatchNorm1d(num_features = 256),
                                  nn.Linear(256, 512))

    self.out_layer = nn.Sequential(nn.Linear(512, 384),
                                   nn.ReLU(),
                                   nn.Linear(384, 54*5),
                                   nn.Sigmoid())

    self.z_layer = nn.Sequential(nn.Linear(1024, 512), nn.Sigmoid())
    self.r_layer = nn.Sequential(nn.Linear(1024, 512), nn.Sigmoid())
    self.h_gate = nn.Sequential(nn.Linear(1024, 512), nn.Tanh())

  def forward(self, p, a, h):
    x_in = self.in_layer(torch.cat((p,a), dim=1))
    z = self.z_layer(torch.cat((x_in, h), dim=1))
    r = self.r_layer(torch.cat((x_in, h), dim=1))
    new_h = r * h
    new_h = self.h_gate(torch.cat((x_in, new_h), dim = 1))
    new_h = (1-z) * h + z * new_h

    y = self.out_layer(new_h)

    return y, new_h

def train(batch_size = 4, device = "cpu"):
  dl = GameHistoryBatchSampler(batch_size, device)
  criterion = nn.BCELoss(reduction='none')
  net = HMM_Network().to(device)
  optimizer = optim.Adam(net.parameters())
  
  for _ in range(10):
    total_loss = 0

    for j in tqdm(range(len(dl))):
      batch = dl[j]
      act = np.concatenate([np.expand_dims(batch[k].action, 1) 
                            for k in range(len(batch))], axis = 1)
      prev = np.concatenate([np.expand_dims(batch[k].prev, 1) 
                            for k in range(len(batch))], axis = 1)
      hand = np.concatenate([np.expand_dims(batch[k].hand, 1) 
                            for k in range(len(batch))], axis = 1)
      
      act = torch.from_numpy(act).to(device).float()
      prev = torch.from_numpy(prev).to(device).float()
      hand = torch.from_numpy(hand).to(device).float()

      loss = 0
      h = torch.zeros([batch_size, 512], device = device)

      optimizer.zero_grad()

      for i in range(act.shape[0]):
        mask = act[i].sum(axis=1) > 0      
        out, h = net(prev[i], act[i], h)

        unmasked_loss = criterion(out, hand[i]).mean(dim=1) * mask
        loss += unmasked_loss.sum()/(mask.sum() + 0.001)
        total_loss += loss.item()

      loss.backward()
      optimizer.step()
    print(total_loss)
  return net
    

      