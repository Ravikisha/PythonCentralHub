# Random Password Generator

import random
import string

def randompasswordgenerator():
    print("Random Password Generator")
    print("Enter the length of password: ")
    length = int(input())
    password = ''
    for i in range(length):
        password += random.choice(string.ascii_letters + string.digits + string.punctuation)
    print(password)
    
if __name__ == "__main__":
    randompasswordgenerator()