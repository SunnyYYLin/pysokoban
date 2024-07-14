import pygame
import os
from game.level import SPACE, GOALBOX, GOALPLAYER, BOX, GOAL, WALL, PLAYER, Pos, Tile, Level

class Display:
    def __init__(self, level: Level):
        """
        Initializes the Display object.

        Args:
            level (Level): The level object representing the game level.
        """
        self.tile_size = 400 // max(level.scale)
        self.scale = tuple(self.tile_size * length for length in level.scale)
        print(self.scale)
        self.screen = pygame.display.set_mode(self.scale)
        pygame.display.set_caption("Sokoban")
        self.assets_path = "assets"
        
        self.images = {}
        self.load_images()

    def load_images(self):
        """
        Loads the images for each tile type.

        Raises:
            Exception: If there is an error loading an image.
        """
        self.image_paths = {
            SPACE: os.path.join(self.assets_path, "images", "space.png"),
            GOALBOX: os.path.join(self.assets_path, "images", "goalbox.png"),
            GOALPLAYER: os.path.join(self.assets_path, "images", "goalplayer.png"),
            BOX: os.path.join(self.assets_path, "images", "box.png"),
            GOAL: os.path.join(self.assets_path, "images", "goal.png"),
            WALL: os.path.join(self.assets_path, "images", "wall.png"),
            PLAYER: os.path.join(self.assets_path, "images", "player.png")
        }
        for tile, path in self.image_paths.items():
            try:
                self.images[tile] = pygame.image.load(path)
            except:
                print(f"Error loading image for {tile}")
                self.images[tile] = None

    def render(self, level):
        """
        Renders the game level on the display.

        Args:
            level (Level): The level object representing the game level.
        """
        self.screen.fill((0, 0, 0))
        for y, row in enumerate(level.tiles):
            for x, tile in enumerate(row):
                image = self.images.get(tile)
                if image:
                    if image:
                        # 调整图像大小以匹配格子的大小
                        scaled_image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                        self.screen.blit(scaled_image, (x * self.tile_size, y * self.tile_size))