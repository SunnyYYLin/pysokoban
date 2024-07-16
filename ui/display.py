import pygame
import os
from game.map import SPACE, GOALBOX, GOALPLAYER, BOX, GOAL, WALL, PLAYER, Map
from enum import Enum, auto

class Mode(Enum):
    """
    Represents the game modes.

    Attributes:
        HUMAN: The human player mode.
        AI: The AI player mode.
    """
    HUMAN = auto()
    AI = auto()
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
        icon_style = "images"
        self.image_paths = {
            GOALBOX: os.path.join(assets_path, icon_style, "goalbox.png"),
            GOALPLAYER: os.path.join(assets_path, icon_style, "goalplayer.png"),
            BOX: os.path.join(assets_path, icon_style, "box.png"),
            GOAL: os.path.join(assets_path, icon_style, "goal.png"),
            WALL: os.path.join(assets_path, icon_style, "wall.png"),
            PLAYER: os.path.join(assets_path, icon_style, "player.png"),
            SPACE: os.path.join(assets_path, icon_style, "space.png"),
        }
        self.images = {}
        for tile, path in self.image_paths.items():
            try:
                self.images[tile] = pygame.image.load(path)
            except:
                print(f"Failed to load image for tile {tile}")
                self.images[tile] = None

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

    def select_mode(self) -> Mode:
        """
        Displays a mode selection menu and returns the selected mode.

        Returns:
            Mode: The selected game mode.
        """
        font = pygame.font.Font(None, 36)
        ai_text = font.render("AI Mode", True, (255, 255, 255))
        human_text = font.render("Human Mode", True, (255, 255, 255))
        ai_rect = ai_text.get_rect(center=(200, 100))
        human_rect = human_text.get_rect(center=(200, 200))

        while True:
            self.screen.fill((0, 0, 0))
            self.screen.blit(ai_text, ai_rect)
            self.screen.blit(human_text, human_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if ai_rect.collidepoint(event.pos):
                        return Mode.AI
                    elif human_rect.collidepoint(event.pos):
                        return Mode.HUMAN