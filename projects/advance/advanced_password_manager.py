"""
Advanced Password Manager

Features:
- Secure password vault
- Encryption
- CLI/GUI interface
- Modular design
- Error handling
"""
import sys
import os
import json
import base64
from cryptography.fernet import Fernet
try:
    import tkinter as tk
    from tkinter import simpledialog, messagebox
except ImportError:
    tk = None
    simpledialog = None
    messagebox = None

class Vault:
    def __init__(self, key):
        self.key = key
        self.fernet = Fernet(key)
        self.data = {}
    def add(self, name, password):
        self.data[name] = self.fernet.encrypt(password.encode()).decode()
    def get(self, name):
        if name in self.data:
            return self.fernet.decrypt(self.data[name].encode()).decode()
        return None
    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.data, f)
    def load(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.data = json.load(f)

class PasswordManagerGUI:
    def __init__(self, vault):
        self.vault = vault
        self.root = tk.Tk()
        self.root.title("Password Manager")
        self.add_btn = tk.Button(self.root, text="Add Password", command=self.add_pw)
        self.add_btn.pack()
        self.get_btn = tk.Button(self.root, text="Get Password", command=self.get_pw)
        self.get_btn.pack()
    def add_pw(self):
        name = simpledialog.askstring("Name", "Enter account name:")
        pw = simpledialog.askstring("Password", "Enter password:")
        self.vault.add(name, pw)
        messagebox.showinfo("Saved", "Password saved.")
    def get_pw(self):
        name = simpledialog.askstring("Name", "Enter account name:")
        pw = self.vault.get(name)
        if pw:
            messagebox.showinfo("Password", f"Password: {pw}")
        else:
            messagebox.showerror("Error", "Account not found.")
    def run(self):
        self.root.mainloop()

class CLI:
    @staticmethod
    def run():
        key = Fernet.generate_key()
        vault = Vault(key)
        vault.load('vault.json')
        print("Advanced Password Manager")
        print("Commands: add <name> <password>, get <name>, save, exit")
        while True:
            cmd = input('> ')
            if cmd.startswith('add'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: add <name> <password>")
                    continue
                vault.add(parts[1], parts[2])
                print("Password added.")
            elif cmd.startswith('get'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: get <name>")
                    continue
                pw = vault.get(parts[1])
                print(f"Password: {pw}")
            elif cmd == 'save':
                vault.save('vault.json')
                print("Vault saved.")
            elif cmd == 'gui' and tk:
                gui = PasswordManagerGUI(vault)
                gui.run()
            elif cmd == 'exit':
                break
            else:
                print("Unknown command.")
        vault.save('vault.json')

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
