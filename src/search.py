import chess
from src.evaluation import evaluate_board
from src.board import GameState

position_count = 0


def order_moves(gamestate: GameState, moves: list[chess.Move]) -> list[chess.Move]:
    captures = []
    others = []
    for move in moves:
        if gamestate.board.is_capture(move):
            captures.append(move)
        else:
            others.append(move)
    return captures + others


def quiescence_search(gamestate: GameState, alpha: float, beta: float) -> float:
    global position_count
    position_count += 1
    stand_pat_score = evaluate_board(gamestate.board)
    if stand_pat_score >= beta:
        return beta
    alpha = max(alpha, stand_pat_score)
    legal_moves = order_moves(gamestate, list(gamestate.get_legal_moves()))
    for move in legal_moves:
        if not gamestate.board.is_capture(move):
            continue
        gamestate.make_move(move)
        score = -quiescence_search(gamestate, -beta, -alpha)
        gamestate.unmake_move()
        if score >= beta:
            return beta
        alpha = max(alpha, score)
    return alpha


def negamax(gamestate: GameState, depth: int, alpha: float, beta: float) -> float:
    global position_count
    position_count += 1
    if gamestate.board.is_game_over():
        return evaluate_board(gamestate.board)
    if depth == 0:
        return quiescence_search(gamestate, alpha, beta)

    max_score = float('-inf')
    legal_moves = order_moves(gamestate, list(gamestate.get_legal_moves()))
    for move in legal_moves:
        gamestate.make_move(move)
        score = -negamax(gamestate, depth - 1, -beta, -alpha)
        gamestate.unmake_move()
        max_score = max(max_score, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return max_score


def search_root(gamestate: GameState, depth: int, alpha: float, beta: float) -> tuple[chess.Move, float]:
    best_move_at_this_node = None
    best_score = float('-inf')
    legal_moves = order_moves(gamestate, list(gamestate.get_legal_moves()))

    if not legal_moves:
        return None, evaluate_board(gamestate.board)

    best_move_at_this_node = legal_moves[0]

    for move in legal_moves:
        gamestate.make_move(move)
        board_score = -negamax(gamestate, depth - 1, -beta, -alpha)
        gamestate.unmake_move()
        if board_score > best_score:
            best_score = board_score
            best_move_at_this_node = move
        alpha = max(alpha, board_score)
    return best_move_at_this_node, best_score


def find_best_move(gamestate: GameState, max_depth: int) -> chess.Move:
    global position_count
    position_count = 0
    best_move_overall = None

    for current_depth in range(1, max_depth + 1):
        best_move_for_depth, score = search_root(gamestate, current_depth, float('-inf'), float('inf'))
        if best_move_for_depth:
            best_move_overall = best_move_for_depth
    return best_move_overall