# Simple Stopwatch

# Import Modules
import time
import datetime
import tkinter as tk

# Defining Variables
root = tk.Tk()
root.title("Simple Stopwatch")
root.geometry("500x500")
root.resizable(False, False)
root.config(bg="black")

# Defining Functions
def start():
    global running
    running = True
    global count
    count = -1
    counter()
    
def counter():
    global running
    global count
    if running:
        count += 1
        time_label.config(text=str(count))
        time_label.after(1000, counter)
        
def stop():
    global running
    running = False
    
def reset():
    global count
    count = 0
    time_label.config(text=str(count))
    
# Creating Widgets
time_label = tk.Label(root, text="0", font=("Helvetica", 80), bg="black", fg="white")

start_button = tk.Button(root, text="Start", font=("Helvetica", 20), bg="black", fg="white", command=start)
stop_button = tk.Button(root, text="Stop", font=("Helvetica", 20), bg="black", fg="white", command=stop)
reset_button = tk.Button(root, text="Reset", font=("Helvetica", 20), bg="black", fg="white", command=reset)

# Placing Widgets
time_label.pack(pady=20)
start_button.pack(pady=20)
stop_button.pack(pady=20)
reset_button.pack(pady=20)

# Calling Functions
root.mainloop()