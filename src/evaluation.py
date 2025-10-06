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

def evaluate_board(board: chess.Board):
    total_score = 0
    total_piece_count = count_pieces_both_sides(board)
    current_phase_score = 0
    for piece_type, count in total_piece_count.items():
        if piece_type in PHASE_VALUES:
            current_phase_score += count * PHASE_VALUES[piece_type]

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_type = piece.piece_type
            color = piece.color
            score_multiply = 0
            if color == chess.WHITE:
                score_multiply = 1
            else:
                score_multiply = -1

            piece_score = piece_values[piece_type]
            pst_type = PST[piece_type]
            mg_score = PST[piece_type][0]
            eg_score = PST[piece_type][1]

            # if color == chess.WHITE:
            #     mg_s