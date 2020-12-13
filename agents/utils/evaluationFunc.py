from utils.constants import DECK, INT2CARD, CARD2INT, COLORS

# Very naive evaluation function is implemented. QAQ
def naiveEvaluate(current_player, hands):
    """
    Args:
        hand (np.zeros(54)): The current agent A's hand
        hands ({i:np.zeros(54)...}): All agents' hands
    Return:
        evaluationVal (float): Evaluation score of the 
            current player's state.
    """

    # Metric 1: cardNumRatio
    # Ratio of the number of cards in the current Agent's hand
    # to the number of cards in all the agents' hands.
    # The smaller the ratio is, the higher the evaluation value should be.
    cardNumOfCurAgent = hands[current_player].sum()
    cardNumOfAllAgents = 1
    for i in hands:
        cardNumOfAllAgents += hands[i].sum()
    cardNumRatio = cardNumOfCurAgent / cardNumOfAllAgents

    # Metric 2: special NumRatio
    # Special cards can help players in many dangerious situations.
    # The more percentage of special cards one agent helds, the safer it will be safer.
    plus2NumOfCurAgent = 0
    plus2NumOfAllAgents = 1
    for c in COLORS:
        plus2NumOfCurAgent += hands[current_player][CARD2INT[c+'+2']]
    for i in hands:
        for c in COLORS:
             plus2NumOfAllAgents += hands[i][CARD2INT[c+'+2']]
    plus2NumRatio = plus2NumOfCurAgent / plus2NumOfAllAgents

    skipNumOfCurAgent = 0
    skipNumOfAllAgents = 1
    for c in COLORS:
        skipNumOfCurAgent += hands[current_player][CARD2INT[c+'skip']]
    for i in hands:
        for c in COLORS:
            skipNumOfAllAgents += hands[i][CARD2INT[c+'skip']]
    skipNumRatio = skipNumOfCurAgent / skipNumOfAllAgents

    reverseNumOfCurAgent = 0
    reverseNumOfAllAgents = 1
    for c in COLORS:
        reverseNumOfCurAgent += hands[current_player][CARD2INT[c+'reverse']]
    for i in hands:
        for c in COLORS:
            reverseNumOfAllAgents += hands[i][CARD2INT[c+'reverse']]
    reverseNumRatio = reverseNumOfCurAgent / reverseNumOfAllAgents

    wildNumOfCurAgent = 0
    wildNumOfAllAgents = 1
    wildNumOfCurAgent += hands[current_player][CARD2INT['wild']]
    for i in hands:
        wildNumOfAllAgents += hands[i][CARD2INT['wild']]
    wildNumRatio = wildNumOfCurAgent / wildNumOfAllAgents

    plus4NumOfCurAgent = 0
    plus4NumOfAllAgents = 1
    plus4NumOfCurAgent += hands[current_player][CARD2INT['+4']]
    for i in hands:
        plus4NumOfAllAgents += hands[i][CARD2INT['+4']]
    plus4NumRatio = plus4NumOfCurAgent / plus4NumOfAllAgents

    # Metric 3: ...

    evaluationVal = \
        - cardNumRatio * 0 \
        + plus2NumRatio * 2 \
        + skipNumRatio * 2 \
        + reverseNumRatio * 2 \
        + wildNumRatio * 3 \
        + plus4NumRatio * 3
    
    return evaluationVal
