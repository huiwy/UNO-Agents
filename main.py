# combine all the things together
from game import play
from agents.humanAgent import HumanAgent
from agents.randomAgent import RandomAgent
from agents.expectimaxAgent import ExpectimaxAgent

import numpy as np
from time import gmtime, strftime

startTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

agent0 = ExpectimaxAgent()
agent1 = RandomAgent()
agent2 = RandomAgent()
agent3 = RandomAgent()

repeat = 1000
agents = [agent0, agent1, agent2, agent3]
winner_record = np.zeros(repeat)
turns_record = np.zeros(repeat)

for i in range(repeat):
    winner, turns = play(agents)

    winner_record[i] = winner
    turns_record[i] = turns

winning_rate = len(winner_record[winner_record==0])/len(winner_record)
avg_turns = np.average(turns_record)

endTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

print('Start at: %s' % startTime)
print('End at: %s' % endTime)

print('='*10 + '%s' % repeat + ' games in total' + '='*10 )
print('Participants:')
for i in range(len(agents)):
    print('\t' + 'agent%s: %s' % (i, agents[i].name))

print('-'*10)
print('winning rate of agent0: %s' % winning_rate)
print('average turns: %s' % avg_turns)


