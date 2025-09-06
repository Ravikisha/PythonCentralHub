import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

class CustomerSegmentationML:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters)

    def fit(self, data):
        self.model.fit(data)
        print(f"Model fitted with {self.n_clusters} clusters.")

    def predict(self, data):
        return self.model.predict(data)

    def plot_clusters(self, data):
        labels = self.model.predict(data)
        plt.scatter(data[:,0], data[:,1], c=labels)
        plt.title('Customer Segmentation')
        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        plt.show()

if __name__ == "__main__":
    print("Customer Segmentation ML Demo")
    # Example data
    import numpy as np
    data = np.random.rand(100, 2)
    segmenter = CustomerSegmentationML(n_clusters=3)
    segmenter.fit(data)
    segmenter.plot_clusters(data)
