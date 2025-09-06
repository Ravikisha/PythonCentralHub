"""
Smart Health Monitor

Features:
- Sensor data analysis
- Alerting
- Modular design
- CLI interface
- Error handling
"""
import sys
import random
import time
import threading

class Sensor:
    def __init__(self, name):
        self.name = name
        self.data = []
    def read(self):
        value = random.uniform(60, 100) if self.name == 'heart_rate' else random.uniform(36, 38)
        self.data.append(value)
        return value

class HealthMonitor:
    def __init__(self):
        self.sensors = [Sensor('heart_rate'), Sensor('temperature')]
        self.running = True
        self.thread = threading.Thread(target=self.monitor, daemon=True)
        self.thread.start()
    def monitor(self):
        while self.running:
            readings = {s.name: s.read() for s in self.sensors}
            print(f"Readings: {readings}")
            if readings['heart_rate'] > 95:
                print("ALERT: High heart rate!")
            if readings['temperature'] > 37.5:
                print("ALERT: High temperature!")
            time.sleep(2)
    def stop(self):
        self.running = False

class CLI:
    @staticmethod
    def run():
        print("Smart Health Monitor")
        hm = HealthMonitor()
        try:
            while True:
                cmd = input('> ')
                if cmd == 'stop':
                    hm.stop()
                    break
                else:
                    print("Unknown command. Type 'stop' to exit.")
        except KeyboardInterrupt:
            hm.stop()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
