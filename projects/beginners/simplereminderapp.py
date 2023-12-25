# Simple Reminder App

# Import Modules
import time
import datetime
from plyer import notification

# Defining Functions
def print_pause(message_to_print):
    print(message_to_print)
    time.sleep(2)
    
def reminder():
    print_pause("What would you like to be reminded about?")
    reminder = input("Enter your reminder: ")
    print_pause("In how many minutes would you like to be reminded?")
    minutes = input("Enter minutes: ")
    print_pause("Reminder set!")
    time.sleep(int(minutes) * 60)
    notification.notify(
        title = "Reminder",
        message = reminder,
        timeout = 10
    )
    print_pause("Reminder: " + reminder)
    print_pause("Reminder Completed!")
    play_again()
    
def play_again():
    print_pause("Would you like to set another reminder?")
    while True:
        choice = input("Enter yes or no: ")
        if choice == "yes":
            print_pause("Great!")
            reminder()
            break
        elif choice == "no":
            print_pause("Thank you for using the Reminder App!")
            break
        else:
            print_pause("Please enter yes or no: ")
            
def intro():
    print_pause("Welcome to the Reminder App!")
    print_pause("This app will remind you about anything you want!")
    print_pause("Let's get started!")
    reminder()
    
# Calling Functions
intro()