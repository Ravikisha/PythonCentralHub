import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

class RealTimeCustomerSegmentation:
    def __init__(self, n_clusters=3):
        self.model = KMeans(n_clusters=n_clusters)

    def fit(self, data):
        self.model.fit(data)
        print(f"Model fitted with {self.model.n_clusters} clusters.")

    def predict(self, data):
        return self.model.predict(data)

    def demo(self):
        data = np.random.rand(100, 2)
        self.fit(data)
        labels = self.predict(data)
        plt.scatter(data[:,0], data[:,1], c=labels)
        plt.title('Real-Time Customer Segmentation')
        plt.show()

if __name__ == "__main__":
    print("Real-Time Customer Segmentation Demo")
    segmenter = RealTimeCustomerSegmentation()
    segmenter.demo()
