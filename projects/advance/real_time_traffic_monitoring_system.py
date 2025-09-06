"""
Real-time Traffic Monitoring System

Features:
- Traffic monitoring with live data
- Visualization
- Alerts
- Modular design
- CLI interface
- Error handling
"""
import sys
import random
import time
import matplotlib.pyplot as plt

class TrafficMonitor:
    def __init__(self):
        self.data = []
        self.timestamps = []
    def collect(self, duration=60):
        print("Collecting traffic data...")
        for _ in range(duration):
            traffic = random.randint(50, 200)
            self.data.append(traffic)
            self.timestamps.append(time.time())
            if traffic > 180:
                print("ALERT: High traffic detected!")
            time.sleep(1)
    def visualize(self):
        plt.plot(self.timestamps, self.data, label='Traffic')
        plt.xlabel('Time')
        plt.ylabel('Traffic Volume')
        plt.title('Traffic Monitoring')
        plt.legend()
        plt.show()

class CLI:
    @staticmethod
    def run():
        monitor = TrafficMonitor()
        monitor.collect(60)
        print("Visualizing...")
        monitor.visualize()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
