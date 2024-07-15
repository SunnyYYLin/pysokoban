import pygame
import os
from game.map import SPACE, GOALBOX, GOALPLAYER, BOX, GOAL, WALL, PLAYER, Map

class Display:
    """
    Represents the display for the Sokoban game.
    
    Attributes:
        tile_size (int): The size of each tile in pixels.
        scale (tuple): The scale of the display in pixels, calculated based on the map scale.
        screen (pygame.Surface): The surface representing the game display.
        image_paths (dict): A dictionary mapping tile types to their corresponding image paths.
        images (dict): A dictionary mapping tile types to their corresponding loaded images.

    Methods:
        __init__(self, map: Map): Initializes the Display object.
        load_images(self): Loads the images for each tile type.
        render(self, map: Map): Renders the game map on the display.
    """
    def __init__(self, map: Map):
        """
        Initializes the Display object.

        Args:
            map (Map): The map object representing the game map.
        """
        self.tile_size = 400 // max(map.scale)
        self.scale = tuple(self.tile_size * length for length in map.scale)
        self.screen = pygame.display.set_mode(self.scale)
        pygame.display.set_caption("Sokoban")
        self.load_images()

    def load_images(self):
        """
        Loads the images for each tile type.

        Raises:
            ValueError: If an image fails to load for a tile.
        """
        assets_path = "assets"
        self.image_paths = {
            GOALBOX: os.path.join(assets_path, "images", "goalbox.png"),
            GOALPLAYER: os.path.join(assets_path, "images", "goalplayer.png"),
            BOX: os.path.join(assets_path, "images", "box.png"),
            GOAL: os.path.join(assets_path, "images", "goal.png"),
            WALL: os.path.join(assets_path, "images", "wall.png"),
            PLAYER: os.path.join(assets_path, "images", "player.png")
        }
        self.images = {}
        for tile, path in self.image_paths.items():
            if tile == SPACE:
                self.images[tile] = None
            else:
                try:
                    self.images[tile] = pygame.image.load(path)
                except:
                    raise ValueError(f"Failed to load image for tile {tile}")

    def render(self, map: Map):
        """
        Renders the game map on the display.

        Args:
            map (Map): The map object representing the game map.
        """
        self.screen.fill((0, 0, 0))
        for y, row in enumerate(map.tiles):
            for x, tile in enumerate(row):
                image = self.images.get(tile)
                if image:
                    scaled_image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                    self.screen.blit(scaled_image, (x * self.tile_size, y * self.tile_size))
