import pygame
import math
from bullet import Bullet
import app

class Player:
    def __init__(self, x, y, assets, game):
        self.x = x
        self.y = y
        self.speed = app.PLAYER_SPEED

        self.xp = 0
        self.level = 1
        self.health = 5
        
        self.animations = assets["player"]
        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.facing_left = False

        self.health = 5

        self.bullet_speed = 10
        self.bullet_size = 10
        self.homing_bullet_count = 1
        self.homing_side_bullet_count = 0
        self.spray_bullet_count = 3
        self.shoot_cooldown = 1  # Reduced cooldown for rapid shooting
        self.shoot_timer = 0
        self.spray_timer = 0
        self.spray_interval = 180  # 3 seconds at 60 FPS
        self.bullets = []

        self.selecting_power_up = False
        self.game = game  # Reference to the game instance

    def handle_input(self):
        if self.game.paused or self.game.in_level_up_menu:
            return

        keys = pygame.key.get_pressed()

        vel_x, vel_y = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vel_x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vel_x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vel_y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vel_y += self.speed

        self.x += vel_x
        self.y += vel_y

        self.x = max(0, min(self.x, app.WIDTH))
        self.y = max(0, min(self.y, app.HEIGHT))
        self.rect.center = (self.x, self.y)

        if vel_x != 0 or vel_y != 0:
            self.state = "run"
        else:
            self.state = "idle"

        if vel_x < 0:
            self.facing_left = True
        elif vel_x > 0:
            self.facing_left = False

    def update(self):
        if self.game.paused or self.game.in_level_up_menu:
            return

        for bullet in self.bullets:
            bullet.update()

            if bullet.y > app.HEIGHT or bullet.x < 0 or bullet.x > app.WIDTH:
                self.bullets.remove(bullet)

        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        self.shoot_timer += 1
        self.spray_timer += 1

        if self.spray_timer >= self.spray_interval:
            self.shoot_spray_bullets()
            self.spray_timer = 0

    def draw(self, surface):
        if self.facing_left:
            flipped_img = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_img, self.rect)
        else:
            surface.blit(self.image, self.rect)

        for bullet in self.bullets:
            bullet.draw(surface)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def shoot_toward_position(self, tx, ty):
        if self.shoot_timer < self.shoot_cooldown or self.game.paused or self.game.in_level_up_menu:
            return

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return

        vx = (dx / dist) * self.bullet_speed
        vy = (dy / dist) * self.bullet_speed

        # Homing bullets
        for _ in range(self.homing_bullet_count):
            bullet = Bullet(self.x, self.y, vx, vy, self.bullet_size)
            self.bullets.append(bullet)

        # Side bullets
        angle_offset = math.radians(15)
        for i in range(1, self.homing_side_bullet_count + 1):
            angle_left = math.atan2(vy, vx) - i * angle_offset
            angle_right = math.atan2(vy, vx) + i * angle_offset
            vx_left = math.cos(angle_left) * self.bullet_speed
            vy_left = math.sin(angle_left) * self.bullet_speed
            vx_right = math.cos(angle_right) * self.bullet_speed
            vy_right = math.sin(angle_right) * self.bullet_speed
            bullet_left = Bullet(self.x, self.y, vx_left, vy_left, self.bullet_size)
            bullet_right = Bullet(self.x, self.y, vx_right, vy_right, self.bullet_size)
            self.bullets.append(bullet_left)
            self.bullets.append(bullet_right)

        self.shoot_timer = 0

    def shoot_spray_bullets(self):
        angle_offset = math.radians(360 / self.spray_bullet_count)
        base_angle = 0

        for i in range(self.spray_bullet_count):
            angle = base_angle + i * angle_offset
            final_vx = math.cos(angle) * self.bullet_speed
            final_vy = math.sin(angle) * self.bullet_speed
            bullet = Bullet(self.x, self.y, final_vx, final_vy, self.bullet_size)
            self.bullets.append(bullet)

    def shoot_toward_mouse(self, pos):
        mx, my = pos
        self.shoot_toward_position(mx, my)

    def shoot_toward_enemy(self, enemy):
        self.shoot_toward_position(enemy.x, enemy.y)

    def add_xp(self, amount):
        self.xp += amount