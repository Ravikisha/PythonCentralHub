"""
AI-powered Recommendation System

Features:
- Collaborative filtering
- Content-based filtering
- Web API (Flask)
- Modular design
- Error handling
"""
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import sys
import threading

class CollaborativeFiltering:
    def __init__(self, ratings):
        self.ratings = ratings
        self.user_means = ratings.mean(axis=1)

    def predict(self, user, item):
        if item not in self.ratings.columns or user not in self.ratings.index:
            return None
        sim = self.ratings.corrwith(self.ratings[item])
        sim = sim.dropna()
        user_ratings = self.ratings.loc[user]
        weighted_sum = np.dot(sim, user_ratings)
        return weighted_sum / sim.sum() if sim.sum() != 0 else self.user_means[user]

class ContentBasedFiltering:
    def __init__(self, items, features):
        self.items = items
        self.features = features

    def recommend(self, user_profile):
        scores = np.dot(self.features, user_profile)
        idx = np.argsort(scores)[::-1]
        return [self.items[i] for i in idx[:5]]

class RecommendationAPI:
    def __init__(self, ratings, items, features):
        self.cf = CollaborativeFiltering(ratings)
        self.cb = ContentBasedFiltering(items, features)
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/predict', methods=['POST'])
        def predict():
            data = request.json
            user = data.get('user')
            item = data.get('item')
            pred = self.cf.predict(user, item)
            return jsonify({'prediction': pred})

        @self.app.route('/recommend', methods=['POST'])
        def recommend():
            data = request.json
            user_profile = np.array(data.get('profile'))
            recs = self.cb.recommend(user_profile)
            return jsonify({'recommendations': recs})

    def run(self):
        self.app.run(debug=True)

class CLI:
    @staticmethod
    def run():
        ratings = pd.DataFrame(np.random.randint(1, 6, (10, 10)), columns=[f'item{i}' for i in range(10)], index=[f'user{j}' for j in range(10)])
        items = [f'item{i}' for i in range(10)]
        features = np.random.rand(10, 5)
        api = RecommendationAPI(ratings, items, features)
        print("Starting Recommendation API on http://127.0.0.1:5000 ...")
        api.run()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
