"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions from othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cache = {} # Use this for state caching

def eprint(*args, **kwargs): #use this for debugging, to print to sterr
    print(*args, file=sys.stderr, **kwargs)
    
def compute_utility(board, color):
    # IMPLEMENT!
    """
    Method to compute the utility value of board.
    INPUT: a game state and the player that is in control
    OUTPUT: an integer that represents utility
    """
    dark_score, white_score = get_score(board)
    if color == 1:
        return dark_score - white_score
    else:
        return white_score - dark_score
    
def compute_heuristic(board, color):
    # IMPLEMENT! 
    """
    Method to heuristic value of board, to be used if we are at a depth limit.
    INPUT: a game state and the player that is in control
    OUTPUT: an integer that represents heuristic value
    """
    # heuristic logic:
    # 1. calculate the raw score difference
    # 2. calculate how many coners each player occupies and how many corner can be occupided in the future, 
    # and they are awarded a multiple of 10 as corner chesses can not be flipped
    # 3. calculate the moves available to each player

    # Based on the stage of the game, raw score, corner and move available should have different weights:
    # (the stage is determined based on how full the board is occupied)
    # At the openning stage, we emphasize more on the possible moves and the possibility of occupying corners in the future.
    # At the middle of the game, we want to have more emphasis on raw score and occupied corner, less possibility on future 
    # possible corners and moves as we want to have more cells occupied already.
    # At the end of the game, occupied cells including corners are a lot more important, while possible moves and corners
    # are not that important because we want to have the board filled by our color.

    # score difference
    dark_score, white_score = get_score(board)
    if color == 1:
        score_diff = dark_score - white_score
    else:
        score_diff = white_score - dark_score

    # corner + opponent corner
    corner = 0
    opponent_corner = 0
    corners = [(0, 0), (0, len(board) - 1), (len(board) - 1, len(board) - 1), (len(board) - 1, 0)]
    for (i, j) in corners:
        if board[i][j] == color:
            corner += 1
        elif board[i][j] == (3 - color):
            opponent_corner += 1
    corner_diff = (corner - opponent_corner) * 10

    # moves available + corner
    future_corner = 0
    future_oppo_corner = 0
    for move in get_possible_moves(board, color):
        if move == board[0][0] or move == board[0][len(board) - 1] or move == board[len(board) - 1][len(board) - 1] or move == board[len(board) - 1][0]:
            future_corner += 1
    for move in get_possible_moves(board, 3 - color):
        if move == board[0][0] or move == board[0][len(board) - 1] or move == board[len(board) - 1][len(board) - 1] or move == board[len(board) - 1][0]:
            future_oppo_corner += 1
    future_corner_diff = (future_corner - future_oppo_corner) * 10
            
    movable = len(get_possible_moves(board, color)) - len(get_possible_moves(board, 3 - color))

    # check which stage the game is at
    total = len(board) * len(board)
    occupied = 0
    for i in board:
        for j in i:
            if j != 0:
                occupied += 1
    stage = occupied / total

    if stage < 0.25:
        score_weight = 1
        corner_weight = 2
        future_corner_weight = 3
        movable_weight = 3
    elif stage <= 0.5:
        score_weight = 2
        corner_weight = 3
        future_corner_weight = 2
        movable_weight = 2
    else:
        score_weight = 5
        corner_weight = 4
        future_corner_weight = 1
        movable_weight = 1

    heuristic_value = (score_weight * score_diff + corner_weight * corner_diff + future_corner_weight * future_corner_diff + movable_weight * movable)
    return heuristic_value
    
############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    # IMPLEMENT!
    """
    A helper function for minimax that finds the lowest possible utility
    """
    # HINT:
    # 1. Get the allowed moves
    # 2. Check if w are at terminal state
    # 3. If not, for each possible move, get the max utiltiy
    # 4. After checking every move, you can find the minimum utility
    # ...
    if caching and (board, 3 - color) in cache:
        return cache[(board, 3 - color)]

    moves = get_possible_moves(board, 3 - color)
    if moves == [] or limit == 0:
        return None, compute_utility(board, color)
    
    curr_min = float('inf')
    for move in moves:
        new_board = play_move(board, 3 - color, move[0], move[1])

        oppo_move, value = minimax_max_node(new_board, color, limit - 1, caching)
        if caching:
            cache[(new_board, 3 - color)] = (move, value)

        if value < curr_min:
            best_move = move
            curr_min = value

    return best_move, curr_min


def minimax_max_node(board, color, limit, caching = 0):
    # IMPLEMENT!
    """
    A helper function for minimax that finds the highest possible utility
    """
    # HINT:
    # 1. Get the allowed moves
    # 2. Check if w are at terminal state
    # 3. If not, for each possible move, get the min utiltiy
    # 4. After checking every move, you can find the maximum utility
    # ...
    if caching and (board, color) in cache:
        return cache[(board, color)]

    moves = get_possible_moves(board, color)

    if moves == [] or limit == 0:
        return None, compute_utility(board, color)
    
    curr_max = -float('inf')
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])

        oppo_move, value = minimax_min_node(new_board, color, limit - 1, caching)
        if caching:
            cache[(new_board, color)] = (move, value)

        if value > curr_max:
            best_move = move
            curr_max = value

    return best_move, curr_max

def select_move_minimax(board, color, limit, caching = 0):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using Minimax algorithm. 
    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a flag determining whether state caching is on or not
    OUTPUT: a tuple of integers (i,j) representing a move, where i is the column and j is the row on the board.
    """
    # cache.clear()
    return minimax_max_node(board, color, limit, caching)[0]


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # IMPLEMENT!
    """
    A helper function for alpha-beta that finds the lowest possible utility (don't forget to utilize and update alpha and beta!)
    """
    if caching and (board, 3 - color, alpha, beta, limit) in cache:
        return cache[(board, 3 - color, alpha, beta, limit)]

    moves = get_possible_moves(board, 3 - color)

    if moves == [] or limit == 0:
        return (None, compute_utility(board, color))

    best_move = None
    curr_min = float("inf")

    if ordering:
        moves = sorted(moves, key=lambda move: compute_utility(play_move(board, 3 - color, move[0], move[1]), color))

    for move in moves:
        new_board = play_move(board, 3 - color, move[0], move[1])

        oppo_move, value = alphabeta_max_node(new_board, color, alpha, beta, limit - 1, caching, ordering)
        if caching:
            cache[(new_board, 3 - color, alpha, beta, limit)] = (move, value)

        if value < curr_min:
            curr_min = value
            best_move = move
       
        beta = min(beta, curr_min)

        if beta <= alpha:
            break

    return best_move, curr_min


def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # IMPLEMENT!
    """
    A helper function for alpha-beta that finds the highest possible utility (don't forget to utilize and update alpha and beta!)
    """
    if caching and (board, color, alpha, beta, limit) in cache:
        return cache[(board, color, alpha, beta, limit)]

    moves = get_possible_moves(board, color)

    if moves == [] or limit == 0:
        return (None, compute_utility(board, color))

    best_move = None
    curr_max = float("-inf")

    if ordering:
        moves = sorted(moves, key=lambda mv: compute_utility(play_move(board, color, mv[0], mv[1]), color), reverse=True)

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        
        oppo_move, value = alphabeta_min_node(new_board, color, alpha, beta, limit - 1, caching, ordering)
        if caching:
            cache[(new_board, color, alpha, beta, limit)] = (move, value)
    
        if value > curr_max:
            curr_max = value
            best_move = move
       
        alpha = max(alpha, curr_max)

        if beta <= alpha:
            break

    return best_move, curr_max

def select_move_alphabeta(board, color, limit = -1, caching = 0, ordering = 0):
    # IMPLEMENT!
    """
    Given a board and a player color, decide on a move using Alpha-Beta algorithm. 
    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    INPUT: a game state, the player that is in control, the depth limit for the search, a flag determining whether state caching is on or not, a flag determining whether node ordering is on or not
    OUTPUT: a tuple of integers (i,j) representing a move, where i is the column and j is the row on the board.
    """
    # cache.clear()
    return alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)[0]

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) # Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) # Depth limit
    minimax = int(arguments[2]) # Minimax or alpha beta
    caching = int(arguments[3]) # Caching 
    ordering = int(arguments[4]) # Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): # run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: # else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
