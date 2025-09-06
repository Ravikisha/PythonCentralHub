import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance

def fuse_sensors(sensor_data):
    # Dummy fusion (for demo)
    return np.mean(sensor_data, axis=0)

def plan_path(start, end):
    # Dummy path planning (for demo)
    path = [start, end]
    return path

def main():
    print("Autonomous Vehicle Simulation")
    # Simulate sensor data for 5 time steps (e.g., GPS, LIDAR, Radar)
    np.random.seed(42)
    sensor_data = np.random.rand(5, 3) * 10  # 5 readings, 3 sensors
    print("Sensor data (5 readings, 3 sensors):")
    print(sensor_data)

    # Fuse sensor data
    fused = fuse_sensors(sensor_data)
    print(f"\nFused sensor data (mean): {fused}")

    # Plan a path from start to end
    start = tuple(fused[:2])
    end = (fused[0] + 10, fused[1] + 10)
    path = plan_path(start, end)
    print(f"\nPlanned path: {path}")

    # Calculate path length using Euclidean distance
    path_length = distance.euclidean(start, end)
    print(f"Path length: {path_length:.2f}")

    # Visualization
    plt.figure(figsize=(6, 6))
    plt.plot([p[0] for p in path], [p[1] for p in path], marker='o', color='blue', label='Planned Path')
    plt.scatter(sensor_data[:,0], sensor_data[:,1], color='red', label='Sensor Readings')
    plt.title('Autonomous Vehicle Path Planning')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid(True)
    plt.show()
    print("\nSimulation complete. Visualization displayed.")

if __name__ == "__main__":
    main()
