import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

class RealTimeAnomalyDetection:
    def __init__(self):
        self.model = IsolationForest()

    def fit(self, data):
        self.model.fit(data)
        print("Model trained for anomaly detection.")

    def predict(self, data):
        return self.model.predict(data)

    def demo(self):
        data = np.random.rand(100, 2)
        self.fit(data)
        preds = self.predict(data)
        plt.scatter(data[:,0], data[:,1], c=preds)
        plt.title('Real-Time Anomaly Detection Results')
        plt.show()

if __name__ == "__main__":
    print("Real-Time Anomaly Detection Demo")
    detector = RealTimeAnomalyDetection()
    detector.demo()
