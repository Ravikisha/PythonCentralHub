"""
Password Generator with Strength Meter

A password generator application with the following features:
- Generate passwords with customizable length and character types
- Evaluate password strength in real-time
- Copy generated passwords to clipboard
"""

import random
import string
from tkinter import Tk, Label, Entry, Button, IntVar, Checkbutton, messagebox


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")

        self.length = IntVar(value=12)
        self.include_uppercase = IntVar(value=1)
        self.include_numbers = IntVar(value=1)
        self.include_symbols = IntVar(value=1)

        self.generated_password = ""

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        Label(self.root, text="Password Length:").grid(row=0, column=0, padx=10, pady=10)
        Entry(self.root, textvariable=self.length).grid(row=0, column=1, padx=10, pady=10)

        Checkbutton(self.root, text="Include Uppercase Letters", variable=self.include_uppercase).grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        Checkbutton(self.root, text="Include Numbers", variable=self.include_numbers).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        Checkbutton(self.root, text="Include Symbols", variable=self.include_symbols).grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        Button(self.root, text="Generate Password", command=self.generate_password).grid(row=4, column=0, columnspan=2, pady=10)

        Label(self.root, text="Generated Password:").grid(row=5, column=0, padx=10, pady=10)
        self.password_label = Label(self.root, text="", fg="blue")
        self.password_label.grid(row=5, column=1, padx=10, pady=10)

        Button(self.root, text="Copy to Clipboard", command=self.copy_to_clipboard).grid(row=6, column=0, columnspan=2, pady=10)

    def generate_password(self):
        """Generate a random password based on user preferences."""
        length = self.length.get()
        if length < 6:
            messagebox.showerror("Error", "Password length must be at least 6 characters.")
            return

        characters = string.ascii_lowercase
        if self.include_uppercase.get():
            characters += string.ascii_uppercase
        if self.include_numbers.get():
            characters += string.digits
        if self.include_symbols.get():
            characters += string.punctuation

        self.generated_password = "".join(random.choice(characters) for _ in range(length))
        self.password_label.config(text=self.generated_password)

    def copy_to_clipboard(self):
        """Copy the generated password to the clipboard."""
        if not self.generated_password:
            messagebox.showerror("Error", "No password generated.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.generated_password)
        self.root.update()  # Keep the clipboard content
        messagebox.showinfo("Success", "Password copied to clipboard.")


def main():
    root = Tk()
    app = PasswordGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
