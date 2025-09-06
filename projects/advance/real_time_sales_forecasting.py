import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

class RealTimeSalesForecasting:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, X, y):
        self.model.fit(X, y)
        print("Sales forecasting model trained.")

    def predict(self, X):
        return self.model.predict(X)

    def demo(self):
        X = np.arange(0, 100).reshape(-1, 1)
        y = 3 * X.flatten() + np.random.normal(0, 20, 100)
        self.train(X, y)
        preds = self.predict(X)
        plt.plot(X, y, label='Actual')
        plt.plot(X, preds, label='Predicted')
        plt.legend()
        plt.title('Real-Time Sales Forecasting')
        plt.show()

if __name__ == "__main__":
    print("Real-Time Sales Forecasting Demo")
    forecaster = RealTimeSalesForecasting()
    forecaster.demo()
