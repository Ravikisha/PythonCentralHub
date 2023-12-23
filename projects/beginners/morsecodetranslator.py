# Morse Code Translator

# Importing modules
import winsound
import time
import sys

# Defining variables
morse_code = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', ' ': ' ', ',': '--..--', '.': '.-.-.-', '?': '..--..',
    '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'
}

# Defining functions
def translate_to_morse_code(text):
    morse_code_text = ''
    for letter in text:
        morse_code_text += morse_code[letter.upper()] + ' '
    return morse_code_text

def translate_to_text(morse_code_text):
    text = ''
    morse_code_text += ' '
    letter = ''
    for symbol in morse_code_text:
        if symbol != ' ':
            i = 0
            letter += symbol
        else:
            i += 1
            if i == 2:
                text += ' '
            else:
                text += list(morse_code.keys())[list(morse_code.values()).index(letter)]
                letter = ''
    return text
    
def play_morse_code(morse_code_text):
    for symbol in morse_code_text:
        if symbol == '.':
            winsound.Beep(1000, 100)
        elif symbol == '-':
            winsound.Beep(1000, 300)
        else:
            time.sleep(0.5)
            
def main():
    print('Morse Code Translator')
    print('1. Translate to Morse Code')
    print('2. Translate to Text')
    print('3. Play Morse Code')
    print('4. Exit')
    choice = input('Enter your choice: ')
    if choice == '1':
        text = input('Enter the text to translate to Morse Code: ')
        morse_code_text = translate_to_morse_code(text)
        print('Morse Code: ' + morse_code_text)
        main()
    elif choice == '2':
        morse_code_text = input('Enter the Morse Code to translate to Text: ')
        text = translate_to_text(morse_code_text)
        print('Text: ' + text)
        main()
    elif choice == '3':
        morse_code_text = input('Enter the Morse Code to play: ')
        play_morse_code(morse_code_text)
        main()
    elif choice == '4':
        sys.exit()
    else:
        print('Invalid choice')
        main()
        
# Calling main function
main()
