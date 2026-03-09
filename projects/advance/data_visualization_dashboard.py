import pandas as pd
import matplotlib.pyplot as plt

class DataVisualizationDashboard:
    def __init__(self, data):
        self.data = data

    def plot(self):
        self.data.plot(kind='bar')
        plt.title('Data Visualization Dashboard')
        plt.xlabel('Category')
        plt.ylabel('Value')
        plt.show()

if __name__ == "__main__":
    print("Data Visualization Dashboard Demo")
    # Example data
    df = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6]})
    dashboard = DataVisualizationDashboard(df)
    dashboard.plot()
