# Random Password Generator

import random
import string


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

def randompasswordgenerator():
    print("Random Password Generator")
    print("Enter the length of password: ")
    length = int(ask("", "16"))
    password = ''
    for i in range(length):
        password += random.choice(string.ascii_letters + string.digits + string.punctuation)
    print(password)
    
if __name__ == "__main__":
    randompasswordgenerator()