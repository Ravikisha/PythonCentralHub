"""
Multiplayer Tic-Tac-Toe

A Python-based multiplayer Tic-Tac-Toe game using socket programming. Features include:
- Two players can play over a network.
- Real-time updates of the game board.
"""

import socket
import threading

# Constants
HOST = "127.0.0.1"
PORT = 65432

# Game board
board = [" " for _ in range(9)]
current_player = "X"
lock = threading.Lock()

def print_board():
    """Print the game board."""
    print("\n")
    for i in range(3):
        print(" | ".join(board[i * 3:(i + 1) * 3]))
        if i < 2:
            print("-" * 5)

def check_winner():
    """Check if there is a winner."""
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != " ":
            return board[combo[0]]
    if " " not in board:
        return "Draw"
    return None

def handle_client(conn, addr):
    """Handle communication with a client."""
    global current_player
    conn.sendall("Welcome to Tic-Tac-Toe!\n".encode())
    conn.sendall("You are player {}\n".format(current_player).encode())

    player = current_player
    with lock:
        current_player = "O" if current_player == "X" else "X"

    while True:
        conn.sendall("\n".join(board).encode())
        conn.sendall("\nEnter your move (0-8): ".encode())
        move = conn.recv(1024).decode().strip()

        if not move.isdigit() or int(move) not in range(9):
            conn.sendall("Invalid move. Try again.\n".encode())
            continue

        move = int(move)
        with lock:
            if board[move] == " ":
                board[move] = player
                winner = check_winner()
                if winner:
                    conn.sendall("\nGame Over! Winner: {}\n".format(winner).encode())
                    break
            else:
                conn.sendall("Spot already taken. Try again.\n".encode())

    conn.close()

def main():
    """Main server function."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print("Server started. Waiting for players...")

    while True:
        conn, addr = server.accept()
        print(f"Player connected from {addr}")
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
