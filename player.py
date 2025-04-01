import pygame
import math
from bullet import Bullet
import app

class Player:
    def __init__(self, x, y, assets, game):
        # Initialise the player with starting position (x, y) and necessary assets
        self.x = x
        self.y = y
        self.speed = app.PLAYER_SPEED  # Speed of the player

        # Player's experience points, level, and health
        self.xp = 0
        self.level = 1
        self.health = 5
        
        # Load player animations (idle and running)
        self.animations = assets["player"]
        self.state = "idle"  # Initial state of the player is 'idle'
        self.frame_index = 0  # Frame index for animation
        self.animation_timer = 0  # Timer to control animation speed
        self.animation_speed = 8  # Animation speed

        # Set up the player's initial image and rectangle for collision detection
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.facing_left = False  # To track the player's facing direction

        # Bullet-related settings
        self.bullet_speed = 10
        self.bullet_size = 10
        self.homing_bullet_count = 1
        self.homing_side_bullet_count = 0
        self.spray_bullet_count = 3
        self.shoot_cooldown = 1  # Reduced cooldown for rapid shooting
        self.shoot_timer = 0
        self.spray_timer = 1
        self.spray_interval = 60  # 3 seconds at 60 FPS
        self.bullets = []  # List to hold all bullets shot by the player

        # Flag to track if the player is selecting a power-up
        self.selecting_power_up = False
        self.game = game  # Reference to the game instance to check if game is paused

    def handle_input(self):
        # Handle user input for player movement
        if self.game.paused or self.game.in_level_up_menu:
            return  # If the game is paused or in level-up menu, don't process inputs

        keys = pygame.key.get_pressed()  # Get the currently pressed keys

        # Initialize velocity
        vel_x, vel_y = 0, 0

        # Check for movement inputs (arrow keys or WASD)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vel_x -= self.speed  # Move left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vel_x += self.speed  # Move right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vel_y -= self.speed  # Move up
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vel_y += self.speed  # Move down

        # Update player's position
        self.x += vel_x
        self.y += vel_y

        # Ensure the player doesn't move outside the screen boundaries
        self.x = max(0, min(self.x, app.WIDTH))
        self.y = max(0, min(self.y, app.HEIGHT))
        self.rect.center = (self.x, self.y)

        # Change player state to "run" if moving, otherwise "idle"
        if vel_x != 0 or vel_y != 0:
            self.state = "run"
        else:
            self.state = "idle"

        # Update facing direction
        if vel_x < 0:
            self.facing_left = True
        elif vel_x > 0:
            self.facing_left = False

    def update(self):
        # Update method for the player, called every frame
        if self.game.paused or self.game.in_level_up_menu:
            return  # If game is paused or in level-up menu, skip updates

        # Update all bullets
        for bullet in self.bullets:
            bullet.update()

            # Remove bullets that are off the screen
            if bullet.off_screen(app.WIDTH, app.HEIGHT):
                self.bullets.remove(bullet)

        # Animate the player (change the frame based on the animation speed)
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        # Update timers for shooting
        self.shoot_timer += 1
        self.spray_timer += 1

        # Shoot spray bullets if the timer exceeds the interval
        if self.spray_timer >= self.spray_interval:
            self.shoot_spray_bullets()
            self.spray_timer = 0

    def draw(self, surface):
        # Draw the player image on the screen
        if self.facing_left:
            flipped_img = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_img, self.rect)
        else:
            surface.blit(self.image, self.rect)

        # Draw all bullets
        for bullet in self.bullets:
            bullet.draw(surface)

    def take_damage(self, amount):
        # Reduce player's health when taking damage
        self.health = max(0, self.health - amount)

    def shoot_toward_position(self, tx, ty):
        # Shoot bullets towards a given position (tx, ty)
        if self.shoot_timer < self.shoot_cooldown or self.game.paused or self.game.in_level_up_menu:
            return  # If shooting cooldown hasn't passed or game is paused, don't shoot

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return

        # Calculate velocity of bullet in x and y directions
        vx = (dx / dist) * self.bullet_speed
        vy = (dy / dist) * self.bullet_speed

        # Shoot homing bullets
        for _ in range(self.homing_bullet_count):
            bullet = Bullet(self.x, self.y, vx, vy, self.bullet_size, color=(0, 0, 255))  # Blue bullets for homing
            self.bullets.append(bullet)

        # Shoot side bullets
        angle_offset = math.radians(15)
        for i in range(1, self.homing_side_bullet_count + 1):
            # Create side bullets at an angle to the main bullet's trajectory
            angle_left = math.atan2(vy, vx) - i * angle_offset
            angle_right = math.atan2(vy, vx) + i * angle_offset
            vx_left = math.cos(angle_left) * self.bullet_speed
            vy_left = math.sin(angle_left) * self.bullet_speed
            vx_right = math.cos(angle_right) * self.bullet_speed
            vy_right = math.sin(angle_right) * self.bullet_speed
            bullet_left = Bullet(self.x, self.y, vx_left, vy_left, self.bullet_size, color=(0, 0, 255))  # Blue for side bullets
            bullet_right = Bullet(self.x, self.y, vx_right, vy_right, self.bullet_size, color=(0, 0, 255))  # Blue for side bullets
            self.bullets.append(bullet_left)
            self.bullets.append(bullet_right)

        # Reset shoot timer
        self.shoot_timer = 0

    def shoot_spray_bullets(self):
        # Shoot bullets in a spray pattern
        angle_offset = math.radians(360 / self.spray_bullet_count)
        base_angle = 0

        for i in range(self.spray_bullet_count):
            angle = base_angle + i * angle_offset
            final_vx = math.cos(angle) * self.bullet_speed
            final_vy = math.sin(angle) * self.bullet_speed
            bullet = Bullet(self.x, self.y, final_vx, final_vy, self.bullet_size, color=(255, 0, 0))  # Red bullets for spray
            self.bullets.append(bullet)

    def shoot_toward_mouse(self, pos):
        # Shoot toward the mouse position
        mx, my = pos
        self.shoot_toward_position(mx, my)

    def shoot_toward_enemy(self, enemy):
        # Shoot toward an enemy's position
        self.shoot_toward_position(enemy.x, enemy.y)

    def add_xp(self, amount):
        # Add experience points to the player
        self.xp += amount