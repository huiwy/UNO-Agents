def greedy_heuristic(state):
  return 1/state.sum() + (state[52] + state[53]) / state.sum()