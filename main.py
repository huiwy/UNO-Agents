import agents
import game

agent = agents.MCTSAgent()
gagent = agents.HumanAgent()

game.play([agent, gagent], "fin", False, False)