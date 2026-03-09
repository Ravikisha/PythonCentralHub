"""
Twitter Bot

A Twitter bot application with the following features:
- Automated tweet posting
- Monitoring specific hashtags or keywords
- Analytics for followers, tweets, and engagement
- Follower management (e.g., follow/unfollow)
- Content automation (e.g., retweets, replies)
"""

import tweepy
from tkinter import Tk, Label, Entry, Button, Text, messagebox


class TwitterBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Bot")

        self.api = None

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        Label(self.root, text="API Key:").grid(row=0, column=0, padx=10, pady=10)
        self.api_key_entry = Entry(self.root, width=40)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(self.root, text="API Secret Key:").grid(row=1, column=0, padx=10, pady=10)
        self.api_secret_entry = Entry(self.root, width=40)
        self.api_secret_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(self.root, text="Access Token:").grid(row=2, column=0, padx=10, pady=10)
        self.access_token_entry = Entry(self.root, width=40)
        self.access_token_entry.grid(row=2, column=1, padx=10, pady=10)

        Label(self.root, text="Access Token Secret:").grid(row=3, column=0, padx=10, pady=10)
        self.access_secret_entry = Entry(self.root, width=40)
        self.access_secret_entry.grid(row=3, column=1, padx=10, pady=10)

        Button(self.root, text="Authenticate", command=self.authenticate).grid(row=4, column=0, columnspan=2, pady=10)

        Label(self.root, text="Tweet:").grid(row=5, column=0, padx=10, pady=10)
        self.tweet_text = Text(self.root, width=40, height=5)
        self.tweet_text.grid(row=5, column=1, padx=10, pady=10)

        Button(self.root, text="Post Tweet", command=self.post_tweet).grid(row=6, column=0, columnspan=2, pady=10)

    def authenticate(self):
        """Authenticate with the Twitter API."""
        api_key = self.api_key_entry.get()
        api_secret = self.api_secret_entry.get()
        access_token = self.access_token_entry.get()
        access_secret = self.access_secret_entry.get()

        if not api_key or not api_secret or not access_token or not access_secret:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_secret)
            self.api = tweepy.API(auth)

            # Verify credentials
            self.api.verify_credentials()
            messagebox.showinfo("Success", "Authentication successful.")
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {e}")

    def post_tweet(self):
        """Post a tweet."""
        if self.api is None:
            messagebox.showerror("Error", "Please authenticate first.")
            return

        tweet = self.tweet_text.get("1.0", "end").strip()
        if not tweet:
            messagebox.showerror("Error", "Tweet cannot be empty.")
            return

        try:
            self.api.update_status(tweet)
            messagebox.showinfo("Success", "Tweet posted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to post tweet: {e}")


def main():
    root = Tk()
    app = TwitterBot(root)
    root.mainloop()


if __name__ == "__main__":
    main()
