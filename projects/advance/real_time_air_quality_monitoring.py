import numpy as np
import matplotlib.pyplot as plt

class RealTimeAirQualityMonitoring:
    def __init__(self):
        pass

    def get_air_quality_data(self):
        # Simulate real-time air quality data
        data = np.random.normal(loc=50, scale=10, size=100)
        print(f"Air quality data: {data}")
        return data

    def plot_data(self, data):
        plt.plot(data)
        plt.title('Real-Time Air Quality Monitoring')
        plt.xlabel('Time')
        plt.ylabel('AQI')
        plt.show()

    def demo(self):
        data = self.get_air_quality_data()
        self.plot_data(data)

if __name__ == "__main__":
    print("Real-Time Air Quality Monitoring Demo")
    monitor = RealTimeAirQualityMonitoring()
    monitor.demo()
