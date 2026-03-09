import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

class RealTimeChurnPrediction:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, X, y):
        self.model.fit(X, y)
        print("Churn prediction model trained.")

    def predict(self, X):
        return self.model.predict(X)

    def demo(self):
        X = np.random.rand(100, 4)
        y = np.random.randint(0, 2, 100)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        self.train(X_train, y_train)
        preds = self.predict(X_test)
        print(f"Predictions: {preds}")

if __name__ == "__main__":
    print("Real-Time Churn Prediction Demo")
    predictor = RealTimeChurnPrediction()
    predictor.demo()
