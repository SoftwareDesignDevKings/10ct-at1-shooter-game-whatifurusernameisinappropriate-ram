import app

class Coin:
    def __init__(self, x, y):
        # Initialise the coin with its position (x, y)
        self.x = x
        self.y = y
        
        # Create a surface for the coin with transparency (SRCALPHA)
        # The coin is represented as a small 15x15 surface
        self.image = app.pygame.Surface((15, 15), app.pygame.SRCALPHA)
        
        # Fill the coin surface with a gold color (RGB value for gold is (255, 215, 0))
        self.image.fill((255, 215, 0))
        
        # Get the rectangular area of the coin image for collision detection
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, surface):
        # Draw the coin on the given surface at its current position
        surface.blit(self.image, self.rect)