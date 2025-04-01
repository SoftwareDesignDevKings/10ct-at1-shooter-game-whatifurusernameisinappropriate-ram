import pygame
import app

class Enemy:
    def __init__(self, x, y, enemy_type, animations):
        # Initialise the enemy with position (x, y), type, and animations
        self.x = x
        self.y = y
        self.speed = app.DEFAULT_ENEMY_SPEED  # Default enemy speed from app settings
        self.enemy_type = enemy_type  # Type of the enemy (could be used for different behaviors)
        self.animations = animations  # Dictionary of animations for the enemy
        self.state = "idle"  # Enemy starts in the 'idle' state
        self.frame_index = 0  # Frame index for animations
        self.animation_timer = 0  # Timer for controlling animation speed
        self.animation_speed = 8  # Speed of animation frames
        self.image = self.animations[self.frame_index]  # Initial image of the enemy based on the frame index
        self.rect = self.image.get_rect(center=(self.x, self.y))  # Rectangle for collision detection
        self.knockback = False  # Flag to track if the enemy is being knocked back
        self.knockback_speed = app.ENEMY_KNOCKBACK_SPEED  # Speed of knockback from app settings
        self.knockback_direction = (0, 0)  # Direction of knockback
        self.knockback_duration = 10  # Duration of knockback (in frames)
        self.knockback_timer = 0  # Timer to track knockback duration

    def update(self, player):
        # Update the enemy's state and position each frame
        if player.game.paused or player.game.in_level_up_menu:
            return  # If the game is paused or in level-up menu, skip the update

        if self.knockback:
            # Apply knockback effect to the enemy
            self.x += self.knockback_direction[0] * self.knockback_speed
            self.y += self.knockback_direction[1] * self.knockback_speed
            
            # Update the knockback timer
            self.knockback_timer += 1
            if self.knockback_timer >= self.knockback_duration:
                self.knockback = False  # End the knockback effect after the duration
                self.knockback_timer = 0  # Reset knockback timer
        else:
            # Move towards the player if not knocked back
            dx = player.x - self.x  # Horizontal distance to player
            dy = player.y - self.y  # Vertical distance to player
            dist = (dx**2 + dy**2) ** 0.5  # Calculate the distance to the player
            if dist != 0:
                # Move the enemy towards the player
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

        # Update the enemy's rectangle position
        self.rect.center = (self.x, self.y)

        # Call the animate function to update the enemy's animation
        self.animate()

    def animate(self):
        # Update the enemy's animation based on the timer
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0  # Reset the animation timer
            self.frame_index = (self.frame_index + 1) % len(self.animations)  # Loop through frames
            self.image = self.animations[self.frame_index]  # Set the new animation frame

    def draw(self, surface):
        # Draw the enemy on the screen at its current position
        surface.blit(self.image, self.rect)

    def set_knockback(self, px, py, distance):
        # Set the knockback direction and apply knockback effect
        dx = self.x - px  # Horizontal distance from the player
        dy = self.y - py  # Vertical distance from the player
        dist = (dx**2 + dy**2) ** 0.5  # Calculate the distance from the player
        if dist != 0:
            # Set the knockback direction based on the distance from the player
            self.knockback_direction = (dx / dist, dy / dist)
            self.knockback = True  # Enable knockback effect
            self.knockback_timer = 0  # Reset knockback timer
