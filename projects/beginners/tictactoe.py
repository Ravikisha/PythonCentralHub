# Tic-Tac-Toe Game

import random

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # 3x3 board
        self.current_player = 'X'
    
    def display_board(self):
        """Display the current board state"""
        print("\n   |   |   ")
        print(f" {self.board[0]} | {self.board[1]} | {self.board[2]} ")
        print("___|___|___")
        print("   |   |   ")
        print(f" {self.board[3]} | {self.board[4]} | {self.board[5]} ")
        print("___|___|___")
        print("   |   |   ")
        print(f" {self.board[6]} | {self.board[7]} | {self.board[8]} ")
        print("   |   |   ")
        print("\nPositions:")
        print(" 1 | 2 | 3 ")
        print(" 4 | 5 | 6 ")
        print(" 7 | 8 | 9 ")
    
    def make_move(self, position, player):
        """Make a move on the board"""
        if self.board[position] == ' ':
            self.board[position] = player
            return True
        return False
    
    def check_winner(self):
        """Check if there's a winner"""
        # Winning combinations
        win_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for combo in win_combinations:
            if (self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' '):
                return self.board[combo[0]]
        
        return None
    
    def is_board_full(self):
        """Check if the board is full"""
        return ' ' not in self.board
    
    def get_available_moves(self):
        """Get list of available moves"""
        return [i for i, spot in enumerate(self.board) if spot == ' ']
    
    def computer_move(self):
        """Simple AI for computer moves"""
        available_moves = self.get_available_moves()
        
        # Check if computer can win
        for move in available_moves:
            self.board[move] = 'O'
            if self.check_winner() == 'O':
                self.board[move] = ' '
                return move
            self.board[move] = ' '
        
        # Check if need to block player
        for move in available_moves:
            self.board[move] = 'X'
            if self.check_winner() == 'X':
                self.board[move] = ' '
                return move
            self.board[move] = ' '
        
        # Take center if available
        if 4 in available_moves:
            return 4
        
        # Take corners
        corners = [0, 2, 6, 8]
        available_corners = [move for move in corners if move in available_moves]
        if available_corners:
            return random.choice(available_corners)
        
        # Take any available move
        return random.choice(available_moves)
    
    def play_vs_computer(self):
        """Play against computer"""
        print("Welcome to Tic-Tac-Toe!")
        print("You are X, Computer is O")
        
        while True:
            self.display_board()
            
            if self.current_player == 'X':
                # Player's turn
                try:
                    position = int(input("Enter your move (1-9): ")) - 1
                    if position < 0 or position > 8:
                        print("Invalid position! Choose 1-9.")
                        continue
                    
                    if not self.make_move(position, 'X'):
                        print("Position already taken! Choose another.")
                        continue
                
                except ValueError:
                    print("Invalid input! Enter a number 1-9.")
                    continue
            
            else:
                # Computer's turn
                position = self.computer_move()
                self.make_move(position, 'O')
                print(f"Computer chooses position {position + 1}")
            
            # Check for winner
            winner = self.check_winner()
            if winner:
                self.display_board()
                if winner == 'X':
                    print("🎉 You win!")
                else:
                    print("💻 Computer wins!")
                break
            
            # Check for tie
            if self.is_board_full():
                self.display_board()
                print("🤝 It's a tie!")
                break
            
            # Switch player
            self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def play_two_players(self):
        """Play with two human players"""
        print("Welcome to Tic-Tac-Toe!")
        print("Player 1 is X, Player 2 is O")
        
        while True:
            self.display_board()
            
            # Current player's turn
            player_name = "Player 1" if self.current_player == 'X' else "Player 2"
            
            try:
                position = int(input(f"{player_name} ({self.current_player}), enter your move (1-9): ")) - 1
                if position < 0 or position > 8:
                    print("Invalid position! Choose 1-9.")
                    continue
                
                if not self.make_move(position, self.current_player):
                    print("Position already taken! Choose another.")
                    continue
            
            except ValueError:
                print("Invalid input! Enter a number 1-9.")
                continue
            
            # Check for winner
            winner = self.check_winner()
            if winner:
                self.display_board()
                winner_name = "Player 1" if winner == 'X' else "Player 2"
                print(f"🎉 {winner_name} wins!")
                break
            
            # Check for tie
            if self.is_board_full():
                self.display_board()
                print("🤝 It's a tie!")
                break
            
            # Switch player
            self.current_player = 'O' if self.current_player == 'X' else 'X'

def main():
    """Main function to start the game"""
    while True:
        print("\n" + "="*30)
        print("TIC-TAC-TOE GAME")
        print("="*30)
        print("1. Play vs Computer")
        print("2. Two Players")
        print("3. Exit")
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == '1':
            game = TicTacToe()
            game.play_vs_computer()
        
        elif choice == '2':
            game = TicTacToe()
            game.play_two_players()
        
        elif choice == '3':
            print("Thanks for playing!")
            break
        
        else:
            print("Invalid choice! Please choose 1, 2, or 3.")
        
        # Ask if want to play again
        if choice in ['1', '2']:
            play_again = input("\nPlay again? (y/n): ").lower()
            if play_again != 'y':
                print("Thanks for playing!")
                break

if __name__ == "__main__":
    main()
