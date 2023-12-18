# Calculator with GUI using Tkinter

from tkinter import *

solution = ""

def press(num):
    global solution
    solution = solution + str(num)
    equation.set(solution)
    
def equalpress():
    try:
        global solution
        total = str(eval(solution))
        equation.set(total)
        solution = ""
    except:
        equation.set(" error ")
        solution = ""
        
def clear():
    global solution
    solution = ""
    equation.set("")
    
if __name__ == "__main__":
    gui = Tk()
    gui.configure(background="light green")
    gui.title("Calculator")
    gui.geometry("270x150")
    equation = StringVar()
    expression_field = Entry(gui, textvariable=equation)
    expression_field.grid(columnspan=4, ipadx=70)
    equation.set('enter your expression')
    button1 = Button(gui, text=' 1 ', fg='black', bg='gray',
                     command=lambda: press(1), height=1, width=7)
    button1.grid(row=2, column=0)
    button2 = Button(gui, text=' 2 ', fg='black', bg='gray',
                     command=lambda: press(2), height=1, width=7)
    button2.grid(row=2, column=1)
    button3 = Button(gui, text=' 3 ', fg='black', bg='gray',
                     command=lambda: press(3), height=1, width=7)
    button3.grid(row=2, column=2)
    button4 = Button(gui, text=' 4 ', fg='black', bg='gray',
                     command=lambda: press(4), height=1, width=7)
    button4.grid(row=3, column=0)
    button5 = Button(gui, text=' 5 ', fg='black', bg='gray',
                     command=lambda: press(5), height=1, width=7)
    button5.grid(row=3, column=1)
    button6 = Button(gui, text=' 6 ', fg='black', bg='gray',
                     command=lambda: press(6), height=1, width=7)
    button6.grid(row=3, column=2)
    button7 = Button(gui, text=' 7 ', fg='black', bg='gray',
                     command=lambda: press(7), height=1, width=7)
    button7.grid(row=4, column=0)
    button8 = Button(gui, text=' 8 ', fg='black', bg='gray',
                     command=lambda: press(8), height=1, width=7)
    button8.grid(row=4, column=1)
    button9 = Button(gui, text=' 9 ', fg='black', bg='gray',
                     command=lambda: press(9), height=1, width=7)
    button9.grid(row=4, column=2)
    button0 = Button(gui, text=' 0 ', fg='black', bg='gray',
                     command=lambda: press(0), height=1, width=7)
    button0.grid(row=5, column=0)
    plus = Button(gui, text=' + ', fg='black', bg='gray',
                  command=lambda: press("+"), height=1, width=7)
    plus.grid(row=2, column=3)
    minus = Button(gui, text=' - ', fg='black', bg='gray',
                   command=lambda: press("-"), height=1, width=7)
    minus.grid(row=3, column=3)
    multiply = Button(gui, text=' * ', fg='black', bg='gray',
                      command=lambda: press("*"), height=1, width=7)
    multiply.grid(row=4, column=3)
    divide = Button(gui, text=' / ', fg='black', bg='gray',
                    command=lambda: press("/"), height=1, width=7)
    divide.grid(row=5, column=3)
    equal = Button(gui, text=' = ', fg='black', bg='gray',
                   command=equalpress, height=1, width=7)
    equal.grid(row=5, column=2)
    clear = Button(gui, text='Clear', fg='black', bg='gray',
                   command=clear, height=1, width=7)
    clear.grid(row=5, column='1')
    Decimal= Button(gui, text='.', fg='black', bg='gray',
                    command=lambda: press('.'), height=1, width=7)
    Decimal.grid(row=6, column=0)
    gui.mainloop()
    