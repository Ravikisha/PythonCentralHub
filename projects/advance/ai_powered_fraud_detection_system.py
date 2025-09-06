"""
AI-powered Fraud Detection System

Features:
- Detects fraud using ML
- Data analysis
- Reporting
- Modular design
- CLI interface
- Error handling
"""
import sys
import numpy as np
try:
    from sklearn.ensemble import IsolationForest
except ImportError:
    IsolationForest = None

class FraudDetection:
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
        return [1] * len(X)

class CLI:
    @staticmethod
    def run():
        print("AI-powered Fraud Detection System")
        print("Commands: train <data_file>, predict <data_file>, exit")
        detector = FraudDetection()
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
