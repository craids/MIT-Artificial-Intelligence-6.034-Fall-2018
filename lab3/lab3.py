# MIT 6.034 Lab 3: Games
# Written by 6.034 staff

from game_api import *
from boards import *
from toytree import GAME1

INF = float('inf')

# Please see wiki lab page for full description of functions and API.

#### Part 1: Utility Functions #################################################

def is_game_over_connectfour(board):
    for c in board.get_all_chains():
        if len(c) >= 4:
            return True
    return board.count_pieces() >= board.num_rows * board.num_cols

def next_boards_connectfour(board):
    """Returns a list of ConnectFourBoard objects that could result from the
    next move, or an empty list if no moves can be made."""
    next_boards = list()
    if is_game_over_connectfour(board):
        return next_boards
    for col in range(7):
        if not board.is_column_full(col):
            next_boards.append(board.add_piece(col))
    return next_boards

def endgame_score_connectfour(board, is_current_player_maximizer):
    """Given an endgame board, returns 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie."""
    cur_player = board.players[0]
    for c in board.get_all_chains():
        if len(c) >= 4 and len(set(c)) == 1:
            if cur_player == c[0]:
                return 1000 if is_current_player_maximizer else -1000
            else:
                return -1000 if is_current_player_maximizer else 1000
    return 0

def endgame_score_connectfour_faster(board, is_current_player_maximizer):
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""
    cur_pieces = (board.num_rows * board.num_cols + 1) - board.count_pieces()
    return endgame_score_connectfour(board, is_current_player_maximizer) + (-cur_pieces if is_current_player_maximizer else cur_pieces)

def heuristic_connectfour(board, is_current_player_maximizer):
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""
    cur_player = board.count_pieces() % 2
    p1 = board.get_all_chains(cur_player)
    p2 = board.get_all_chains(1 - cur_player)
    p1_tot = p2_tot = 0
    scores = [5, 10, 25, 50]
    for c in p1:
        for i in range(4):
            if len(c) == i:
                p1_tot += i * scores[i]
    for c in p2:
        for i in range(4):
            if len(c) == i:
                p2_tot += i * scores[i]
    score = p1_tot - p2_tot
    return (1-score) if is_current_player_maximizer else score

# Now we can create AbstractGameState objects for Connect Four, using some of
# the functions you implemented above.  You can use the following examples to
# test your dfs and minimax implementations in Part 2.

# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


#### Part 2: Searching a Game Tree #############################################

# Note: Functions in Part 2 use the AbstractGameState API, not ConnectFourBoard.
def expand(state, path, allpaths):
    new_path = path[:]
    new_path.append(state)
    if state.is_game_over():
        allpaths.append(new_path)
        return True
    for child in state.generate_next_states():
        expand(child, new_path, allpaths)

def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score.
    Returns a tuple containing:
     0. the best path (a list of AbstractGameState objects),
     1. the score of the leaf node (a number), and
     2. the number of static evaluations performed (a number)"""
    all_paths = list()
    expand(state, list(), all_paths)

    evals = 0
    path_scores = list()
    for p in all_paths:
        path_scores.append(p[-1].get_endgame_score(is_current_player_maximizer=True))
        evals += 1 #len(path) - 1

    best_path_sel = path_scores.index(max(path_scores))
    best_path = all_paths[best_path_sel]
    best_score = max(path_scores)

    return (best_path, best_score, evals)


# Uncomment the line below to try your dfs_maximizing on an
# AbstractGameState representing the games tree "GAME1" from toytree.py:

# pretty_print_dfs_type(dfs_maximizing(GAME1))
    
def minimax_endgame_search(state, maximize=True) :
    """Performs minimax search, searching all leaf nodes and statically
    evaluating all endgame scores.  Same return type as dfs_maximizing."""
    results = list()
    if state.is_game_over():
        return ([state], state.get_endgame_score(maximize), 1)
    next_states = state.generate_next_states()
    for child in next_states:
        results.append(minimax_endgame_search(child, not maximize))
    evals = 0
    for r in results:
        evals += r[2]
    minmaxfn = max if maximize else min
    result_state = minmaxfn(results, key = lambda x: x[1])
    
    best_path = [state] + result_state[0] 
    return (best_path, result_state[1], evals)


# Uncomment the line below to try your minimax_endgame_search on an
# AbstractGameState representing the ConnectFourBoard "NEARLY_OVER" from boards.py:

# pretty_print_dfs_type(minimax_endgame_search(state_NEARLY_OVER))


def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    """Performs standard minimax search. Same return type as dfs_maximizing."""
    results = list()
    if state.is_game_over():
        return ([state], state.get_endgame_score(maximize), 1)
    if depth_limit == 0:
        return ([state], heuristic_fn(state.get_snapshot(), maximize), 1)
    next_states = state.generate_next_states()
    for child in next_states:
        results.append(minimax_search(child, heuristic_fn, depth_limit - 1, not maximize))
    evals = 0 
    for r in results:
        evals += r[2]
    minmaxfn = max if maximize else min
    result_state = minmaxfn(results,key = lambda x: x[1])
    
    best_path = [state] + result_state[0] 
    return (best_path, result_state[1], evals)


# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1. Try increasing the value of depth_limit to see what happens:

# pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=1))


def minimax_search_alphabeta(state, alpha=-INF, beta=INF, heuristic_fn=always_zero,
                             depth_limit=INF, maximize=True):
    """"Performs minimax with alpha-beta pruning. Same return type 
    as dfs_maximizing."""
    if state.is_game_over():
        return ([state], state.get_endgame_score(maximize), 1)
    if depth_limit == 0:
        return ([state], heuristic_fn(state.get_snapshot(), maximize), 1)
    results = list()
    bestresult = None
    next_states = state.generate_next_states()
    if maximize:
        bestalpha = alpha
        for child in next_states:
            result = minimax_search_alphabeta(child, bestalpha, beta, heuristic_fn, depth_limit - 1, not maximize)
            results.append(result)
            oldalpha = bestalpha
            bestalpha = max(bestalpha,result[1])
            if bestalpha != oldalpha:
                bestresult = result
            if bestalpha >= beta:
                break
    else:
        bestbeta = beta
        for child in next_states:
            result = minimax_search_alphabeta(child, alpha, bestbeta, heuristic_fn, depth_limit - 1, not maximize)
            results.append(result)
            oldbeta = bestbeta
            bestbeta = min(bestbeta,result[1])
            if bestbeta != oldbeta:
                bestresult = result
            if bestbeta <= alpha:
                break
    evals = sum([r[2] for r in results])
    bestresult = (max if maximize else min)(results,key = lambda x: x[1])
    return ([state] + bestresult[0], bestresult[1], evals)


# Uncomment the line below to try minimax_search_alphabeta with "BOARD_UHOH" and
# depth_limit=4. Compare with the number of evaluations from minimax_search for
# different values of depth_limit.

# pretty_print_dfs_type(minimax_search_alphabeta(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))


def progressive_deepening(state, heuristic_fn=always_zero, depth_limit=INF,
                          maximize=True) :
    """Runs minimax with alpha-beta pruning. At each level, updates anytime_value
    with the tuple returned from minimax_search_alphabeta. Returns anytime_value."""
    depth = 0
    anytime_value = AnytimeValue()
    while depth < depth_limit:
        anytime_value.set_value(minimax_search_alphabeta(state, -INF, INF, heuristic_fn,
                             depth+1, maximize=True))
        depth += 1
    return anytime_value


# Uncomment the line below to try progressive_deepening with "BOARD_UHOH" and
# depth_limit=4. Compare the total number of evaluations with the number of
# evaluations from minimax_search or minimax_search_alphabeta.

# progressive_deepening(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4).pretty_print()


# Progressive deepening is NOT optional. However, you may find that 
#  the tests for progressive deepening take a long time. If you would
#  like to temporarily bypass them, set this variable False. You will,
#  of course, need to set this back to True to pass all of the local
#  and online tests.
TEST_PROGRESSIVE_DEEPENING = True
if not TEST_PROGRESSIVE_DEEPENING:
    def not_implemented(*args): raise NotImplementedError
    progressive_deepening = not_implemented


#### Part 3: Multiple Choice ###################################################

ANSWER_1 = '4'

ANSWER_2 = '1'

ANSWER_3 = '4'

ANSWER_4 = '5'


#### SURVEY ###################################################

NAME = 'Rayden Y Chia'
COLLABORATORS = ''
HOW_MANY_HOURS_THIS_LAB_TOOK = 9
WHAT_I_FOUND_INTERESTING = 'finishing this lab'
WHAT_I_FOUND_BORING = 'everything'
SUGGESTIONS = 'such a tedious lab i got nothing out of it'
