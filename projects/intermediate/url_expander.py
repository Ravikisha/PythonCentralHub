"""
URL Expander

A Python application that expands shortened URLs to their original form.
Features include:
- Accepting a shortened URL as input.
- Displaying the expanded URL.
"""

import requests
from tkinter import Tk, Label, Entry, Button, messagebox


def expand_url(short_url):
    """Expand a shortened URL to its original form."""
    try:
        response = requests.head(short_url, allow_redirects=True)
        return response.url
    except requests.RequestException as e:
        return str(e)


class URLExpanderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Expander")

        Label(root, text="Enter Shortened URL:").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        Button(root, text="Expand URL", command=self.expand_url).grid(row=1, column=0, columnspan=2, pady=10)

    def expand_url(self):
        """Handle the button click to expand the URL."""
        short_url = self.url_entry.get()
        if not short_url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        expanded_url = expand_url(short_url)
        messagebox.showinfo("Expanded URL", f"Original URL: {expanded_url}")


def main():
    root = Tk()
    app = URLExpanderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
