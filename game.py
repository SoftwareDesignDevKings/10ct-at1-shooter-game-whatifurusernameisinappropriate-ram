import random
import os
import math
import pygame  # Ensure pygame is imported for audio
from player import Player
from enemy import Enemy
from coin import Coin
import app

class Game:
    def __init__(self):
        pygame.init()  # Initialize Pygame
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))  # Set up game window size
        pygame.display.set_caption("Shooter")  # Set window title
        self.clock = pygame.time.Clock()  # Create clock object to control the frame rate

        # Load game assets (images, animations, etc.)
        self.assets = app.load_assets()
        self.load_audio()  # Load audio for the game

        # Set font paths for rendering text
        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)

        # Create a random background from floor tiles
        self.background = self.create_random_background(
            app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        )

        # Initialize game state variables
        self.running = True
        self.game_over = False
        self.paused = False

        # Enemies and coins setup
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 60
        self.enemies_per_spawn = 1

        self.coins = []
        self.reset_game()  # Reset game to initial state

    def load_audio(self):
        """Load background music for the game."""
        pygame.mixer.music.load("assets/intense-black-metal-instrumental-304729.mp3")  # Load music file
        pygame.mixer.music.play(-1)  # Play music in a loop

    def reset_game(self):
        """Reset the game state to the initial conditions."""
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets, self)  # Initialize player at center
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 1
        self.coins = []
        self.game_over = False
        self.in_level_up_menu = False  # Track whether the player is in the upgrade menu
        self.upgrade_options = []  # Placeholder for upgrade options

    def create_random_background(self, width, height, floor_tiles):
        """
        Create a random background by tiling floor tiles across the screen.
        
        Arguments:
        - width, height: Screen dimensions.
        - floor_tiles: List of floor tiles to use for the background.
        
        Returns:
        - A Pygame surface representing the background.
        """
        bg = pygame.Surface((width, height))
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        # Tile the background by blitting floor tiles in a grid pattern
        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)  # Randomly choose a tile for each position
                bg.blit(tile, (x, y))

        return bg

    def run(self):
        """
        Main game loop: handles events, updates game state, and draws everything.
        """
        while self.running:
            self.clock.tick(app.FPS)  # Ensure the game runs at a consistent frame rate
            self.handle_events()  # Handle any user input or system events

            # If the game is not over and we're not in the level-up menu, update the game state
            if not self.game_over and not self.in_level_up_menu:
                self.update()
            
            self.draw()  # Draw everything to the screen
        
        pygame.mixer.music.stop()  # Stop the background music when quitting
        pygame.quit()  # Quit Pygame

    def handle_events(self):
        """
        Handle user input (keyboard, mouse, etc.) during the game loop.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the window is closed, stop the game
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:  # If the game is over, handle restart or quit
                    if event.key == pygame.K_r:
                        self.reset_game()  # Restart the game
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False  # Quit the game
                else:
                    # Normal gameplay controls
                    if not self.in_level_up_menu:
                        if event.key == pygame.K_SPACE:
                            # Shoot towards the nearest enemy when space is pressed
                            nearest_enemy = self.find_nearest_enemy()
                            if nearest_enemy:
                                self.player.shoot_toward_enemy(nearest_enemy)
                    else:
                        # In upgrade menu, handle number key presses to select upgrades
                        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                            index = event.key - pygame.K_1  # Map key press to index
                            if 0 <= index < len(self.upgrade_options):
                                upgrade = self.upgrade_options[index]
                                self.apply_upgrade(self.player, upgrade)
                                self.in_level_up_menu = False

    def apply_upgrade(self, player, upgrade):
        """
        Apply an upgrade to the player when they level up.
        
        Arguments:
        - player: The player object to apply the upgrade to.
        - upgrade: The upgrade object containing the upgrade details.
        """
        name = upgrade["name"]
        if name == "Bigger Bullet":
            player.bullet_size += 5
        elif name == "Extra Side Bullets":
            player.homing_side_bullet_count += 1
        elif name == "Spray Bullet":
            player.spray_bullet_count += 2
        elif name == "Shorter Cooldown":
            player.shoot_cooldown = max(1, int(player.shoot_cooldown * 0.8))

    def update(self):
        """
        Update the game state: handle player input, update player and enemies, check collisions, etc.
        """
        self.player.handle_input()  # Update player based on input
        self.player.update()  # Update player state (movement, actions, etc.)

        # Update enemies and handle their logic
        for enemy in self.enemies:
            enemy.update(self.player)

        # Check for collisions between player, enemies, bullets, and coins
        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()
        self.check_player_coin_collisions()

        if self.player.health <= 0:
            self.game_over = True  # End the game if player health reaches 0
            return
        
        self.spawn_enemies()  # Spawn enemies periodically
        self.check_for_level_up()  # Check if the player has enough XP for a level-up

    def draw(self):
        """
        Draw everything to the screen: background, player, enemies, health bar, etc.
        """
        self.screen.blit(self.background, (0, 0))  # Draw background

        # Draw coins on the screen
        for coin in self.coins:
            coin.draw(self.screen)

        # If game is not over, draw the player and enemies
        if not self.game_over:
            self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Draw upgrade menu if in level-up phase
        if self.in_level_up_menu:
            self.draw_upgrade_menu()
        
        # Draw the player's health bar
        hp = max(0, min(self.player.health, 5))  # Ensure health is between 0 and 5
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))

        # Draw XP and XP to next level
        xp_text_surf = self.font_small.render(f"XP: {self.player.xp}", True, (255, 255, 255))
        self.screen.blit(xp_text_surf, (10, 70))

        next_level_xp = self.player.level * self.player.level * 5
        xp_to_next = max(0, next_level_xp - self.player.xp)
        xp_next_surf = self.font_small.render(f"Next Lvl XP: {xp_to_next}", True, (255, 255, 255))
        self.screen.blit(xp_next_surf, (10, 100))

        # Draw the game over screen if the game is over
        if self.game_over:
            self.draw_game_over_screen()
        
        pygame.display.flip()  # Update the screen with all the drawn elements

    def pick_random_upgrades(self, num):
        """
        Pick a set of random upgrades for the player to choose from during level-up.
        
        Arguments:
        - num: Number of upgrades to pick.
        
        Returns:
        - A list of upgrade options.
        """
        possible_upgrades = [
            {"name": "Bigger Bullet",  "desc": "Bullet size +5"},
            {"name": "Extra Side Bullets", "desc": "+2 side bullets"},
            {"name": "Spray Bullet",   "desc": "+2 spray bullets"},
            {"name": "Shorter Cooldown", "desc": "Shoot more frequently"},
        ]
        return random.sample(possible_upgrades, k=num)

    def spawn_enemies(self):
        """
        Spawn enemies at random positions on the screen.
        """
        self.enemy_spawn_timer += 3
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0

            for _ in range(self.enemies_per_spawn):
                # Spawn enemies at one of the screen edges (top, bottom, left, right)
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x = random.randint(0, app.WIDTH)
                    y = -app.SPAWN_MARGIN
                elif side == "bottom":
                    x = random.randint(0, app.WIDTH)
                    y = app.HEIGHT + app.SPAWN_MARGIN
                elif side == "left":
                    x = -app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)
                else:
                    x = app.WIDTH + app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)

                enemy_type = random.choice(list(self.assets["enemies"].keys()))  # Random enemy type
                enemy = Enemy(x, y, enemy_type, self.assets["enemies"][enemy_type])
                self.enemies.append(enemy)

    def increase_enemy_spawn_rate(self):
        """Increase the rate at which enemies spawn."""
        self.enemy_spawn_interval = max(10, self.enemy_spawn_interval - 5)  # Decrease spawn interval

    def pause_game(self):
        """Pause the game."""
        self.paused = True

    def resume_game(self):
        """Resume the game."""
        self.paused = False

    def check_player_enemy_collisions(self):
        """
        Check if the player collides with any enemies and apply damage.
        """
        collided = False
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                collided = True
                break

        if collided:
            self.player.take_damage(1)  # Player takes damage if collided
            px, py = self.player.x, self.player.y
            for enemy in self.enemies:
                enemy.set_knockback(px, py, app.PUSHBACK_DISTANCE)

    def draw_upgrade_menu(self):
        """
        Draw the level-up menu where the player chooses an upgrade.
        """
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Darken the screen with a transparent overlay
        self.screen.blit(overlay, (0, 0))

        title_surf = self.font_large.render("Choose an Upgrade!", True, (255, 255, 0))
        title_rect = title_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 3 - 50))
        self.screen.blit(title_surf, title_rect)

        # Draw upgrade options
        for i, upgrade in enumerate(self.upgrade_options):
            text_str = f"{i+1}. {upgrade['name']} - {upgrade['desc']}"
            option_surf = self.font_small.render(text_str, True, (255, 255, 255))
            line_y = app.HEIGHT // 3 + i * 40
            option_rect = option_surf.get_rect(center=(app.WIDTH // 2, line_y))
            self.screen.blit(option_surf, option_rect)

    def find_nearest_enemy(self):
        """
        Find and return the nearest enemy to the player.
        
        Returns:
        - The nearest enemy object or None if no enemies exist.
        """
        if not self.enemies:
            return None
        nearest = None
        min_dist = float('inf')
        px, py = self.player.x, self.player.y
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        return nearest

    def check_bullet_enemy_collisions(self):
        """
        Check if any player's bullets collide with enemies.
        If so, destroy the enemy and drop a coin.
        """
        for bullet in self.player.bullets[:]:  # Iterate over a copy of the list
            for enemy in self.enemies[:]:  # Iterate over a copy of the list
                if bullet.rect.colliderect(enemy.rect):
                    new_coin = Coin(enemy.x, enemy.y)
                    self.coins.append(new_coin)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)

    def check_player_coin_collisions(self):
        """
        Check if the player collects any coins.
        """
        coins_collected = []
        for coin in self.coins:
            if coin.rect.colliderect(self.player.rect):
                coins_collected.append(coin)
                self.player.add_xp(1)  # Increase XP for collecting coins

        for c in coins_collected:
            if c in self.coins:
                self.coins.remove(c)

    def check_for_level_up(self):
        """
        Check if the player has enough XP to level up.
        """
        xp_needed = self.player.level * self.player.level * 5
        if self.player.xp >= xp_needed:
            self.player.level += 1
            self.in_level_up_menu = True
            self.upgrade_options = self.pick_random_upgrades(3)
            self.enemies_per_spawn += 5  # Increase enemy spawns per level

    def draw_game_over_screen(self):
        """
        Draw the game over screen when the player loses.
        """
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Darken the screen
        self.screen.blit(overlay, (0, 0))

        game_over_surf = self.font_large.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
        self.screen.blit(game_over_surf, game_over_rect)

        restart_surf = self.font_small.render("Press R to Restart", True, (255, 255, 255))
        restart_rect = restart_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
        self.screen.blit(restart_surf, restart_rect)

        quit_surf = self.font_small.render("Press ESC to Quit", True, (255, 255, 255))
        quit_rect = quit_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 60))
        self.screen.blit(quit_surf, quit_rect)
