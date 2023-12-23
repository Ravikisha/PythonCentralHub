# Currency Exchange Rate Calculator GUI

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import requests
import json

# Create an instance of tkinter frame
win = Tk()

# Set the geometry of tkinter frame
win.geometry("700x400")

# Set the title of tkinter frame
win.title("Currency Exchange Rate Calculator")

# Disable resizing the GUI by passing in False/False
win.resizable(False, False)

# Create a function to convert currency
def exchange():
    # Get the amount from the amount entry box
    amount = float(amount_entry.get())
    
    # Get the currency from the currency combobox
    currency = currency_combo.get()
    
    # Get the converted currency from the converted currency combobox
    converted_currency = converted_currency_combo.get()
    
    # Create a base URL
    base_url = "https://api.exchangerate-api.com/v4/latest/"
    
    # Create a full URL
    full_url = base_url + currency
    
    # Send a request to the URL
    response = requests.get(full_url)
    
    # Convert the response to JSON format
    response_json = response.json()
    
    # Get the currency rates from the response
    rates = response_json['rates']
    
    # Get the currency rate for the converted currency
    converted_currency_rate = rates[converted_currency]
    
    # Calculate the converted currency amount
    converted_currency_amount = converted_currency_rate * amount
    
    # Round the converted currency amount to 2 decimal places
    converted_currency_amount = round(converted_currency_amount, 2)
    
    # Create a message box to display the converted currency amount
    messagebox.showinfo("Converted Currency Amount", f"{converted_currency_amount} {converted_currency}")
    
# Create a function to clear the GUI
def clear():
    # Clear the amount entry box
    amount_entry.delete(0, END)
    
    # Clear the currency combobox
    currency_combo.set("")
    
    # Clear the converted currency combobox
    converted_currency_combo.set("")
    
# Create a function to exit the GUI
def exit():
    # Exit the GUI
    win.destroy()
    
# Create a label for the amount entry box
amount_label = Label(win, text="Amount:", font=("Arial", 10, "bold"))

# Create a label for the currency combobox
currency_label = Label(win, text="Currency:", font=("Arial", 10, "bold"))

# Create a label for the converted currency combobox
converted_currency_label = Label(win, text="Converted Currency:", font=("Arial", 10, "bold"))

# Create a label for the amount entry box
amount_label.place(x=30, y=50)

# Create a label for the currency combobox
currency_label.place(x=30, y=100)

# Create a label for the converted currency combobox
converted_currency_label.place(x=30, y=150)

# Create a variable for the amount entry box
amount = StringVar()

# Create an entry box for the amount
amount_entry = Entry(win, textvariable=amount, font=("Arial", 10, "normal"), width=20)

# Create a variable for the currency combobox
currency = StringVar()

# Create a combobox for the currency
currency_combo = ttk.Combobox(win, textvariable=currency, font=("Arial", 10, "normal"), width=18)

# Create a variable for the converted currency combobox
converted_currency = StringVar()

# Create a combobox for the converted currency
converted_currency_combo = ttk.Combobox(win, textvariable=converted_currency, font=("Arial", 10, "normal"), width=18)

# Create a list of currencies
currencies = ["USD", "EUR", "GBP", "INR", "AUD", "CAD", "SGD", "CHF", "MYR", "JPY", "CNY"]

# Set the default value for the currency combobox
currency_combo.set("Select Currency")

# Set the default value for the converted currency combobox
converted_currency_combo.set("Select Converted Currency")

# Add the currencies to the currency combobox
currency_combo['values'] = currencies

# Add the currencies to the converted currency combobox
converted_currency_combo['values'] = currencies

# Create a button to convert currency
convert_button = Button(win, text="Convert", font=("Arial", 10, "bold"), command=exchange)

# Create a button to clear the GUI
clear_button = Button(win, text="Clear", font=("Arial", 10, "bold"), command=clear)

# Create a button to exit the GUI
exit_button = Button(win, text="Exit", font=("Arial", 10, "bold"), command=exit)

# Create an entry box for the amount
amount_entry.place(x=200, y=50)

# Create a combobox for the currency
currency_combo.place(x=200, y=100)

# Create a combobox for the converted currency
converted_currency_combo.place(x=200, y=150)

# Create a button to convert currency
convert_button.place(x=30, y=200)

# Create a button to clear the GUI
clear_button.place(x=130, y=200)

# Create a button to exit the GUI
exit_button.place(x=230, y=200)

# Run the tkinter event loop
win.mainloop()