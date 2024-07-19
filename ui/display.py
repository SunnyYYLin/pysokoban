import pygame
import os
from game.map import Tile, Map
from enum import Enum, auto

pygame.init()
TITLE_FONT = pygame.font.Font(None, 96)
BUTTON_FONT = pygame.font.Font(None, 48)

class Event(Enum):
    START = auto()
    RESTART = auto()
    CONTINUE = auto()
    EXIT = auto()
    ASK_AI = auto()
    RUN = auto()
    
class State(Enum):
    MAIN_MENU = auto()
    START_MENU = auto()
    VICTORY_MENU = auto()
    GAMING = auto()
    
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
    def __init__(self, scale=(800, 600)):
        """
        Initializes the Display object.

        Args:
            map (Map): The map object representing the game map.
        """
        self.scale = scale
        self.screen = pygame.display.set_mode(self.scale)
        self.state = State.START_MENU
        self.load_images()
        pygame.display.set_caption("Sokoban")

    def load_images(self):
        """
        Loads the images for each tile type.

        Raises:
            ValueError: If an image fails to load for a tile.
        """
        assets_path = "assets"
        icon_style = "images"
        self.image_paths = {
            Tile.GOALBOX: os.path.join(assets_path, icon_style, "goalbox.png"),
            Tile.GOALPLAYER: os.path.join(assets_path, icon_style, "goalplayer.png"),
            Tile.BOX: os.path.join(assets_path, icon_style, "box.png"),
            Tile.GOAL: os.path.join(assets_path, icon_style, "goal.png"),
            Tile.WALL: os.path.join(assets_path, icon_style, "wall.png"),
            Tile.PLAYER: os.path.join(assets_path, icon_style, "player.png"),
            Tile.SPACE: os.path.join(assets_path, icon_style, "space.png"),
        }
        self.images = {}
        for tile, path in self.image_paths.items():
            try:
                self.images[tile] = pygame.image.load(path)
            except:
                print(f"Failed to load image for tile {tile}")
                self.images[tile] = None

    def render(self, map) -> Event:
        self.tile_size = min(self.scale[0] // map.scale[1], self.scale[1] // map.scale[0])
        self.screen.fill((0, 0, 0))
        for y, row in enumerate(map.tiles):
            for x, tile in enumerate(row):
                image = self.images.get(tile)
                if image:
                    scaled_image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                    self.screen.blit(scaled_image, (x * self.tile_size, y * self.tile_size))
        pygame.display.flip()
        return Event.RUN
    
    def _show(self, text_pos, text_event) -> Event:
        text_rect = {text:text.get_rect(
            center=(self.scale[0] * text_pos[text][0], self.scale[1] * text_pos[text][1]))
                     for text in text_pos.keys()}
        while True:
            self.screen.fill((0, 0, 0))
            for text, rect in text_rect.items():
                self.screen.blit(text, rect)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return Event.EXIT
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return Event.START
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    return Event.ASK_AI
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    return Event.RESTART
                for text, ev in text_event.items():
                    if event.type == pygame.MOUSEBUTTONDOWN \
                        and text_rect[text].collidepoint(pygame.mouse.get_pos()):
                        print(f"Clicked {ev}")
                        return ev
                    
    def victory_menu(self, lvl_num: int) -> Event:
        victory_text = TITLE_FONT.render(f"Level {lvl_num} Complete!", True, (255, 255, 255))
        next_text = BUTTON_FONT.render("Next Level", True, (255, 255, 255))
        exit_text = BUTTON_FONT.render("Exit", True, (255, 255, 255))
        text_event = {
            next_text: Event.START,
            exit_text: Event.EXIT,
        }
        text_pos = {
            victory_text: (0.5, 0.4),
            next_text: (0.5, 0.6),
            exit_text: (0.5, 0.7)
        }
        return self._show(text_pos, text_event)
                    
    def start_menu(self) -> Event:
        title_text = TITLE_FONT.render("Sokoban", True, (255, 255, 255))
        start_text = BUTTON_FONT.render("Start Game", True, (255, 255, 255))
        exit_text = BUTTON_FONT.render("Exit", True, (255, 255, 255))
        text_event = {
            start_text: Event.START,
            exit_text: Event.EXIT
        }
        text_pos = {
            title_text: (0.5, 0.2),
            start_text: (0.5, 0.4),
            exit_text: (0.5, 0.5)
        }
        return self._show(text_pos, text_event)
                    
    def main_menu(self, lvl_num: int) -> Event:
        """
        Displays the main menu.

        Returns:
            Event: The event corresponding to the user's selection
        """
        title_text = TITLE_FONT.render(f"Level {lvl_num}", True, (255, 255, 255))
        start_text = BUTTON_FONT.render("Continue", True, (255, 255, 255))
        restart_text = BUTTON_FONT.render("Restart", True, (255, 255, 255))
        ai_text = BUTTON_FONT.render("Ask AI", True, (255, 255, 255))
        exit_text = BUTTON_FONT.render("Exit", True, (255, 255, 255))
        text_event = {
            start_text: Event.CONTINUE,
            restart_text: Event.RESTART,
            ai_text: Event.ASK_AI,
            exit_text: Event.EXIT
        }
        text_pos = {
            title_text: (0.5, 0.2),
            start_text: (0.5, 0.3),
            restart_text: (0.5, 0.4),
            ai_text: (0.5, 0.5),
            exit_text: (0.5, 0.6)
        }
        return self._show(text_pos, text_event)
                    
    def run(self, map: map, lvl_num: int) -> Event:
        match self.state:
            case State.GAMING:
                return self.render(map)
            case State.MAIN_MENU:
                return self.main_menu(lvl_num)
            case State.START_MENU:
                return self.start_menu()
            case State.VICTORY_MENU:
                return self.victory_menu(lvl_num)
            case _:
                raise ValueError("Invalid state")