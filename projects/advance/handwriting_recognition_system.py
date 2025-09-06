import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

class HandwritingRecognitionSystem:
    def __init__(self):
        self.model = SVC()

    def train(self, X, y):
        self.model.fit(X, y)
        print("SVM model trained for handwriting recognition.")

    def predict(self, X):
        return self.model.predict(X)

    def demo(self):
        digits = load_digits()
        X_train, X_test, y_train, y_test = train_test_split(digits.data, digits.target, test_size=0.2)
        self.train(X_train, y_train)
        score = self.model.score(X_test, y_test)
        print(f"Test accuracy: {score:.2f}")
        plt.imshow(digits.images[1], cmap='gray')
        plt.title(f"Label: {digits.target[1]}")
        plt.show()

if __name__ == "__main__":
    print("Handwriting Recognition System Demo")
    system = HandwritingRecognitionSystem()
    system.demo()
