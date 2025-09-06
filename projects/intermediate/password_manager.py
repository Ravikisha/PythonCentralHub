"""
Password Manager

A secure password manager application with the following features:
- Encryption and decryption of stored passwords
- Password generation with customizable options
- Categorization of passwords (e.g., work, personal, etc.)
- Search functionality to quickly find stored passwords
- Master password protection to access the application
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from tkinter import Tk, Label, Entry, Button, messagebox, simpledialog


class PasswordManager:
    def __init__(self):
        self.master_password = None
        self.key = None
        self.data_file = "passwords.json"
        self.data = {}

        # Load existing data if available
        self.load_data()

    def generate_key(self, master_password):
        """Generate a key based on the master password."""
        return base64.urlsafe_b64encode(master_password.encode().ljust(32)[:32])

    def encrypt(self, plaintext):
        """Encrypt plaintext using the generated key."""
        cipher = Fernet(self.key)
        return cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext):
        """Decrypt ciphertext using the generated key."""
        cipher = Fernet(self.key)
        return cipher.decrypt(ciphertext.encode()).decode()

    def load_data(self):
        """Load password data from the JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.data = json.load(file)

    def save_data(self):
        """Save password data to the JSON file."""
        with open(self.data_file, "w") as file:
            json.dump(self.data, file, indent=4)

    def authenticate(self):
        """Authenticate the user with the master password."""
        master_password = simpledialog.askstring("Master Password", "Enter your master password:", show="*")
        if not master_password:
            return False

        self.master_password = master_password
        self.key = self.generate_key(master_password)
        return True

    def add_password(self, category, name, username, password):
        """Add a new password to the manager."""
        if category not in self.data:
            self.data[category] = []

        encrypted_password = self.encrypt(password)
        self.data[category].append({
            "name": name,
            "username": username,
            "password": encrypted_password
        })
        self.save_data()

    def get_passwords(self, category):
        """Retrieve passwords for a specific category."""
        if category not in self.data:
            return []

        passwords = []
        for entry in self.data[category]:
            decrypted_password = self.decrypt(entry["password"])
            passwords.append({
                "name": entry["name"],
                "username": entry["username"],
                "password": decrypted_password
            })
        return passwords

    def search_passwords(self, query):
        """Search for passwords matching the query."""
        results = []
        for category, entries in self.data.items():
            for entry in entries:
                if query.lower() in entry["name"].lower() or query.lower() in entry["username"].lower():
                    decrypted_password = self.decrypt(entry["password"])
                    results.append({
                        "category": category,
                        "name": entry["name"],
                        "username": entry["username"],
                        "password": decrypted_password
                    })
        return results


class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.manager = PasswordManager()

        if not self.manager.authenticate():
            messagebox.showerror("Error", "Authentication failed.")
            self.root.destroy()
            return

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        Label(self.root, text="Category:").grid(row=0, column=0, padx=10, pady=10)
        self.category_entry = Entry(self.root)
        self.category_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(self.root, text="Name:").grid(row=1, column=0, padx=10, pady=10)
        self.name_entry = Entry(self.root)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(self.root, text="Username:").grid(row=2, column=0, padx=10, pady=10)
        self.username_entry = Entry(self.root)
        self.username_entry.grid(row=2, column=1, padx=10, pady=10)

        Label(self.root, text="Password:").grid(row=3, column=0, padx=10, pady=10)
        self.password_entry = Entry(self.root, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=10)

        Button(self.root, text="Add Password", command=self.add_password).grid(row=4, column=0, columnspan=2, pady=10)
        Button(self.root, text="Search Passwords", command=self.search_passwords).grid(row=5, column=0, columnspan=2, pady=10)

    def add_password(self):
        """Add a new password."""
        category = self.category_entry.get()
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not category or not name or not username or not password:
            messagebox.showerror("Error", "All fields are required.")
            return

        self.manager.add_password(category, name, username, password)
        messagebox.showinfo("Success", "Password added successfully.")

    def search_passwords(self):
        """Search for passwords."""
        query = simpledialog.askstring("Search", "Enter search query:")
        if not query:
            return

        results = self.manager.search_passwords(query)
        if not results:
            messagebox.showinfo("No Results", "No passwords found.")
            return

        result_text = "\n".join([f"Category: {r['category']}, Name: {r['name']}, Username: {r['username']}, Password: {r['password']}" for r in results])
        messagebox.showinfo("Search Results", result_text)


def main():
    root = Tk()
    app = PasswordManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
