import app
import math
import pygame

class Bullet:
    def __init__(self, x, y, vx, vy, size, color=(255, 0, 0)):  # Default color is red
        # Initialise the bullet's position (x, y) and velocity (vx, vy)
        self.x = x
        self.y = y
        self.vx = vx  # Horizontal velocity
        self.vy = vy  # Vertical velocity
        self.size = size  # Size of the bullet
        self.color = color  # Store color as a property (default red)
        
        # Create the bullet image based on size and color
        self.image = self.create_bullet_image()
        
        # Get the rectangular area for the bullet image, used for positioning and collision detection
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def create_bullet_image(self):
        """Creates and returns the surface for the bullet image."""
        # Create a surface with the given size
        bullet_image = pygame.Surface((self.size, self.size))
        
        # Fill the surface with the specified color
        bullet_image.fill(self.color)
        
        return bullet_image

    def update(self):
        """Updates the bullet's position based on its velocity."""
        # Update the bullet's x and y positions by adding the velocity components
        self.x += self.vx
        self.y += self.vy
        
        # Update the bullet's rectangle position (used for drawing and collision detection)
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        """Draws the bullet on the given screen."""
        # Blit (draw) the bullet image onto the screen at the bullet's current position
        screen.blit(self.image, self.rect.topleft)

    def off_screen(self, width, height):
        """Checks if the bullet is off the screen."""
        # Return True if the bullet is out of bounds (either x or y is outside the screen)
        return self.x < 0 or self.x > width or self.y < 0 or self.y > height
