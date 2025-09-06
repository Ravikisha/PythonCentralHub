"""
Advanced Network Traffic Monitor

Features:
- Network traffic analysis
- Visualization
- Anomaly detection
- Modular design
- CLI interface
- Error handling
"""
import psutil
import time
import sys
import matplotlib.pyplot as plt
import numpy as np

class TrafficMonitor:
    def __init__(self):
        self.data = []
        self.timestamps = []

    def collect(self, duration=60):
        print("Collecting network traffic data...")
        for _ in range(duration):
            stats = psutil.net_io_counters()
            self.data.append(stats.bytes_sent + stats.bytes_recv)
            self.timestamps.append(time.time())
            time.sleep(1)

    def detect_anomaly(self):
        arr = np.array(self.data)
        mean = arr.mean()
        std = arr.std()
        anomalies = [(i, v) for i, v in enumerate(arr) if abs(v - mean) > 2*std]
        return anomalies

    def visualize(self):
        plt.plot(self.timestamps, self.data, label='Traffic')
        anomalies = self.detect_anomaly()
        for idx, val in anomalies:
            plt.scatter(self.timestamps[idx], val, color='r', label='Anomaly' if idx==anomalies[0][0] else "")
        plt.xlabel('Time')
        plt.ylabel('Bytes')
        plt.title('Network Traffic Over Time')
        plt.legend()
        plt.show()

class CLI:
    @staticmethod
    def run():
        monitor = TrafficMonitor()
        monitor.collect(60)
        print("Visualizing...")
        monitor.visualize()
        anomalies = monitor.detect_anomaly()
        print(f"Anomalies detected: {anomalies}")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
