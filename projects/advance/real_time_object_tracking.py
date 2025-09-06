import numpy as np
import matplotlib.pyplot as plt

class RealTimeObjectTracking:
    def __init__(self):
        pass

    def track_object(self, positions):
        print("Tracking object...")
        return positions

    def demo(self):
        positions = np.cumsum(np.random.randn(20, 2), axis=0)
        tracked = self.track_object(positions)
        plt.plot(tracked[:,0], tracked[:,1], marker='o')
        plt.title('Real-Time Object Tracking')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    print("Real-Time Object Tracking Demo")
    tracker = RealTimeObjectTracking()
    tracker.demo()
