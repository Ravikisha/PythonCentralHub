"""
Interactive Data Visualization Tool

Features:
- Interactive charts
- Dashboards
- Modular design
- CLI interface
- Error handling
"""
import sys
import pandas as pd
import matplotlib.pyplot as plt
import random

class DataVisualizer:
    def __init__(self):
        self.data = None
    def load_data(self, file_path):
        self.data = pd.read_csv(file_path)
    def plot(self, col1, col2):
        if self.data is not None:
            plt.scatter(self.data[col1], self.data[col2])
            plt.xlabel(col1)
            plt.ylabel(col2)
            plt.title(f'{col1} vs {col2}')
            plt.show()
        else:
            print("No data loaded.")
    def dashboard(self):
        if self.data is not None:
            print("Columns:", list(self.data.columns))
            print(self.data.describe())
        else:
            print("No data loaded.")

class CLI:
    @staticmethod
    def run():
        viz = DataVisualizer()
        print("Interactive Data Visualization Tool")
        while True:
            cmd = input('> ')
            if cmd.startswith('load'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: load <csv_file>")
                    continue
                viz.load_data(parts[1])
                print("Data loaded.")
            elif cmd.startswith('plot'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: plot <col1> <col2>")
                    continue
                viz.plot(parts[1], parts[2])
            elif cmd == 'dashboard':
                viz.dashboard()
            elif cmd == 'exit':
                break
            else:
                print("Unknown command. Type 'load', 'plot', 'dashboard', or 'exit'.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
