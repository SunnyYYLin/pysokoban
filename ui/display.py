import pygame
import os
from game.level import SPACE, GOALBOX, GOALPLAYER, BOX, GOAL, WALL, PLAYER, Pos, Tile

class Display:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Sokoban")
        self.assets_path = "assets"
        self.images = {}
        self.load_images()

    def load_images(self):
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
        self.screen.fill((0, 0, 0))
        for y, row in enumerate(level.tiles):
            for x, tile in enumerate(row):
                image = self.images.get(tile)
                if image:
                    self.screen.blit(image, (x * 64, y * 64))