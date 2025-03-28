import pygame
import app

class Enemy:
    def __init__(self, x, y, enemy_type, animations):
        self.x = x
        self.y = y
        self.speed = app.DEFAULT_ENEMY_SPEED
        self.enemy_type = enemy_type
        self.animations = animations
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8
        self.image = self.animations[self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.knockback = False
        self.knockback_speed = app.ENEMY_KNOCKBACK_SPEED
        self.knockback_direction = (0, 0)

    def update(self, player):
        if player.game.paused or player.game.in_level_up_menu:
            return

        if self.knockback:
            self.x += self.knockback_direction[0] * self.knockback_speed
            self.y += self.knockback_direction[1] * self.knockback_speed
            self.knockback = False
        else:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = (dx**2 + dy**2) ** 0.5
            if dist != 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

        self.rect.center = (self.x, self.y)
        self.animate()

    def animate(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations)
            self.image = self.animations[self.frame_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def set_knockback(self, px, py, distance):
        dx = self.x - px
        dy = self.y - py
        dist = (dx**2 + dy**2) ** 0.5
        if dist != 0:
            self.knockback_direction = (dx / dist, dy / dist)
            self.knockback = True