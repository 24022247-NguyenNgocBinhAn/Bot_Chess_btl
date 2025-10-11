import chess
from src.constant import PST, PHASE_VALUES
from src.constant import piece_values

def phase_score_calculator(current_phase_score: int, mg_score: int, eg_score: int) -> float:
    phase = current_phase_score/24
    return (mg_score*(24-phase) + eg_score*phase) / 24


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
            score_multiply = 0

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