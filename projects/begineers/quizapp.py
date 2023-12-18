# Basic Quiz App

# Importing Modules
from tkinter import *
from tkinter import messagebox
import random

# Creating Root Window
root = Tk()
root.title("Quiz App")
root.geometry("500x500")
root.resizable(0, 0)
root.config(bg="white")

# Creating Variables
score = 0
ques = 1
ques_num = 1
ans = 0
ans_list = []

# Creating Questions
questions = [
    "What is the Capital of India?",
    "What is the Capital of USA?",
    "What is the Capital of UK?",
    "What is the Capital of China?",
    "What is the Capital of Japan?",
    "What is the Capital of Russia?",
    "What is the Capital of France?",
    "What is the Capital of Germany?",
    "What is the Capital of Brazil?",
    "What is the Capital of Australia?",
]

# Creating Options
options = [
    ["New Delhi", "Mumbai", "Kolkata", "Chennai"],
    ["New York", "Washington DC", "California", "Texas"],
    ["London", "Manchester", "Liverpool", "Birmingham"],
    ["Beijing", "Shanghai", "Hong Kong", "Wuhan"],
    ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
    ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg"],
    ["Paris", "Lyon", "Marseille", "Toulouse"],
    ["Berlin", "Hamburg", "Munich", "Cologne"],
    ["Brasilia", "Rio de Janeiro", "Sao Paulo", "Salvador"],
    ["Sydney", "Melbourne", "Perth", "Brisbane"],
]

# Creating Answers
answers = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]

# Creating Functions
def selected():
    global ans, radio
    global ques_num, ques
    global score, ans_list
    x = 0
    y = 50
    if ques_num == 10:
        submit.config(text="Finish")
    if ans == answers[ques_num - 1]:
        score += 1
        ans_list.append(1)
    else:
        ans_list.append(0)
    ques_num += 1
    ques.config(text=questions[ques_num - 1])
    for i in range(4):
        radio[i].config(text=options[ques_num - 1][i])
    if ques_num == 11:
        messagebox.showinfo("Score", f"Your Score is {score}")
        root.destroy()
        
def submit():
    global ques_num, score, ans_list
    if ques_num == 10:
        submit.config(text="Finish")
    if ans == answers[ques_num - 1]:
        score += 1
        ans_list.append(1)
    else:
        ans_list.append(0)
    ques_num += 1
    ques.config(text=questions[ques_num - 1])
    for i in range(4):
        radio[i].config(text=options[ques_num - 1][i])
    if ques_num == 11:
        messagebox.showinfo("Score", f"Your Score is {score}")
        root.destroy()
        
def back():
    global ques_num, score, ans_list
    if ques_num == 1:
        messagebox.showinfo("Error", "You are at the first question")
    else:
        ques_num -= 1
        score -= ans_list[ques_num - 1]
        ques.config(text=questions[ques_num - 1])
        for i in range(4):
            radio[i].config(text=options[ques_num - 1][i])
        if ques_num == 10:
            submit.config(text="Finish")
        else:
            submit.config(text="Next")
            
def reset():
    global ques_num, score, ans_list
    ques_num = 1
    score = 0
    ans_list = []
    ques.config(text=questions[ques_num - 1])
    for i in range(4):
        radio[i].config(text=options[ques_num - 1][i])
    submit.config(text="Next")
    
def check():
    global ans
    ans = v.get()
    
def shuffle():
    global questions, options, answers
    x = list(zip(questions, options, answers))
    random.shuffle(x)
    questions, options, answers = zip(*x)
    ques.config(text=questions[ques_num - 1])
    for i in range(4):
        radio[i].config(text=options[ques_num - 1][i])
        
def show():
    global ques_num, score, ans_list
    messagebox.showinfo("Score", f"Your Score is {score}")
    root.destroy()
    
# Creating Labels
ques = Label(root, text=questions[ques_num - 1], font=("Helvetica", 20), bg="white")
ques.place(x=50, y=50)

# Creating Radio Buttons
v = IntVar()
radio = []
for i in range(4):
    radio.append(Radiobutton(root, text=options[ques_num - 1][i], font=("Helvetica", 20), bg="white", variable=v, value=i, command=check))
    radio[i].place(x=50, y=100 + i * 50)
    
# Creating Buttons
submit = Button(root, text="Next", font=("Helvetica", 20), bg="white", command=submit)
submit.place(x=50, y=300)
back = Button(root, text="Back", font=("Helvetica", 20), bg="white", command=back)
back.place(x=150, y=300)
reset = Button(root, text="Reset", font=("Helvetica", 20), bg="white", command=reset)
reset.place(x=250, y=300)
shuffle = Button(root, text="Shuffle", font=("Helvetica", 20), bg="white", command=shuffle)
shuffle.place(x=350, y=300)
show = Button(root, text="Show Score", font=("Helvetica", 20), bg="white", command=show)
show.place(x=50, y=400)

# Running Root Window
root.mainloop()