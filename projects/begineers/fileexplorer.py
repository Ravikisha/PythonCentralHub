# Basic File Explorer in Python

import tkinter as tk # pip install tk
from tkinter import *
from tkinter import filedialog, Text

root = tk.Tk()
apps = []

def browseFiles():
    output.delete('1.0', END)
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("Text files","*.txt*"), ("all files", "*.*")))
    pathh.config(text = "Path: " + filename)
    tf = open(filename, encoding="utf8")
    data = tf.read()
    output.insert(END, data)
    tf.close()   
    
        
root.title("File Explorer")
root.geometry("700x700")
root.config(background="white")

label_file_explorer = Label(root, text = "File Explorer using Tkinter", width = 100, height = 3, fg = "gray", bg = "whitesmoke")

button_explore = Button(root, text = "Browse Files", command = browseFiles)
exit_button = Button(root, text = "Exit", command = root.destroy)
output = Text(root)
pathh = Label(root, text = "Path: ", width = 100, height = 3, fg = "gray", bg = "whitesmoke")

label_file_explorer.grid(column = 1, row = 1)
button_explore.grid(column = 1, row = 2)
exit_button.grid(column = 1, row = 3)
output.grid(column = 1, row = 4)
pathh.grid(column = 1, row = 5)

root.mainloop()