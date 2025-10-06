import chess

def evaluate_board(board):
    total_score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_type = piece.piece_type
            color = piece.color
            if color == chess.WHITE:
