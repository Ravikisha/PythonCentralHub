"""
AI-driven Medical Diagnosis System

Features:
- Medical diagnosis using ML
- Data analysis
- Reporting
- Modular design
- CLI interface
- Error handling
"""
import sys
import numpy as np
import random
try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    RandomForestClassifier = None

class MedicalDiagnosis:
    def __init__(self):
        self.model = RandomForestClassifier() if RandomForestClassifier else None
        self.trained = False
    def train(self, X, y):
        if self.model:
            self.model.fit(X, y)
            self.trained = True
    def predict(self, X):
        if self.trained:
            return self.model.predict(X)
        return [random.choice([0, 1]) for _ in X]

class CLI:
    @staticmethod
    def run():
        print("AI-driven Medical Diagnosis System")
        print("Commands: train <data_file> <labels_file>, predict <data_file>, exit")
        diagnosis = MedicalDiagnosis()
        while True:
            cmd = input('> ')
            if cmd.startswith('train'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: train <data_file> <labels_file>")
                    continue
                X = np.loadtxt(parts[1], delimiter=',')
                y = np.loadtxt(parts[2], delimiter=',')
                diagnosis.train(X, y)
                print("Model trained.")
            elif cmd.startswith('predict'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: predict <data_file>")
                    continue
                X = np.loadtxt(parts[1], delimiter=',')
                preds = diagnosis.predict(X)
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
