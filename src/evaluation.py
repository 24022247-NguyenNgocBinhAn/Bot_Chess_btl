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
def get_doubled_pawns_penalty(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    my_pawns = board.pieces(chess.PAWN, color)
    doubled_pawn_count = 0

    for file_i in range(8):
        file_mask = FILE_MASKS[file_i]
        pawns_on_file = my_pawns & file_mask

        count = len(pawns_on_file)
        if count > 1:
            doubled_pawn_count += (count - 1)

    if doubled_pawn_count == 0:
        return (0,0)

    mg_penalty = doubled_pawn_count * DOUBLE_PAWNS_PENALTY_MG
    eg_penalty = doubled_pawn_count * DOUBLE_PAWNS_PENALTY_EG

    if mg_penalty == 0:
        return (0,0)

    return (mg_penalty,eg_penalty)

def get_isolated_pawns_penalty(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    mg_penalty = 0
    eg_penalty = 0
    my_pawns = board.pieces(chess.PAWN, color)

    for pawn_square in my_pawns:
        file_i = chess.square_file(pawn_square)
        adjacent_mask = ADJACENT_FILES_MASKS[file_i]
        file_open = is_file_semi_open(board, file_i, not color)

        if not (my_pawns & adjacent_mask) and file_open:
            mg_penalty += ISOLATED_PAWNS_SEMI_OPEN_MG
            eg_penalty += ISOLATED_PAWNS_SEMI_OPEN_EG
        elif not (my_pawns & adjacent_mask) and not file_open:
            mg_penalty += ISOLATED_PAWNS_PENALTY_MG
            eg_penalty += ISOLATED_PAWNS_PENALTY_EG

    return (mg_penalty, eg_penalty)


def get_passed_pawn_bonus(board: chess.Board, color: chess.Color) -> tuple[int, int]:
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

    return (mg_value, eg_value)

def get_backward_pawn_penalty(board: chess.Board, color: chess.Color) -> tuple[int, int]:
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
        return (0,0)

    return (mg_penalty, eg_penalty)

def get_pawn_value(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    doubled_pawn_mg, doubled_pawn_eg = get_doubled_pawns_penalty(board, color)
    isolated_pawn_mg, isolated_pawn_eg = get_isolated_pawns_penalty(board, color)
    passed_pawn_mg, passed_pawn_eg = get_passed_pawn_bonus(board, color)
    backward_pawn_mg, backward_pawn_eg = get_backward_pawn_penalty(board, color)
    return (doubled_pawn_mg + isolated_pawn_mg + passed_pawn_mg + backward_pawn_mg, doubled_pawn_eg + isolated_pawn_eg + passed_pawn_eg + backward_pawn_eg)

## PAWN VALUE SUB FUNCTION END

# ROOK ON SEMI AND OPEN FILES
def get_rook_bonus(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    my_rooks = board.pieces(chess.ROOK, color)
    mg_bonus = 0
    eg_bonus = 0
    for rook_square in my_rooks:
        if is_file_semi_open(board, chess.square_file(rook_square), color):
            mg_bonus += ROOK_SEMI_OPEN_FILES_BONUS_MG
            eg_bonus += ROOK_SEMI_OPEN_FILES_BONUS_EG
            continue
        if is_file_open(board, chess.square_file(rook_square)):
            mg_bonus += ROOK_OPEN_FILES_BONUS_MG
            eg_bonus += ROOK_OPEN_FILES_BONUS_EG

    return (mg_bonus, eg_bonus)

# DOUBLE BISHOP
def get_double_bishop_bonus(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    my_bishop = board.pieces((chess.BISHOP, color))
    if len(my_bishop) == 2:
        return (DOUBLE_BISHOP_BONUS_MG, DOUBLE_BISHOP_BONUS_EG)
    return (0, 0)

def sub_piece_value(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    rook_bonus_mg, rook_bonus_eg = get_rook_bonus(board, color)
    double_bishop_bonus_mg, double_bishop_bonus_eg = get_double_bishop_bonus(board, color)
    return (rook_bonus_mg + double_bishop_bonus_mg, rook_bonus_eg + double_bishop_bonus_eg)

## KING SAFETY SUB FUNCTIONS
def pawn_shield_penalty(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    mg_penalty = 0
    eg_penalty = 0
    king_square = board.king(color)
    king_file = chess.square_file(king_square)
    king_rank = chess.square_rank(king_square)

    if king_file < 3 or king_file > 4:
        shield_files = []
        if king_file <= 2:
            shield_files = [0, 1, 2]
        else:
            shield_files = [5, 6, 7]

        pawn_rank = -1
        if color == chess.WHITE:
            pawn_rank = 1
        else:
            pawn_rank = 6
        my_pawns = board.pieces(chess.PAWN, color)

        for file in shield_files:
            shield_square = chess.square(file, pawn_rank)
            piece = board.piece_at(shield_square)

            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                if chess.square_rank(shield_square) != pawn_rank:
                    mg_penalty += ADVANCED_PAWN_SHIELD_PENALTY_MG
                    eg_penalty += ADVANCED_PAWN_SHIELD_PENALTY_EG
            else:
                mg_penalty += MISSING_PAWN_SHIELD_PENALTY_MG
                eg_penalty += MISSING_PAWN_SHIELD_PENALTY_EG

    return (mg_penalty, eg_penalty)


def king_attack_zone_penalty(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    king_square = board.king(color)
    opponent_color = not color

    attack_zone = chess.SquareSet(chess.BB_KING_ATTACKS[king_square])
    attack_zone.add(king_square)

    value_of_attacks = 0
    attacker_count = 0

    for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        opponent_pieces = board.pieces(piece_type, opponent_color)
        for piece_square in opponent_pieces:
            attacks = board.attacks(piece_square)

            attacks_in_zone = attacks & attack_zone

            if attacks_in_zone:
                attacker_count += 1
                value_of_attacks += len(attacks_in_zone) * KING_ATTACK_ZONE_WEIGHTS[piece_type]

    if attacker_count == 0:
        return 0

    multiplier_index = min(attacker_count, len(ATTACK_WEIGHT_MULTIPLIER) - 1)
    attack_multiplier = ATTACK_WEIGHT_MULTIPLIER[multiplier_index]
    final_penalty = (value_of_attacks * attack_multiplier)/100

    return (int(final_penalty), 0)

def get_king_safety_penalty(board: chess.Board, color: chess.Color) -> tuple[int, int]:
    king_shield_mg, king_shield_eg = pawn_shield_penalty(board, color)
    king_attack_zone_penalty_mg = king_attack_zone_penalty(board, color)[0]
    return (king_shield_mg + king_attack_zone_penalty_mg, king_shield_eg)

## KING SAFETY SUB FUNCTIONS END
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

    for color in [chess.WHITE, chess.BLACK]:
        pawn_mg, pawn_eg = get_pawn_value(board, color)
        sub_piece_mg, sub_piece_eg = sub_piece_value(board, color)
        king_safety_mg, king_safety_eg = get_king_safety_penalty(board, color)
        mg_total_score += pawn_mg + sub_piece_mg + king_safety_mg
        eg_total_score += pawn_eg + sub_piece_eg + king_safety_eg

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