# Cards, colors, and their maps

import numpy as np

COLORS = ['r', 'y', 'g', 'b']
UCARDS = ['+2', 'skip', 'reverse']
DECK = []

counter = 0

INT2CARD = {}
CARD2INT = {}

for c in COLORS:
  DECK.append(c + '0')
  INT2CARD[counter] = c + '0'
  CARD2INT[c + '0'] = counter
  counter += 1
  for i in range(1, 10):
    DECK.append(c + str(i))
    DECK.append(c + str(i))
    INT2CARD[counter] = c + str(i)
    CARD2INT[c + str(i)] = counter
    counter += 1
  for u in UCARDS:
    DECK.append(c + u)
    INT2CARD[counter] = c + u
    CARD2INT[c + u] = counter
    counter += 1

for i in range(4):
  DECK.append('wild')
  DECK.append('+4')
INT2CARD[52] = 'wild'
CARD2INT['wild'] = 52
INT2CARD[53] = '+4'
CARD2INT['+4'] = 53

INTACT2TUPLE = {i: (i,0) for i in range(52)}
INTACT2TUPLE[60] = (54, 0)
INTACT2TUPLE[52] = (52, 0)
INTACT2TUPLE[53] = (52, 1)
INTACT2TUPLE[54] = (52, 2)
INTACT2TUPLE[55] = (52, 3)
INTACT2TUPLE[56] = (53, 0)
INTACT2TUPLE[57] = (53, 1)
INTACT2TUPLE[58] = (53, 2)
INTACT2TUPLE[59] = (53, 3)

TUPLEACT2INT = {(i, j):i for i in range(52) for j in range(4)}
TUPLEACT2INT.update({(54, i): 60 for i in range(4)})
TUPLEACT2INT[(52, 0)] = 52
TUPLEACT2INT[(52, 1)] = 53
TUPLEACT2INT[(52, 2)] = 54
TUPLEACT2INT[(52, 3)] = 55
TUPLEACT2INT[(53, 0)] = 56
TUPLEACT2INT[(53, 1)] = 57
TUPLEACT2INT[(53, 2)] = 58
TUPLEACT2INT[(53, 3)] = 59

VALIDACTION = []
for i in range(52):
  valid = np.zeros(60)
  num = i % 13
  color = i // 13
  valid[13*color:13*(1+color)] = 1
  valid[num] = 1
  valid[num+13] = 1
  valid[num+26] = 1
  valid[num+39] = 1
  valid[52:] = 1
  VALIDACTION.append(valid)

for i in range(8):
  color = i % 4
  valid = np.zeros(60)
  valid[13*color:13*(1+color)] = 1
  valid[52:] = 1
  VALIDACTION.append(valid)