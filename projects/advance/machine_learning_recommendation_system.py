import numpy as np
from sklearn.neighbors import NearestNeighbors

class MachineLearningRecommendationSystem:
    def __init__(self, n_neighbors=3):
        self.model = NearestNeighbors(n_neighbors=n_neighbors)

    def fit(self, data):
        self.model.fit(data)
        print(f"Model fitted with {self.model.n_neighbors} neighbors.")

    def recommend(self, item):
        distances, indices = self.model.kneighbors([item])
        print(f"Recommended indices: {indices[0]}")
        return indices[0]

    def demo(self):
        data = np.random.rand(10, 4)
        self.fit(data)
        self.recommend(data[0])

if __name__ == "__main__":
    print("Machine Learning Recommendation System Demo")
    recommender = MachineLearningRecommendationSystem()
    recommender.demo()
