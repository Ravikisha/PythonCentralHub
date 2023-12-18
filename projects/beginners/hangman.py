# Hangman game
# -----------------------------------

# Importing the random module
import random
import time

# Inputting the name of the user
name = input("What is your name? ")
print("Good Luck ! ", name)

time.sleep(1)

print("The game is about to start !")
print("Let's play Hangman")

time.sleep(1)

open_file = open("words.txt", "r")
words = open_file.readlines()

# Function will choose one random
# word from this list of words
word = random.choice(words)
word = word.lower().strip().replace("\n", "").replace("\r", "").replace(" ", "").replace("-", "")
print("Guess the characters")

guesses = ''
turns = len(word) * 2 

# Checks if the turns are more than zero
while turns > 0:
    failed = 0

    # for every character in secret_word
    for char in word:

        # see if the character is in the players guess
        if char in guesses:
            print(char, end="")

        else:
            print("_", end="")

            # and increase the failed counter with one
            failed += 1

    if failed == 0:
        print("\nYou Win")

        # this print the correct word
        print("The word is: ", word)
        break

    # if failed equals to zero
    # then you will get this message
    if turns == 1:
        print("\nYou have", turns, 'more guess')
    else:
        print("\nYou have", turns, 'more guesses')

    guess = input("guess a character: ")

    # every input character will be stored in guesses
    guesses += guess

    # check input with the character in word
    if guess not in word:

        turns -= 1

        # if the character doesn’t match the word
        # then “Wrong” will be given as output
        print("Wrong")

        # this will print the number of
        # turns left for the user
        if turns == 1:
            print("\nYou have", turns, 'more guess')
        else:
            print("\nYou have", turns, 'more guesses')

        if turns == 0:
            print("\nYou Loose")
            print("\nThe word is: ", word)
            break
