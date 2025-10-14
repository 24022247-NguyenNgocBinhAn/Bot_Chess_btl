# ui.py (compact version)
import tkinter as tk
import threading
import chess
import chess.svg
import src
from src.search import find_best_move
from src.board import GameState

PIECES = {
    ('P', True): '♙', ('N', True): '♘', ('B', True): '♗', ('R', True): '♖', ('Q', True): '♕', ('K', True): '♔',
    ('P', False): '♟', ('N', False): '♞', ('B', False): '♝', ('R', False): '♜', ('Q', False): '♛', ('K', False): '♚',
}

LIGHT = "#F0D9B5"
DARK = "#B58863"
HIGHLIGHT = "#F7EC6E"


class ChessUI(tk.Tk):
    def __init__(self, difficulty: int = 3, player_color: str = "white"):
        super().__init__()
        self.title("PyChess UI (Compact)")
        self.resizable(False, False)
        self.game = GameState()
        self.difficulty = difficulty
        self.player_color = chess.WHITE if player_color.lower() == "white" else chess.BLACK
        self.selected_square = None
        self.buttons = {}
        self.status = tk.StringVar(value="Your turn (White starts)")
        self._create_board()
        self._draw_board()

        if self.game.board.turn != self.player_color:
            self.after(500, self.ai_move)

    def _create_board(self):
        for r in range(8):
            for c in range(8):
                btn = tk.Button(
                    self,
                    width=3, height=1,  # nhỏ hơn trước (width 4, height 2)
                    font=("Segoe UI Symbol", 20),  # giảm từ 28 → 20
                    command=lambda rr=r, cc=c: self.on_click(rr, cc)
                )
                btn.grid(row=r, column=c, padx=0, pady=0)
                self.buttons[(r, c)] = btn

        tk.Label(self, textvariable=self.status, font=("Arial", 10)).grid(row=8, column=0, columnspan=8, pady=4)

    def _draw_board(self):
        for r in range(8):
            for c in range(8):
                square = chess.square(c, 7 - r)
                piece = self.game.board.piece_at(square)
                color = LIGHT if (r + c) % 2 == 0 else DARK
                text = PIECES.get((piece.symbol().upper(), piece.color), '') if piece else ''
                self.buttons[(r, c)].config(text=text, bg=color)

        if self.selected_square is not None:
            r, c = self._square_to_rc(self.selected_square)
            self.buttons[(r, c)].config(bg=HIGHLIGHT)

    def on_click(self, r, c):
        if self.game.is_game_over() or self.game.board.turn != self.player_color:
            return

        sq = chess.square(c, 7 - r)
        piece = self.game.board.piece_at(sq)

        if self.selected_square is None:
            if piece and piece.color == self.game.board.turn:
                self.selected_square = sq
        else:
            move = chess.Move(self.selected_square, sq)
            if move in self.game.board.legal_moves:
                self.game.make_move(move)
                self.selected_square = None
                self._draw_board()
                self._check_game_over()
                if not self.game.is_game_over():
                    self.after(200, self.ai_move)
                return
            else:
                self.selected_square = None

        self._draw_board()

    def ai_move(self):
        """AI xử lý trong luồng riêng để không làm đơ giao diện."""
        def worker():
            self.status.set("AI is thinking...")
            ai_move = find_best_move(self.game, self.difficulty)
            if ai_move:
                print(f"AI plays: {self.game.board.san(ai_move)}")
                self.game.make_move(ai_move)
            self.status.set("Your turn" if self.game.board.turn == self.player_color else "")
            self._draw_board()
            self._check_game_over()

        threading.Thread(target=worker, daemon=True).start()

    def _check_game_over(self):
        if self.game.is_game_over():
            result = self.game.board.result()
            self.status.set(f"Game Over — Result: {result}")
            print(f"Game Over. Result: {result}")

    def _square_to_rc(self, square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        return (7 - rank, file)


if __name__ == "__main__":
    app = ChessUI(difficulty=3, player_color="white")
    app.mainloop()
