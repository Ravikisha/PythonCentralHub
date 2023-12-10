# Number Guessing Game with AI
# Credits: https://gist.github.com/ashishanand7/61bb95a556e1575a63b1745c5fd48a4a

import random

print("NUMBER GUESSING GAME . YOU vs AI \n AI's turn is first\n")
print('Think of a number a number between 0 and 100. ')
input('Press Enter when done')

m=50
j=100
i=0
c=0
print('\nAnswer with:\n "h" if your number is bigger.\n "l" if your number is smaller.\n "y" if AI guesses the correct number')
while True:
    x=input('is it '+str(m)+' ?\n')
    c+=1
    if x=="y":
        print("BINGO")
        break
    elif x=="h":
        i=m
        m=round(((m+j)/2),0)
    elif x=="l":
        j=m
        m=round(((m+i)/2),0)
    else:
        print("Invalid input")
        c-=1

print("Now it's your turn to guess which number computer has thought of between 0 and 100")
a=random.randint(0,101)
d=0
while True:
    x=int(input('Tell which number AI has picked between 0 & 100\n'))
    d+=1
    if x==a:
        print('BINGO . You guessed right.')
        break
    elif x<a:
        print('you guessed too low .')
    elif x>a:
        print('you guessed too high .')

if c<d:
    print("The AI guessed it in ",c," rounds while you took ",d," rounds .\n  AI WINS :D\n Robots are your Overlords . Accept it !!!")
elif c==d:
    print("Both AI & you took ",c," rounds . So , it's a TIE :|")
else:
    print("The AI guessed it in ",c," rounds while you took ",d," rounds .\nYOU WON :\ \nSavour the few wins left before robots outsmart you forever ...")