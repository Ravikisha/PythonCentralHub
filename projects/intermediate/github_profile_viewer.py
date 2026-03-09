"""
GitHub Profile Viewer

A Python application that fetches and displays GitHub user profile information using the GitHub API.
Features include:
- Fetching user details like name, bio, repositories, followers, etc.
- Displaying the information in a user-friendly format.
"""

import requests
from tkinter import Tk, Label, Entry, Button, Text, END, messagebox


class GitHubProfileViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Profile Viewer")

        Label(root, text="Enter GitHub Username:").grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = Entry(root, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        Button(root, text="Fetch Profile", command=self.fetch_profile).grid(row=1, column=0, columnspan=2, pady=10)

        self.result_text = Text(root, width=50, height=20)
        self.result_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def fetch_profile(self):
        """Fetch GitHub profile information for the entered username."""
        username = self.username_entry.get()
        if not username:
            messagebox.showerror("Error", "Please enter a GitHub username.")
            return

        url = f"https://api.github.com/users/{username}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            self.display_profile(data)
        else:
            messagebox.showerror("Error", f"Failed to fetch profile. Status code: {response.status_code}")

    def display_profile(self, data):
        """Display the fetched profile information in the text widget."""
        self.result_text.delete(1.0, END)
        self.result_text.insert(END, f"Name: {data.get('name', 'N/A')}\n")
        self.result_text.insert(END, f"Bio: {data.get('bio', 'N/A')}\n")
        self.result_text.insert(END, f"Public Repos: {data.get('public_repos', 'N/A')}\n")
        self.result_text.insert(END, f"Followers: {data.get('followers', 'N/A')}\n")
        self.result_text.insert(END, f"Following: {data.get('following', 'N/A')}\n")
        self.result_text.insert(END, f"Profile URL: {data.get('html_url', 'N/A')}\n")


def main():
    root = Tk()
    app = GitHubProfileViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
