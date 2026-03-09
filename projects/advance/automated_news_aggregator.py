"""
Automated News Aggregator

Features:
- Topic classification
- Sentiment analysis
- Web interface (Flask)
- Modular design
- Error handling
"""
import requests
from flask import Flask, jsonify
import threading
import sys
import random

class NewsFetcher:
    def __init__(self):
        self.news = []
    def fetch(self):
        # Dummy: fetch random news
        for _ in range(10):
            self.news.append({
                'title': f'News {_}',
                'content': f'Content for news {_}',
                'topic': random.choice(['tech', 'sports', 'politics']),
                'sentiment': random.choice(['positive', 'neutral', 'negative'])
            })

class NewsAPI:
    def __init__(self, fetcher):
        self.app = Flask(__name__)
        self.fetcher = fetcher
        self.setup_routes()
    def setup_routes(self):
        @self.app.route('/news', methods=['GET'])
        def get_news():
            return jsonify(self.fetcher.news)
    def run(self):
        self.app.run(debug=True)

class CLI:
    @staticmethod
    def run():
        fetcher = NewsFetcher()
        fetcher.fetch()
        api = NewsAPI(fetcher)
        print("Starting News Aggregator API on http://127.0.0.1:5000 ...")
        api.run()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
