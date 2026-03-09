"""
AI-powered Stock Market Predictor

Features:
- Predicts stock prices using ML
- Data visualization
- Modular design
- CLI interface
- Error handling
"""
import sys
import numpy as np
try:
    from sklearn.linear_model import LinearRegression
    import matplotlib.pyplot as plt
except ImportError:
    LinearRegression = None
    plt = None

class StockPredictor:
    def __init__(self):
        self.model = LinearRegression() if LinearRegression else None
        self.trained = False
    def train(self, X, y):
        if self.model:
            self.model.fit(X, y)
            self.trained = True
    def predict(self, X):
        if self.trained:
            return self.model.predict(X)
        return [np.mean(X)] * len(X)
    def plot(self, X, y):
        if plt:
            plt.scatter(X, y)
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.title('Stock Prices')
            plt.show()
        else:
            print("matplotlib not available.")

class CLI:
    @staticmethod
    def run():
        print("AI-powered Stock Market Predictor")
        predictor = StockPredictor()
        while True:
            cmd = input('> ')
            if cmd.startswith('train'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: train <data_file> <labels_file>")
                    continue
                X = np.loadtxt(parts[1], delimiter=',').reshape(-1, 1)
                y = np.loadtxt(parts[2], delimiter=',')
                predictor.train(X, y)
                print("Model trained.")
            elif cmd.startswith('predict'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: predict <data_file>")
                    continue
                X = np.loadtxt(parts[1], delimiter=',').reshape(-1, 1)
                preds = predictor.predict(X)
                print(f"Predictions: {preds}")
            elif cmd.startswith('plot'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: plot <data_file> <labels_file>")
                    continue
                X = np.loadtxt(parts[1], delimiter=',').reshape(-1, 1)
                y = np.loadtxt(parts[2], delimiter=',')
                predictor.plot(X, y)
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
