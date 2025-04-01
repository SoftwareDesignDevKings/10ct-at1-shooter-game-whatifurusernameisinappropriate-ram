# Import necessary libraries
import pygame
import os

# --------------------------------------------------------------------------
#                               CONSTANTS
# --------------------------------------------------------------------------

# Game screen dimensions and frames per second
WIDTH = 800
HEIGHT = 600
FPS = 60

# Player and enemy movement speeds
PLAYER_SPEED = 3
DEFAULT_ENEMY_SPEED = 3
ENEMY_SPEED_INCREMENT = 2  # Speed increment for enemies with each level

# Margin around the edges of the screen where enemies can spawn
SPAWN_MARGIN = 50

# Scale factors for various assets (used for resizing images)
ENEMY_SCALE_FACTOR = 2
PLAYER_SCALE_FACTOR = 2
FLOOR_TILE_SCALE_FACTOR = 2
HEALTH_SCALE_FACTOR = 1

# Knockback properties for enemy interactions
PUSHBACK_DISTANCE = 100
ENEMY_KNOCKBACK_SPEED = 5

# --------------------------------------------------------------------------
#                       ASSET LOADING FUNCTIONS
# --------------------------------------------------------------------------

def load_frames(prefix, frame_count, scale_factor=1, folder="assets"):
    """
    Loads frames for an animation. Each frame is an image.
    
    Arguments:
    - prefix: The name of the image files (without number or extension).
    - frame_count: Number of frames to load.
    - scale_factor: The factor to scale images by (default is 1, no scaling).
    - folder: The folder where assets are located (default is "assets").
    
    Returns:
    - A list of Pygame surfaces representing the frames.
    """
    frames = []
    for i in range(frame_count):
        image_path = os.path.join(folder, f"{prefix}_{i}.png")  # Construct file path
        img = pygame.image.load(image_path).convert_alpha()  # Load and convert image
        
        # Scale the image if scale_factor is not 1
        if scale_factor != 1:
            w = img.get_width() * scale_factor
            h = img.get_height() * scale_factor
            img = pygame.transform.scale(img, (w, h))

        frames.append(img)  # Add the frame to the list
    return frames

def load_floor_tiles(folder="assets"):
    """
    Loads floor tiles for the background.
    
    Arguments:
    - folder: The folder where assets are located (default is "assets").
    
    Returns:
    - A list of Pygame surfaces representing the floor tiles.
    """
    floor_tiles = []
    for i in range(8):  # Assuming there are 8 floor tiles
        path = os.path.join(folder, f"floor_{i}.png")
        tile = pygame.image.load(path).convert()  # Load the floor tile image

        # Scale the tile image if needed
        if FLOOR_TILE_SCALE_FACTOR != 1:
            tw = tile.get_width() * FLOOR_TILE_SCALE_FACTOR
            th = tile.get_height() * FLOOR_TILE_SCALE_FACTOR
            tile = pygame.transform.scale(tile, (tw, th))

        floor_tiles.append(tile)  # Add the tile to the list
    return floor_tiles

def load_assets():
    """
    Loads all game assets (images, animations, etc.).
    
    Returns:
    - A dictionary containing all game assets, such as enemies, player animations, floor tiles, and health images.
    """
    assets = {}

    # Load enemy frames (animations)
    assets["enemies"] = {
        "orc":    load_frames("orc",    4, scale_factor=ENEMY_SCALE_FACTOR),
        "undead": load_frames("undead", 4, scale_factor=ENEMY_SCALE_FACTOR),
        "demon":  load_frames("demon",  4, scale_factor=ENEMY_SCALE_FACTOR),
    }

    # Load player frames (animations)
    assets["player"] = {
        "idle": load_frames("player_idle", 4, scale_factor=PLAYER_SCALE_FACTOR),
        "run":  load_frames("player_run",  4, scale_factor=PLAYER_SCALE_FACTOR),
    }

    # Load floor tiles for background
    assets["floor_tiles"] = load_floor_tiles()

    # Load health images (for player health display)
    assets["health"] = load_frames("health", 6, scale_factor=HEALTH_SCALE_FACTOR)

    return assets

# --------------------------------------------------------------------------
#                               GAME LOOP
# --------------------------------------------------------------------------

def main():
    """
    Main game loop that initializes Pygame, updates the game state, and handles events.
    """
    pygame.init()  # Initialize Pygame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set up the game window
    clock = pygame.time.Clock()  # Create a clock to control the frame rate

    level = 1  # Starting level
    enemy_speed = DEFAULT_ENEMY_SPEED + (ENEMY_SPEED_INCREMENT * (level - 1))  # Calculate enemy speed

    running = True
    while running:
        for event in pygame.event.get():  # Event handling loop
            if event.type == pygame.QUIT:  # Check if the user closed the window
                running = False

        # Update enemy speed based on the current level
        enemy_speed = DEFAULT_ENEMY_SPEED + (ENEMY_SPEED_INCREMENT * (level - 1))

        # Game logic: Spawn enemies, update player, etc. (not implemented here)
        # level += 1  # Uncomment to automatically level up

        # Fill the screen with black color
        screen.fill((0, 0, 0))

        pygame.display.flip()  # Update the screen
        clock.tick(FPS)  # Limit the frame rate to FPS

    pygame.quit()  # Quit Pygame when done

# Check if this script is being run directly (as opposed to being imported)
if __name__ == "__main__":
    main()  # Run the main game loop