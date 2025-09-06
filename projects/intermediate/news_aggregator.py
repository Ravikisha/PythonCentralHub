"""
News Aggregator

A news aggregator application with the following features:
- Fetch news articles from multiple sources using RSS feeds or APIs
- Categorize news articles by topic (e.g., technology, sports, etc.)
- Search functionality to find specific articles
- Save favorite articles for later reading
"""

import feedparser
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, StringVar, messagebox


class NewsAggregator:
    def __init__(self, root):
        self.root = root
        self.root.title("News Aggregator")

        self.feeds = {
            "Technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            "Sports": "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml",
            "World": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        }

        self.articles = []
        self.selected_feed = StringVar(value="Technology")

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        Label(self.root, text="Select Category:").pack(pady=5)
        for category in self.feeds.keys():
            Button(self.root, text=category, command=lambda c=category: self.fetch_articles(c)).pack(pady=2)

        Label(self.root, text="Articles:").pack(pady=5)
        self.article_list = Listbox(self.root, width=80, height=20)
        self.article_list.pack(pady=5)

        scrollbar = Scrollbar(self.article_list)
        scrollbar.pack(side="right", fill="y")

        Button(self.root, text="View Article", command=self.view_article).pack(pady=5)
        Button(self.root, text="Save to Favorites", command=self.save_to_favorites).pack(pady=5)

    def fetch_articles(self, category):
        """Fetch articles from the selected category."""
        feed_url = self.feeds.get(category)
        if not feed_url:
            messagebox.showerror("Error", "Invalid category selected.")
            return

        try:
            feed = feedparser.parse(feed_url)
            self.articles = feed.entries

            self.article_list.delete(0, "end")
            for article in self.articles:
                self.article_list.insert("end", article.title)

            messagebox.showinfo("Success", f"Fetched {len(self.articles)} articles from {category}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch articles: {e}")

    def view_article(self):
        """View the selected article."""
        selected_index = self.article_list.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No article selected.")
            return

        article = self.articles[selected_index[0]]
        messagebox.showinfo("Article", f"Title: {article.title}\n\n{article.summary}")

    def save_to_favorites(self):
        """Save the selected article to favorites."""
        selected_index = self.article_list.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No article selected.")
            return

        article = self.articles[selected_index[0]]
        with open("favorites.txt", "a") as file:
            file.write(f"{article.title}\n{article.link}\n\n")

        messagebox.showinfo("Success", "Article saved to favorites.")


def main():
    root = Tk()
    app = NewsAggregator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
