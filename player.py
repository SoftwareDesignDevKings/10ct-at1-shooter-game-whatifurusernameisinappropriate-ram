import pygame
import app
import math

from bullet import Bullet

class Player:
    def __init__(self, x, y, assets):
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
        self.bullet_count = 1
        self.shoot_cooldown = 1  # Reduced cooldown for rapid shooting
        self.shoot_timer = 0
        self.bullets = []

        self.power_up = None
        self.selecting_power_up = False

    def handle_input(self):
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

        # Check for level up
        self.check_level_up()

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
        if self.shoot_timer < self.shoot_cooldown:
            return

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return

        vx = (dx / dist) * self.bullet_speed
        vy = (dy / dist) * self.bullet_speed

        if self.power_up == "spread":
            self.shoot_spread(vx, vy)
        elif self.power_up == "minigun":
            self.shoot_minigun(vx, vy)
        elif self.power_up == "360":
            self.shoot_360()
        else:
            bullet = Bullet(self.x, self.y, vx, vy, self.bullet_size)
            self.bullets.append(bullet)

        self.shoot_timer = 0

    def shoot_spread(self, vx, vy):
        angle_spread = 10
        base_angle = math.atan2(vy, vx)
        mid = (self.bullet_count - 1) / 2

        for i in range(3):  # Shoot 3 bullets in a spread
            offset = i - mid
            spread_radians = math.radians(angle_spread * offset)
            angle = base_angle + spread_radians
            final_vx = math.cos(angle) * self.bullet_speed
            final_vy = math.sin(angle) * self.bullet_speed

            bullet = Bullet(self.x, self.y, final_vx, final_vy, self.bullet_size)
            self.bullets.append(bullet)

    def shoot_minigun(self, vx, vy):
        bullet = Bullet(self.x, self.y, vx, vy, self.bullet_size)
        self.bullets.append(bullet)

    def shoot_360(self):
        for angle in range(0, 360, 30):  # Shoot bullets in 360 degrees
            radians = math.radians(angle)
            vx = math.cos(radians) * self.bullet_speed
            vy = math.sin(radians) * self.bullet_speed
            bullet = Bullet(self.x, self.y, vx, vy, self.bullet_size)
            self.bullets.append(bullet)

    def shoot_toward_mouse(self, pos):
        mx, my = pos
        self.shoot_toward_position(mx, my)

    def shoot_toward_enemy(self, enemy):
        self.shoot_toward_position(enemy.x, enemy.y)

    def add_xp(self, amount):
        self.xp += amount

    def check_level_up(self):
        level_up_xp = self.level * 5  # Reduced XP required to level up
        if self.xp >= level_up_xp:
            self.level += 1
            self.xp -= level_up_xp
            self.display_level_up_message()

            if self.level % 5 == 0:
                self.selecting_power_up = True

    def display_level_up_message(self):
        print(f"Level Up! You are now level {self.level}")

    def handle_power_up_selection(self, key):
        if key == pygame.K_1:
            self.power_up = "360"
            self.selecting_power_up = False
        elif key == pygame.K_2:
            self.power_up = "spread"
            self.selecting_power_up = False
        elif key == pygame.K_3:
            self.power_up = "minigun"
            self.selecting_power_up = False