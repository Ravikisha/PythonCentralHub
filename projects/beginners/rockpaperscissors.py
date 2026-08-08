# Rock, Paper, Scissors Game

# Import Libraries
import random


def ask(prompt, default):
    """Read a line, or fall back to `default` when nobody is there to type.

    Without this the script raises EOFError as soon as it runs unattended --
    in a test, a scheduled job, or the documentation build that captures this
    output. The default is what the demo uses.
    """
    try:
        answer = input(prompt)
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default
    return answer.strip() or default

# Creating a list of options
options = ["ROCK", "PAPER", "SCISSORS"]

# Creating a function to play the game
def play():
    # Getting the user's choice
    user_choice = ask("Choose Rock, Paper or Scissors: ", "Rock").upper()
    
    # Getting the computer's choice
    computer_choice = random.choice(options)
    
    # Checking if the user's choice is valid
    while user_choice not in options:
        user_choice = ask("Invalid input. Choose Rock, Paper or Scissors: ", "Rock").upper()
    
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
    play_again = ask("Do you want to play again? (y/n): ", "n")
    if play_again.lower() != "y":
        break
    
print("Thanks for playing!")