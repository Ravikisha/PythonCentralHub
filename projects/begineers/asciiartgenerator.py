# ASCII Art Generator

import pyfiglet # pip install pyfiglet
import termcolor # pip install termcolor
import colorama
import os

def asciiartgenerator():
    print("ASCII Art Generator")
    print("Enter the text to convert to ASCII Art: ")
    text = input()
    print("Enter the color of the text: ")
    color = input()
    print('''
    3-d	
3x5	
5lineoblique
acrobatic
alligator
alligator2
alphabet
avatar
banner
banner3-D
banner3
banner4
barbwire
basic
bell
big
bigchief
binary
block
bubble
bulbhead
calgphy2
caligraphy
catwalk
chunky
coinstak
colossal
computer
contessa	
contrast
cosmic
cosmike
cricket
cursive
cyberlarge
cybermedium
cybersmall
diamond
digital
doh
doom
dotmatrix
drpepper
eftichess
eftifont
eftipiti
eftirobot
eftitalic
eftiwall
eftiwater
epic
fender
fourtops
fuzzy
goofy	
gothic
graffiti
hollywood
invita
isometric1
isometric2
isometric3
isometric4
italic
ivrit	
jazmine	
jerusalem
katakana
kban
larry3d
lcd
lean
letters
linux
lockergnome	
madrid
marquee
maxfour
mike
mini
mirror
mnemonic	
morse
moscow
nancyj-fancy
nancyj-underlined	
nancyj	
nipples
ntgreek
o8	
ogre
pawp
peaks
pebbles
pepper
poison
puffy
pyramid
rectangles
relief
relief2
rev	
roman
rot13
rounded
rowancap
rozzo
runic
runyc
sblood
script
serifcap	
shadow
short
slant
slide
slscript
small
smisome1
smkeyboard
smscript
smshadow
smslant
smtengwar
speed
stampatello
standard
starwars
stellar
stop
straight	
tanja	
tengwar
term
thick
thin
threepoint
ticks
ticksslant
tinker-toy
tombstone
trek
tsalagi
twopoint
univers
usaflag
wavy
weird
    ''')
    print("Enter the font style: ")
    font = input()
    asciiart = pyfiglet.figlet_format(text, font=font)
    colored_asciiart = termcolor.colored(asciiart, color=color)
    print(colored_asciiart)
    print("Do you want to save the ASCII Art? (y/n)")
    save = input()
    if save == 'y':
        print("Enter the name of the file: ")
        filename = input()
        with open(filename, 'w') as f:
            f.write(colored_asciiart)
        print("File saved successfully!")
    else:
        print("File not saved!")
    print("Do you want to clear the screen? (y/n)")
    clear = input()
    if clear == 'y':
        os.system('cls')
    else:
        print("Thank you for using ASCII Art Generator!")
        
if __name__ == "__main__":
    asciiartgenerator()
    