# Dice Rolling Simulator

# Import random module
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

# Creating a function to roll the dice
def roll():
    return random.randint(1, 6)

# Rolling the dice
while True:
    print(f"You rolled {roll()}")
    play_again = ask("Do you want to roll again? (y/n): ", "n")
    if play_again.lower() != "y":
        break
    
print("Thanks for playing!")