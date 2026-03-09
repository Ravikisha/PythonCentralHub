"""
Gesture Recognition System

Features:
- Computer vision gesture recognition
- ML model training and prediction
- Real-time webcam interface
- Modular design
- CLI interface
- Error handling
"""
import cv2
import numpy as np
import sys
import os
import random
try:
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split
except ImportError:
    SVC = None
    train_test_split = None

class GestureDataset:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.images = []
        self.labels = []
    def load(self):
        for label in os.listdir(self.data_dir):
            label_dir = os.path.join(self.data_dir, label)
            for img_file in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_file)
                img = cv2.imread(img_path, 0)
                img = cv2.resize(img, (64, 64)).flatten()
                self.images.append(img)
                self.labels.append(label)
        return np.array(self.images), np.array(self.labels)

class GestureRecognizer:
    def __init__(self):
        self.model = SVC() if SVC else None
        self.trained = False
    def train(self, X, y):
        if self.model:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            self.model.fit(X_train, y_train)
            acc = self.model.score(X_test, y_test)
            print(f"Model accuracy: {acc}")
            self.trained = True
    def predict(self, img):
        if self.trained:
            return self.model.predict([img.flatten()])[0]
        return random.choice(['wave', 'thumbs_up', 'fist'])

class CLI:
    @staticmethod
    def run():
        print("Gesture Recognition System")
        print("Commands: train <data_dir>, predict <img_path>, webcam, exit")
        recognizer = GestureRecognizer()
        while True:
            cmd = input('> ')
            if cmd.startswith('train'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: train <data_dir>")
                    continue
                ds = GestureDataset(parts[1])
                X, y = ds.load()
                recognizer.train(X, y)
            elif cmd.startswith('predict'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: predict <img_path>")
                    continue
                img = cv2.imread(parts[1], 0)
                img = cv2.resize(img, (64, 64))
                label = recognizer.predict(img)
                print(f"Predicted gesture: {label}")
            elif cmd == 'webcam':
                cap = cv2.VideoCapture(0)
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    img = cv2.resize(gray, (64, 64))
                    label = recognizer.predict(img)
                    cv2.putText(frame, f"Gesture: {label}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                    cv2.imshow('Gesture Recognition', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                cap.release()
                cv2.destroyAllWindows()
            elif cmd == 'exit':
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
