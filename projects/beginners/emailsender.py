# Basic Email Sender in Python

# Before the using your gmail and password follows these steps:
# 1. Go to your google account
# 2. Click on Security
# 3. Under "Signing in to Google," select 2-Step Verification.
# 4. At the bottom of the page, select App passwords.
# 5. Enter a name that helps you remember where you’ll use the app password.
# 6. Select Generate.
# 7. To enter the app password, follow the instructions on your screen. The app password is the 16-character code that generates on your device.
# 8. Select Done.
# 9. Use Generated Password in the password field
# For More Infomation: https://support.google.com/mail/?p=InvalidSecondFactor

import tkinter as tk # pip install tk
from tkinter import *
import smtplib # pip install smtplib
from tkinter import messagebox
import re


def sendEmail():
    try:
        sender = email.get()
        rec = receiver.get()
        pas = password.get()
        msg = message.get()
        
        # Validating the Email
        if(sender == "Enter Your Email" or rec == "Enter Receiver's Email" or pas == "Enter Your Password" or msg == "Enter Your Message"):
            messagebox.showerror("Error", "Please Enter All The Fields")
            return
        
        # Validate Email Using Regular Expression
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_regex.match(sender):
            messagebox.showerror("Error", "Invalid Email")
            return
        
        if not email_regex.match(rec):
            messagebox.showerror("Error", "Invalid Receiver's Email")
            return
        
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, pas)
        server.sendmail(sender, rec, msg)
        server.quit()
        messagebox.showinfo("Success", "Email Sent Successfully")
        email.delete(0, END)
        receiver.delete(0, END)
        password.delete(0, END)
        message.delete(0, END)
        
        email.insert(0, "Enter Your Email")
        receiver.insert(0, "Enter Receiver's Email")
        password.insert(0, "Enter Your Password")
        message.insert(0, "Enter Your Message")
        
    except Exception as e:
        messagebox.showerror("Error", "Something Went Wrong")
        print(e)
        
root = tk.Tk()
root.title("Email Sender")
root.geometry("700x700")
root.config(background="white")

label_file_explorer = Label(root, text = "Email Sender using Tkinter", width = 100, height = 3, fg = "gray", bg = "whitesmoke")

email = Entry(root, width = 50)
email.insert(0, "Enter Your Email")
receiver = Entry(root, width = 50)
receiver.insert(0, "Enter Receiver's Email")
password = Entry(root, width = 50)
password.insert(0, "Enter Your Password")
message = Entry(root, width = 50)
message.insert(0, "Enter Your Message")
button_explore = Button(root, text = "Send Email", command = sendEmail)
exit_button = Button(root, text = "Exit", command = root.destroy)

label_file_explorer.grid(column = 1, row = 1)
email.grid(column = 1, row = 2)
receiver.grid(column = 1, row = 3)
password.grid(column = 1, row = 4)
message.grid(column = 1, row = 5)
button_explore.grid(column = 1, row = 6)
exit_button.grid(column = 1, row = 7)

root.mainloop()
