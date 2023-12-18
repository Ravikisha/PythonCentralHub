# Basic Paint Application in Python

from tkinter import *
from tkinter import ttk
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import filedialog
import PIL
from PIL import ImageGrab
import os

class Paint:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint")
        self.root.geometry("800x520")
        self.root.configure(background="white")
        self.root.resizable(0,0)
        self.root.bind("<B1-Motion>", self.paint)
        self.root.bind("<ButtonRelease-1>", self.reset)
        
        self.pen_color = "black"
        self.eraser_color = "white"
        
        self.color_frame = LabelFrame(self.root, text="Color", font=("arial", 15), bd=5, relief=RIDGE, bg="white")
        self.color_frame.place(x=0, y=0, width=70, height=185)
        
        colors = ["#ff0000", "#ff4000", "#ff8000", "#ffbf00", "#ffff00", "#bfff00", "#80ff00", "#40ff00", "#00ff00", "#00ff40", "#00ff80", "#00ffbf", "#00ffff", "#00bfff", "#0080ff", "#0040ff", "#0000ff", "#4000ff", "#8000ff", "#bf00ff", "#ff00ff", "#ff00bf", "#ff0080", "#ff0040", "#ff0000", "#000000", "#ffffff"]
        
        i=j=0
        for color in colors:
            Button(self.color_frame, bg=color, bd=2, relief=RIDGE, width=3, command=lambda col=color:self.select_color(col)).grid(row=i, column=j)
            i+=1
            if i==23:
                i=0
                j=1
                
        self.eraser_button = Button(self.root, text="Eraser", bd=4, bg="white", command=self.eraser, width=8, relief=RIDGE)
        self.eraser_button.place(x=0, y=187)
        
        self.clear_button = Button(self.root, text="Clear", bd=4, bg="white", command=lambda :self.canvas.delete("all"), width=8, relief=RIDGE)
        self.clear_button.place(x=0, y=217)
        
        self.save_button = Button(self.root, text="Save", bd=4, bg="white", command=self.save_paint, width=8, relief=RIDGE)
        self.save_button.place(x=0, y=247)
        
        self.canvas_color_button = Button(self.root, text="Canvas", bd=4, bg="white", command=self.canvas_color, width=8, relief=RIDGE)
        
        self.canvas_color_button.place(x=0, y=277)
        
        self.canvas_width = Scale(self.root, from_=1, to=100, orient=VERTICAL)
        self.canvas_width.set(1)
        
        self.canvas_width.place(x=0, y=330)
        
        self.canvas = Canvas(self.root, bg="white", bd=5, relief=GROOVE, height=500, width=700)
        self.canvas.place(x=80, y=0)
        
    def paint(self, event):
        x1, y1 = (event.x-2), (event.y-2)
        x2, y2 = (event.x+2), (event.y+2)
        
        self.canvas.create_oval(x1, y1, x2, y2, fill=self.pen_color, outline=self.pen_color, width=self.canvas_width.get())
        
    def select_color(self, col):
        self.pen_color = col
        
    def eraser(self):
        self.pen_color = self.eraser_color
        
    def reset(self, event):
        self.old_x = None
        self.old_y = None
        
    def canvas_color(self):
        color = colorchooser.askcolor(title="Select Color")
        self.canvas.configure(background=color[1])
        self.eraser_color = color[1]
        
    def save_paint(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".jpg")
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()
            PIL.ImageGrab.grab().crop((x,y,x1,y1)).save(filename)
            messagebox.showinfo("Paint says", "Image is saved as " + str(os.path.basename(filename)) + " successfully")
        except:
            messagebox.showerror("Paint says", "Unable to save image")
            
if __name__ == "__main__":
    root = Tk()
    p = Paint(root)
    root.mainloop()
    