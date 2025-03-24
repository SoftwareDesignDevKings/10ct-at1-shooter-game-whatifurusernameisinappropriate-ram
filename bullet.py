# bullet.py
import app
import math
import pygame

class Bullet:
    def __init__(self, x, y, vx, vy, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 0, 0))  # Red color for the bullet
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def off_screen(self, width, height):
        return self.x < 0 or self.x > width or self.y < 0 or self.y > height