import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

class RealTimeNetworkIntrusionDetection:
    def __init__(self):
        self.model = IsolationForest()

    def fit(self, data):
        self.model.fit(data)
        print("Model trained for network intrusion detection.")

    def predict(self, data):
        return self.model.predict(data)

    def demo(self):
        data = np.random.rand(100, 3)
        self.fit(data)
        preds = self.predict(data)
        plt.scatter(data[:,0], data[:,1], c=preds)
        plt.title('Real-Time Network Intrusion Detection Results')
        plt.show()

if __name__ == "__main__":
    print("Real-Time Network Intrusion Detection Demo")
    detector = RealTimeNetworkIntrusionDetection()
    detector.demo()
