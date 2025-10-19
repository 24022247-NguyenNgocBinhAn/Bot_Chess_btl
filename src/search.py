import chess
from .evaluation import evaluate_board
from .board import GameState
from .constant import MVV_LVA_SCORES
from chess import polyglot


# ==============================================================================
# TRANSPOSITION TABLE
# ==============================================================================

class TTEntry:
    """Transposition Table Entry"""
    __slots__ = ('depth', 'score', 'flag', 'best_move')

    EXACT = 0
    LOWER = 1  # Beta cutoff (score >= beta)
    UPPER = 2  # Alpha unchanged (score <= alpha)

    def __init__(self, depth: int, score: float, flag: int, best_move: chess.Move):
        self.depth = depth
        self.score = score
        self.flag = flag
        self.best_move = best_move


# ==============================================================================
# GLOBAL DATA STRUCTURES
# ==============================================================================

position_count = 0
MAX_DEPTH = 64
TT_SIZE = 2 ** 20
transposition_table = [None] * TT_SIZE
killer_moves = [[None, None] for _ in range(MAX_DEPTH)]
history_heuristic = [[[0] * 64 for _ in range(64)] for _ in range(2)]

# Constants
NULL_MOVE_REDUCTION = 2
LMR_THRESHOLD = 3
LMR_REDUCTION = 1

def tt_store(board: chess.Board, depth: int, score: float, flag: int, best_move: chess.Move):
    key = chess.polyglot.zobrist_hash(board)%TT_SIZE
    transposition_table[key] = TTEntry(depth, score, flag, best_move)


def tt_probe(board: chess.Board, depth: int, alpha: float, beta: float):
    key = chess.polyglot.zobrist_hash(board)%TT_SIZE
    entry = transposition_table[key]

    if entry is None:
        return False, None, None
    if entry.depth < depth:
        return False, None, entry.best_move

    if entry.flag == TTEntry.EXACT:
        return True, entry.score, entry.best_move
    elif entry.flag == TTEntry.LOWER and entry.score >= beta:
        return True, entry.score, entry.best_move
    elif entry.flag == TTEntry.UPPER and entry.score <= alpha:
        return True, entry.score, entry.best_move

    return False, None, entry.best_move

def score_move(board: chess.Board, move: chess.Move, depth: int, tt_move: chess.Move = None) -> int:
    if tt_move and move == tt_move:
        return 1000000

    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            return 100000 + MVV_LVA_SCORES[attacker.piece_type][victim.piece_type]
        return 100000
    if move.promotion:
        return 90000 + move.promotion

    if depth < MAX_DEPTH:
        if killer_moves[depth][0] == move:
            return 80000
        elif killer_moves[depth][1] == move:
            return 70000

    return history_heuristic[board.turn][move.from_square][move.to_square]


def order_moves(board: chess.Board, moves: list[chess.Move], depth: int, tt_move: chess.Move = None) -> list[chess.Move]:
    return sorted(moves, key=lambda m: score_move(board, m, depth, tt_move), reverse=True)

def quiescence_search(gamestate: GameState, alpha: float, beta: float) -> float:
    global position_count
    position_count += 1
    stand_pat = evaluate_board(gamestate.board)

    if stand_pat >= beta:
        return beta
    BIG_DELTA = 900
    if stand_pat < alpha - BIG_DELTA:
        return alpha

    alpha = max(alpha, stand_pat)
    capture_moves = []
    for m in gamestate.get_legal_moves():
        if gamestate.board.is_capture(m):
            capture_moves.append(m)
    capture_moves = order_moves(gamestate.board, capture_moves, 0)

    for move in capture_moves:
        gamestate.make_move(move)
        score = -quiescence_search(gamestate, -beta, -alpha)
        gamestate.unmake_move()

        if score >= beta:
            return beta
        alpha = max(alpha, score)

    return alpha


def negamax(gamestate: GameState, depth: int, alpha: float, beta: float, do_null: bool = True) -> float:
    global position_count

    alpha_orig = alpha
    position_count += 1

    if gamestate.board.is_game_over():
        return evaluate_board(gamestate.board)
    tt_hit, tt_score, tt_move = tt_probe(gamestate.board, depth, alpha, beta)
    if tt_hit:
        return tt_score
    if depth == 0:
        return quiescence_search(gamestate, alpha, beta)
    if (do_null and
            depth >= 3 and
            not gamestate.board.is_check() and
            has_non_pawn_material(gamestate.board)):
        gamestate.board.push(chess.Move.null())
        score = -negamax(gamestate, depth - 1 - NULL_MOVE_REDUCTION, -beta, -beta + 1, do_null=False)
        gamestate.board.pop()

        if score >= beta:
            return beta
    legal_moves = list(gamestate.get_legal_moves())
    if not legal_moves:
        return evaluate_board(gamestate.board)

    legal_moves = order_moves(gamestate.board, legal_moves, depth, tt_move)

    best_score = float('-inf')
    best_move = None
    moves_searched = 0

    for move in legal_moves:
        gamestate.make_move(move)

        if moves_searched >= LMR_THRESHOLD and depth >= 3 and not gamestate.board.is_check() and not gamestate.board.is_capture(move) and not move.promotion:
            score = -negamax(gamestate, depth - 1 - LMR_REDUCTION, -beta, -alpha)
            if score > alpha:
                score = -negamax(gamestate, depth - 1, -beta, -alpha)
        else:
            score = -negamax(gamestate, depth - 1, -beta, -alpha)

        gamestate.unmake_move()
        moves_searched += 1

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, score)

        if alpha >= beta:
            if not gamestate.board.is_capture(move) and depth < MAX_DEPTH:
                if killer_moves[depth][0] != move:
                    killer_moves[depth][1] = killer_moves[depth][0]
                    killer_moves[depth][0] = move
                bonus = depth * depth
                history_heuristic[gamestate.board.turn][move.from_square][move.to_square] += bonus
                if history_heuristic[gamestate.board.turn][move.from_square][move.to_square] > 10000:
                    history_heuristic[gamestate.board.turn][move.from_square][move.to_square] //= 2

            break
    if best_score <= alpha_orig:
        flag = TTEntry.UPPER
    elif best_score >= beta:
        flag = TTEntry.LOWER
    else:
        flag = TTEntry.EXACT
    tt_store(gamestate.board, depth, best_score, flag, best_move)

    return best_score


def search_root(gamestate: GameState, depth: int) -> tuple[chess.Move, float]:
    alpha = float('-inf')
    beta = float('inf')

    legal_moves = list(gamestate.get_legal_moves())
    if not legal_moves:
        return None, evaluate_board(gamestate.board)
    tt_move = tt_probe(gamestate.board, 0, alpha, beta)[2]
    legal_moves = order_moves(gamestate.board, legal_moves, depth, tt_move)

    best_move = legal_moves[0]
    best_score = float('-inf')

    for move in legal_moves:
        gamestate.make_move(move)
        score = -negamax(gamestate, depth - 1, -beta, -alpha)
        gamestate.unmake_move()

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, score)

    return best_move, best_score


def find_best_move(gamestate: GameState, max_depth: int) -> chess.Move:
    global position_count, killer_moves, history_heuristic

    position_count = 0
    killer_moves = [[None, None] for _ in range(MAX_DEPTH)]
    for color in range(2):
        for from_sq in range(64):
            for to_sq in range(64):
                history_heuristic[color][from_sq][to_sq] //= 8

    best_move = None

    print(f"Searching to depth {max_depth}")

    for depth in range(1, max_depth + 1):
        move, score = search_root(gamestate, depth)
        if move:
            best_move = move

        print(f"Depth {depth}: {best_move} | Score: {score:.2f} | Nodes: {position_count}")

    print(f"Final: {best_move} after {position_count} positions")
    print("-" * 50)

    return best_move

def has_non_pawn_material(board: chess.Board) -> bool:
    """Check if side to move has non-pawn pieces (avoid zugzwang in null move)"""
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.color == board.turn and piece.piece_type != chess.PAWN:
            return True
    return False