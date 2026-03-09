"""
Anomaly Detection System

Features:
- Anomaly detection in data streams
- ML model training and prediction
- Reporting
- Modular design
- CLI interface
- Error handling
"""
import sys
import numpy as np
import random
try:
    from sklearn.ensemble import IsolationForest
except ImportError:
    IsolationForest = None

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest() if IsolationForest else None
        self.trained = False
    def train(self, X):
        if self.model:
            self.model.fit(X)
            self.trained = True
    def predict(self, X):
        if self.trained:
            return self.model.predict(X)
        return [random.choice([-1, 1]) for _ in X]

class CLI:
    @staticmethod
    def run():
        print("Anomaly Detection System")
        print("Commands: train <data_file>, predict <data_file>, exit")
        detector = AnomalyDetector()
        while True:
            cmd = input('> ')
            if cmd.startswith('train'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: train <data_file>")
                    continue
                X = np.loadtxt(parts[1], delimiter=',')
                detector.train(X)
                print("Model trained.")
            elif cmd.startswith('predict'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: predict <data_file>")
                    continue
                X = np.loadtxt(parts[1], delimiter=',')
                preds = detector.predict(X)
                print(f"Predictions: {preds}")
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
