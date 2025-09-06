"""
Autonomous Drone Simulation

Features:
- Path planning
- Obstacle avoidance
- 3D visualization (matplotlib)
- Modular design
- CLI interface
- Error handling
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import random

class Drone:
    def __init__(self, start, goal):
        self.position = np.array(start)
        self.goal = np.array(goal)
        self.path = [start]
        self.obstacles = []

    def add_obstacle(self, obs):
        self.obstacles.append(np.array(obs))

    def plan_path(self):
        for _ in range(200):
            direction = self.goal - self.position
            direction = direction / np.linalg.norm(direction)
            next_pos = self.position + direction * 1.0
            if any(np.linalg.norm(next_pos - obs) < 2.0 for obs in self.obstacles):
                next_pos += np.random.randn(3)
            self.position = next_pos
            self.path.append(tuple(self.position))
            if np.linalg.norm(self.position - self.goal) < 1.0:
                break

    def visualize(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        path = np.array(self.path)
        ax.plot(path[:,0], path[:,1], path[:,2], label='Drone Path')
        ax.scatter(self.goal[0], self.goal[1], self.goal[2], c='r', label='Goal')
        for obs in self.obstacles:
            ax.scatter(obs[0], obs[1], obs[2], c='k', marker='x', label='Obstacle')
        ax.legend()
        plt.show()

class CLI:
    @staticmethod
    def run():
        drone = Drone((0,0,0), (10,10,10))
        for _ in range(5):
            obs = (random.uniform(2,8), random.uniform(2,8), random.uniform(2,8))
            drone.add_obstacle(obs)
        print("Planning path...")
        drone.plan_path()
        print("Visualizing...")
        drone.visualize()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
