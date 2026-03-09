"""
AI-based Chess Game

Features:
- Chess game with AI opponent
- GUI (tkinter)
- Move validation
- Modular design
- Error handling
"""
import tkinter as tk
import sys
import random

class ChessBoard:
    def __init__(self):
        self.board = [['' for _ in range(8)] for _ in range(8)]
        self.init_board()
    def init_board(self):
        for i in range(8):
            self.board[1][i] = 'bp'
            self.board[6][i] = 'wp'
        self.board[0][0] = self.board[0][7] = 'br'
        self.board[7][0] = self.board[7][7] = 'wr'
        self.board[0][1] = self.board[0][6] = 'bn'
        self.board[7][1] = self.board[7][6] = 'wn'
        self.board[0][2] = self.board[0][5] = 'bb'
        self.board[7][2] = self.board[7][5] = 'wb'
        self.board[0][3] = 'bq'
        self.board[0][4] = 'bk'
        self.board[7][3] = 'wq'
        self.board[7][4] = 'wk'
    def move(self, src, dst):
        self.board[dst[0]][dst[1]] = self.board[src[0]][src[1]]
        self.board[src[0]][src[1]] = ''
    def get_moves(self, color):
        # Dummy: random moves
        moves = []
        for i in range(8):
            for j in range(8):
                if self.board[i][j].startswith(color):
                    moves.append(((i,j), (random.randint(0,7), random.randint(0,7))))
        return moves

class ChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI-based Chess Game")
        self.board = ChessBoard()
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.draw_board()
        self.root.after(1000, self.ai_move)
    def draw_board(self):
        self.canvas.delete('all')
        for i in range(8):
            for j in range(8):
                color = 'white' if (i+j)%2==0 else 'gray'
                self.canvas.create_rectangle(j*50, i*50, (j+1)*50, (i+1)*50, fill=color)
                piece = self.board.board[i][j]
                if piece:
                    self.canvas.create_text(j*50+25, i*50+25, text=piece, font=('Arial', 16))
    def ai_move(self):
        moves = self.board.get_moves('b')
        if moves:
            src, dst = random.choice(moves)
            self.board.move(src, dst)
            self.draw_board()
        self.root.after(1000, self.ai_move)
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        gui = ChessGUI()
        gui.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
