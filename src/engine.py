# engine.py
import chess
from board import GameState
from search import find_best_move


def _get_player_move(board: chess.Board) -> chess.Move:
    while True:
        player_input = input("Enter your move (e.g., 'e4' or 'e2e4'): ")
        try:
            move = board.parse_san(player_input)
            return move
        except ValueError:
            try:
                move = chess.Move.from_uci(player_input)
                if move in board.legal_moves:
                    return move
                else:
                    print("Invalid move. That move is not legal on the current board.")
            except ValueError:
                print("Invalid move format. Please use SAN (e.g., Nf3) or UCI (e.g., g1f3).")


def _print_game_result(game: GameState):
    print(f"\nGame over. Result: {game.board.result()}")
    outcome = game.get_outcome()
    if not outcome:
        return

    if outcome.winner == chess.WHITE:
        winner_str = "White"
    elif outcome.winner == chess.BLACK:
        winner_str = "Black"
    else:
        winner_str = "Draw"
    print(f"Winner: {winner_str}")


def play_game(difficulty: int = 5, color: str = "white"):
    game = GameState()
    player_color = chess.WHITE if color.lower() == "white" else chess.BLACK

    while not game.is_game_over():
        print("\n" + str(game.board))
        if game.turn() == player_color:
            move = _get_player_move(game.board)
            game.make_move(move)
        else:
            print("AI is thinking...")
            ai_move = find_best_move(game, difficulty)
            # Use board.san() to show the move in Standard Algebraic Notation
            print(f"AI plays: {game.board.san(ai_move)}")
            game.make_move(ai_move)

    _print_game_result(game)


if __name__ == "__main__":
    play_game()
