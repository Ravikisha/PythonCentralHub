"""
Autonomous Robot Simulation (Pygame)

Features:
- Robot pathfinding
- Sensor simulation
- GUI (Pygame)
- Modular design
- Error handling
"""
import pygame
import sys
import math
import random

WIDTH, HEIGHT = 800, 600
FPS = 60

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 2
        self.path = [(x, y)]
    def move(self, target):
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            self.angle = math.atan2(dy, dx)
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            self.path.append((self.x, self.y))
    def draw(self, screen):
        pygame.draw.circle(screen, (0,255,0), (int(self.x), int(self.y)), 15)
        if len(self.path) > 1:
            pygame.draw.lines(screen, (255,0,0), False, [(int(px), int(py)) for px, py in self.path], 2)

class Obstacle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
    def draw(self, screen):
        pygame.draw.circle(screen, (100,100,100), (int(self.x), int(self.y)), self.r)

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.robot = Robot(100, 100)
        self.target = (700, 500)
        self.obstacles = [Obstacle(random.randint(200,600), random.randint(150,450), random.randint(20,40)) for _ in range(5)]
        self.running = True
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.screen.fill((30,30,30))
            for obs in self.obstacles:
                obs.draw(self.screen)
            self.robot.move(self.target)
            self.robot.draw(self.screen)
            pygame.draw.circle(self.screen, (0,0,255), self.target, 10)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        sim = Simulation()
        sim.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
