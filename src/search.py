import chess
from src.constant import *
from src.evaluation import evaluate_board
from src.board import GameState

position_count = 0

def negamax(gamestate: GameState, depth: int, alpha: float, beta: float) -> float:
    global position_count
    position_count += 1

    if depth == 0 or gamestate.board.is_game_over():
        return evaluate_board(gamestate.board)

    max_score = float('-inf')
    legal_moves = list(gamestate.get_legal_moves())

    for move in legal_moves:
        gamestate.make_move(move)
        score = -negamax(gamestate, depth - 1, -beta, -alpha)
        gamestate.unmake_move()

        max_score = max(max_score, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    return max_score

def find_best_move(gamestate :GameState, depth: int) -> chess.Move:
    global position_count
    position_count = 0

    best_move = None
    best_score = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    legal_moves = list(gamestate.get_legal_moves())

    for move in legal_moves:
        gamestate.make_move(move)
        board_score = -negamax(gamestate, depth, -beta, -alpha)
        gamestate.unmake_move()

        if board_score > best_score:
            best_score = board_score
            best_move = move

        alpha = max(alpha, board_score)

    return best_move