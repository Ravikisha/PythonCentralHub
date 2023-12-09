# Dice Rolling Simulator

# Import random module
import random

# Creating a function to roll the dice
def roll():
    return random.randint(1, 6)

# Rolling the dice
while True:
    print(f"You rolled {roll()}")
    play_again = input("Do you want to roll again? (y/n): ")
    if play_again.lower() != "y":
        break
    
print("Thanks for playing!")