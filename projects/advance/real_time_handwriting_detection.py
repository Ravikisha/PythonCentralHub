import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

class RealTimeHandwritingDetection:
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)

    def train(self, X, y):
        self.model.fit(X, y)
        print("Handwriting detection model trained.")

    def predict(self, X):
        return self.model.predict(X)

    def demo(self):
        X = np.random.rand(100, 16)
        y = np.random.randint(0, 10, 100)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        self.train(X_train, y_train)
        preds = self.predict(X_test)
        print(f"Predictions: {preds}")

if __name__ == "__main__":
    print("Real-Time Handwriting Detection Demo")
    detector = RealTimeHandwritingDetection()
    detector.demo()
