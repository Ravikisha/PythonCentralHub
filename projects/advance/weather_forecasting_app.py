import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

class WeatherForecastingApp:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, X, y):
        self.model.fit(X, y)
        print("Weather forecasting model trained.")

    def predict(self, X):
        return self.model.predict(X)

    def demo(self):
        X = np.arange(0, 50).reshape(-1, 1)
        y = 15 + 0.4 * X.flatten() + np.random.normal(0, 1, 50)
        self.train(X, y)
        preds = self.predict(X)
        plt.plot(X, y, label='Actual')
        plt.plot(X, preds, label='Predicted')
        plt.legend()
        plt.title('Weather Forecasting App')
        plt.show()

if __name__ == "__main__":
    print("Weather Forecasting App Demo")
    app = WeatherForecastingApp()
    app.demo()
