# Rock, Paper, Scissors Game

# Import Libraries
import random

# Creating a list of options
options = ["ROCK", "PAPER", "SCISSORS"]

# Creating a function to play the game
def play():
    # Getting the user's choice
    user_choice = input("Choose Rock, Paper or Scissors: ").upper()
    
    # Getting the computer's choice
    computer_choice = random.choice(options)
    
    # Checking if the user's choice is valid
    while user_choice not in options:
        user_choice = input("Invalid input. Choose Rock, Paper or Scissors: ").upper()
    
    # Checking the user's choice against the computer's choice    
    if user_choice.upper() == computer_choice.upper():
        print(f"Computer chose {computer_choice}. It's a tie!")
    elif user_choice.upper() == "ROCK" and computer_choice.upper() == "SCISSORS":
        print(f"Computer chose {computer_choice}. You win!")
    elif user_choice.upper() == "PAPER" and computer_choice.upper() == "ROCK":
        print(f"Computer chose {computer_choice}. You win!")
    elif user_choice.upper() == "SCISSORS" and computer_choice.upper() == "PAPER":
        print(f"Computer chose {computer_choice}. You win!")
    else:
        print(f"Computer chose {computer_choice}. You lose!")
        
        
# Playing the game
while True:
    play()
    play_again = input("Do you want to play again? (y/n): ")
    if play_again.lower() != "y":
        break
    
print("Thanks for playing!")