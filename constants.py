# Cards, colors, and their maps

COLORS = ['R', 'Y', 'G', 'B']
UCARDS = ['+2', 'skip', 'reverse']
DECK = []

counter = 0

INT2CARD = {}
CARD2INT = {}

for c in COLORS:
  # DECK.append(c + '0')
  # INT2CARD[counter] = c + '0'
  # CARD2INT[c + '0'] = counter
  # counter += 1
  for i in range(0, 10):
    DECK.append(c + str(i))
    DECK.append(c + str(i))
    INT2CARD[counter] = c + str(i)
    CARD2INT[c + str(i)] = counter
    counter += 1
  for u in UCARDS:
    DECK.append(c + u)
    INT2CARD[counter] =c + u
    CARD2INT[c + u] = counter
    counter += 1

for i in range(4):
  DECK.append('wild')
  DECK.append('+4')
INT2CARD[52] = 'wild'
CARD2INT['wild'] = 52
INT2CARD[53] = '+4'
CARD2INT['+4'] = 53