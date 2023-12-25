# Text Based Adventure Game

# Importing Modules
import time
import random

# Defining Functions
def print_pause(message_to_print):
    print(message_to_print)
    time.sleep(2)
    
def intro():
    print_pause("You find yourself standing in an open field, filled with grass and yellow wildflowers.")
    print_pause("Rumor has it that a wicked fairie is somewhere around here, and has been terrifying the nearby village.")
    print_pause("In front of you is a house.")
    print_pause("To your right is a dark cave.")
    print_pause("In your hand you hold your trusty (but not very effective) dagger.\n")
    
def house(items):
    print_pause("You approach the door of the house.")
    print_pause("You are about to knock when the door opens and out steps a wicked fairie.")
    print_pause("Eep! This is the wicked fairie's house!")
    print_pause("The wicked fairie attacks you!")
    if "Sword of Ogoroth" not in items:
        print_pause("You feel a bit under-prepared for this, what with only having a tiny dagger.")
    while True:
        choice = input("Would you like to (1) fight or (2) run away?")
        if choice == "1":
            if "Sword of Ogoroth" in items:
                print_pause("As the wicked fairie moves to attack, you unsheath your new sword.")
                print_pause("The Sword of Ogoroth shines brightly in your hand as you brace yourself for the attack.")
                print_pause("But the wicked fairie takes one look at your shiny new toy and runs away!")
                print_pause("You have rid the town of the wicked fairie. You are victorious!")
            else:
                print_pause("You do your best...")
                print_pause("but your dagger is no match for the wicked fairie.")
                print_pause("You have been defeated!")
            play_again()
            break
        if choice == "2":
            print_pause("You run back into the field. Luckily, you don't seem to have been followed.")
            field(items)
            break
        
def cave(items):
    print_pause("You peer cautiously into the cave.")
    if "Sword of Ogoroth" in items:
        print_pause("You've been here before, and gotten all the good stuff. It's just an empty cave now.")
        print_pause("You walk back out to the field.")
        field(items)
    else:
        print_pause("It turns out to be only a very small cave.")
        print_pause("Your eye catches a glint of metal behind a rock.")
        print_pause("You have found the magical Sword of Ogoroth!")
        print_pause("You discard your silly old dagger and take the sword with you.")
        print_pause("You walk back out to the field.")
        items.append("Sword of Ogoroth")
        field(items)
        
def field(items):
    print_pause("Enter 1 to knock on the door of the house.")
    print_pause("Enter 2 to peer into the cave.")
    while True:
        choice = input("What would you like to do?")
        if choice == "1":
            house(items)
            break
        elif choice == "2":
            cave(items)
            break
        
def play_again():
    while True:
        choice = input("Would you like to play again? (y/n)")
        if choice == "y":
            print_pause("Excellent! Restarting the game ...")
            play_game()
            break
        elif choice == "n":
            print_pause("Thanks for playing! See you next time.")
            break
        
def play_game():
    items = []
    intro()
    field(items)
    
# Calling Functions
play_game()
