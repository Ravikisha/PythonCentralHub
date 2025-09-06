import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

class MedicalDiagnosisAI:
    def __init__(self):
        self.model = DecisionTreeClassifier()

    def train(self, X, y):
        self.model.fit(X, y)
        print("Medical diagnosis model trained.")

    def predict(self, X):
        return self.model.predict(X)

    def demo(self):
        # Simulate medical data
        X = np.random.rand(100, 5)
        y = np.random.randint(0, 2, 100)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        self.train(X_train, y_train)
        preds = self.predict(X_test)
        print(f"Predictions: {preds}")

if __name__ == "__main__":
    print("Medical Diagnosis AI Demo")
    ai = MedicalDiagnosisAI()
    ai.demo()
