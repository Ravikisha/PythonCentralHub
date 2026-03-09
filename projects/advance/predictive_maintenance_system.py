import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

class PredictiveMaintenanceSystem:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, X, y):
        self.model.fit(X, y)
        print("Predictive maintenance model trained.")

    def predict(self, X):
        return self.model.predict(X)

    def demo(self):
        X = np.arange(0, 100).reshape(-1, 1)
        y = 0.5 * X.flatten() + np.random.normal(0, 5, 100)
        self.train(X, y)
        preds = self.predict(X)
        plt.plot(X, y, label='Actual')
        plt.plot(X, preds, label='Predicted')
        plt.legend()
        plt.title('Predictive Maintenance')
        plt.show()

if __name__ == "__main__":
    print("Predictive Maintenance System Demo")
    system = PredictiveMaintenanceSystem()
    system.demo()
