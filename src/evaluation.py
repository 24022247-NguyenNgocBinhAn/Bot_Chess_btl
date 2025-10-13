import chess
from src.constant import *

def phase_score_calculator(current_phase_score: int, mg_score: int, eg_score: int) -> float:
    phase = min(current_phase_score, TOTAL_PHASE)  # Cap phase to handle promotions
    return (mg_score*phase + eg_score*(TOTAL_PHASE - phase))/TOTAL_PHASE

def is_file_open(board: chess.Board, file_i: int) -> bool:
    file_mask = FILE_MASKS[file_i]
    all_pawns = board.pieces(chess.PAWN, chess.WHITE) | board.pieces(chess.PAWN, chess.BLACK)
    return not (all_pawns & file_mask)

# check if a file is semi open for current turn
def is_file_semi_open(board: chess.Board, file_i: int, turn: chess.Color) -> bool:
    file_mask = FILE_MASKS[file_i]
    my_pawns = board.pieces(chess.PAWN, turn)
    enemy_pawns = board.pieces(chess.PAWN, not turn)

    condition_1 = not bool(my_pawns & file_mask)
    condition_2 = bool(enemy_pawns & file_mask)

    return condition_1 and condition_2

## PAWN VALUE SUB FUNCTION
def doubled_pawns_penalty(board: chess.Board, color: chess.Color, current_phase_score: int) -> float:
    my_pawns = board.pieces(chess.PAWN, color)
    doubled_pawn_count = 0

    for file_i in range(8):
        file_mask = FILE_MASKS[file_i]
        pawns_on_file = my_pawns & file_mask

        count = len(pawns_on_file)
        if count > 1:
            doubled_pawn_count += (count - 1)

    if doubled_pawn_count == 0:
        return 0

    mg_penalty = doubled_pawn_count * DOUBLE_PAWNS_PENALTY_MG
    eg_penalty = doubled_pawn_count * DOUBLE_PAWNS_PENALTY_EG

    if mg_penalty == 0:
        return 0

    return phase_score_calculator(current_phase_score, mg_penalty, eg_penalty)

def isolated_pawns_penalty(board: chess.Board, color: chess.Color) -> float:
    total_penalty = 0
    my_pawns = board.pieces(chess.PAWN, color)

    for pawn_square in my_pawns:
        file_i = chess.square_file(pawn_square)
        adjacent_mask = ADJACENT_FILES_MASKS[file_i]
        file_open = is_file_semi_open(board, file_i, not color)

        if not (my_pawns & adjacent_mask) and file_open:
            total_penalty += ISOLATED_PAWNS_SEMI_OPEN
        elif not (my_pawns & adjacent_mask) and not file_open:
            total_penalty += ISOLATED_PAWNS_PENALTY

    return total_penalty


def get_passed_pawn_bonus(board: chess.Board, color: chess.Color, current_phase_score: int) -> float:
    my_pawns = board.pieces(chess.PAWN, color)
    opponent_pawns = board.pieces(chess.PAWN, not color)

    mg_value = 0
    eg_value = 0

    mask_table = None
    if color == chess.WHITE:
        mask_table = WHITE_PASSED_PAWN_MASKS
    else:
        mask_table = BLACK_PASSED_PAWN_MASKS

    for pawn_square in my_pawns:
        if not (opponent_pawns & mask_table[pawn_square]):
            rank = chess.square_rank(pawn_square)
            bonus_rank_index = -1
            if color == chess.WHITE:
                bonus_rank_index = rank
            else:
                bonus_rank_index = 7 - rank

            if board.is_attacked_by(color, pawn_square):
                mg_value += PROTECTED_PASSED_PAWN_BONUS_MG[bonus_rank_index]
                eg_value += PROTECTED_PASSED_PAWN_BONUS_EG[bonus_rank_index]
            else:
                mg_value += UNPROTECTED_PASSED_PAWN_BONUS_MG[bonus_rank_index]
                eg_value += UNPROTECTED_PASSED_PAWN_BONUS_EG[bonus_rank_index]

    return phase_score_calculator(current_phase_score, mg_value, eg_value)

def get_backward_pawn_penalty(board: chess.Board, color: chess.Color, current_phase_score: int) -> float:
    my_pawns = board.pieces(chess.PAWN, color)
    mg_penalty = 0
    eg_penalty = 0
    for pawn_square in my_pawns:
        pawn_file = chess.square_file(pawn_square)

        supported_by_pawn = False

        if pawn_file > 0:
            support_left_square = pawn_square
            if color == chess.WHITE:
                support_left_square = pawn_square - 9 
            else:
                support_left_square = pawn_square + 7
            piece_on_left = board.piece_at(support_left_square)
            if piece_on_left and piece_on_left.piece_type == chess.PAWN and piece_on_left.color == color:
                supported_by_pawn = True

        if not supported_by_pawn and pawn_file < 7:
            support_right_square = pawn_square
            if color == chess.WHITE:
                support_right_square = pawn_square - 7
            else:
                support_right_square = pawn_square + 9
            piece_on_right = board.piece_at(support_right_square)
            if piece_on_right and piece_on_right.piece_type == chess.PAWN and piece_on_right.color == color:
                supported_by_pawn = True

        if supported_by_pawn:
            continue

        pawn_ahead_square = pawn_square
        if color == chess.WHITE:
            pawn_ahead_square = pawn_square + 8
        else:
            pawn_ahead_square = pawn_square - 8
        if 0 <= pawn_ahead_square <= 63:
            if board.is_attacked_by(not color, pawn_ahead_square):
                mg_penalty += BACKWARD_PAWN_PENALTY_MG
                eg_penalty += BACKWARD_PAWN_PENALTY_EG

    if mg_penalty == 0:
        return 0.0

    return phase_score_calculator(current_phase_score, mg_penalty, eg_penalty)

def get_pawn_value(board: chess.Board, color: chess.Color, current_phase_score: int) -> float:
    doubled_pawn_penalty = doubled_pawns_penalty(board, color, current_phase_score)
    isolated_pawn_penalty = isolated_pawns_penalty(board, color)
    passed_pawn_bonus = get_passed_pawn_bonus(board, color, current_phase_score)
    backward_pawn_penalty = get_backward_pawn_penalty(board, color, current_phase_score)
    return doubled_pawn_penalty + isolated_pawn_penalty + passed_pawn_bonus + backward_pawn_penalty
## PAWN VALUE SUB FUNCTION END

# ROOK ON SEMI AND OPEN FILES
def get_rook_bonus(board: chess.Board, color: chess.Color) -> int:
    my_rooks = board.pieces(chess.ROOK, color)
    total_bonus = 0
    for rook_square in my_rooks:
        if is_file_semi_open(board, chess.square_file(rook_square), color):
            total_bonus += ROOK_SEMI_OPEN_FILES_BONUS
            break
        if is_file_open(board, chess.square_file(rook_square)):
            total_bonus += ROOK_OPEN_FILES_BONUS
            break

    return total_bonus

# DOUBLE BISHOP
def get_double_bishop_bonus(board: chess.Board, color: chess.Color) -> int:
    my_bishop = board.pieces((chess.BISHOP, color))
    if len(my_bishop) == 2:
        return DOUBLE_BISHOP_BONUS
    return 0

## KING SAFETY SUB FUNCTIONS


def count_pieces_both_sides(board: chess.Board) -> dict:
    total_counts = {}

    for piece_type in chess.PIECE_TYPES:
        count = len(board.pieces(piece_type, chess.WHITE)) + len(board.pieces(piece_type, chess.BLACK))
        total_counts[piece_type] = count

    return total_counts

def evaluate_board(board: chess.Board) -> float:
    total_piece_count = count_pieces_both_sides(board)
    current_phase_score = 0
    for piece_type, count in total_piece_count.items():
        if piece_type in PHASE_VALUES:
            current_phase_score += count * PHASE_VALUES[piece_type]

    mg_total_score = 0
    eg_total_score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            square_view = square
            piece_type = piece.piece_type
            color = piece.color

            piece_score = piece_values[piece_type]
            mg_score = PST[piece_type][0]
            eg_score = PST[piece_type][1]

            if color == chess.WHITE:
                score_multiply = 1

            else:
                score_multiply = -1
                square_view = chess.square_mirror(square)

            mg_pst_score = mg_score[square_view]
            eg_pst_score = eg_score[square_view]

            mg_total_score += (piece_score + mg_pst_score) * score_multiply
            eg_total_score += (piece_score + eg_pst_score) * score_multiply

    final_score = phase_score_calculator(current_phase_score, mg_total_score, eg_total_score)

    if board.turn == chess.WHITE:
        return final_score
    else:
        return -final_score