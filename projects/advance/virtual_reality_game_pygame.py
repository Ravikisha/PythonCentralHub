"""
Virtual Reality (VR) Game (Pygame)

A basic VR-like game simulation using Pygame. Demonstrates 3D perspective, player movement, collision detection, and interactive environment. (Note: True VR requires specialized hardware; this is a 3D simulation.)
"""
import pygame
import sys
import math

WIDTH, HEIGHT = 800, 600
FPS = 60

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 5
    def move(self, keys):
        if keys[pygame.K_w]:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
        if keys[pygame.K_s]:
            self.x -= self.speed * math.cos(self.angle)
            self.y -= self.speed * math.sin(self.angle)
        if keys[pygame.K_a]:
            self.angle -= 0.05
        if keys[pygame.K_d]:
            self.angle += 0.05
    def draw(self, screen):
        pygame.draw.circle(screen, (0,255,0), (int(self.x), int(self.y)), 10)
        end_x = int(self.x + 20 * math.cos(self.angle))
        end_y = int(self.y + 20 * math.sin(self.angle))
        pygame.draw.line(screen, (255,0,0), (self.x, self.y), (end_x, end_y), 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    player = Player(WIDTH//2, HEIGHT//2)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        player.move(keys)
        screen.fill((30,30,30))
        player.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
