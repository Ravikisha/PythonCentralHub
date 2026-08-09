# Guess the number game

import random


def ask(prompt="", default=""):
    """Read a line, or fall back to `default` when nobody is there to type.

    Without this the script raises EOFError the moment it runs unattended — in
    a test, a scheduled job, or the build that captures this output for the
    docs. The fallback is printed rather than silent, so a reader can always
    tell which answers were typed and which were assumed.
    """
    try:
        return input(prompt).strip() or default
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default

print('Hello, what is your name?')
name = ask("", '1')

print('Well, ' + name + ', I am thinking of a number between 1 and 20.')
secretNumber = random.randint(1, 20)

for guessesTaken in range(1, 7):
    print('Take a guess. You have ' + str(7 - guessesTaken) + ' guesses left.')
    guess = int(ask("", '1'))

    if guess < secretNumber:
        print('Your guess is too low.')
    elif guess > secretNumber:
        print('Your guess is too high.')
    else: 
        break # This condition is the correct guess!
    
if guess == secretNumber:
    print('Good job, ' + name + '! You guessed my number in ' + str(guessesTaken) + ' guesses.')
else:
    print('Nope. The number I was thinking of was ' + str(secretNumber) + '.')