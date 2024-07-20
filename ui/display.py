import pygame
import os
from enum import Enum, auto
from typing import Dict, Tuple, TypeAlias
from .input_handler import Event

Point2D: TypeAlias = Tuple[int, int]

pygame.init()
TITLE_FONT = pygame.font.Font(None, 96)
BUTTON_FONT = pygame.font.Font(None, 48)
    
class State(Enum):
    START_MENU = auto()
    MAIN_MENU = auto()
    VICTORY_MENU = auto()
    GAMING = auto()
    
class Display:
    def __init__(self, icon_paths: str, scale: Point2D = (800, 600)):
        self.scale = scale
        self.screen = pygame.display.set_mode(self.scale)
        self.state = State.START_MENU
        self._load_images(icon_paths)
        pygame.display.set_caption("Sokoban")

    def _load_images(self, icon_paths: str) -> None:
        self.icon_paths = icon_paths
        self.images = {}
        for tile, path in self.icon_paths.items():
            try:
                self.images[tile] = pygame.image.load(path)
            except:
                print(f"Failed to load image for tile {tile.name}")
                self.images[tile] = None

    def render(self, map) -> Tuple[dict, dict]:
        self.tile_size = min(self.scale[0] // map.scale[1], self.scale[1] // map.scale[0])
        self.screen.fill((0, 0, 0))
        for y, row in enumerate(map.tiles):
            for x, tile in enumerate(row):
                image = self.images.get(tile)
                if image:
                    scaled_image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                    self.screen.blit(scaled_image, (x * self.tile_size, y * self.tile_size))
        pygame.display.flip()
        return {}, {}
    
    def _show(self, text_pos: Dict[pygame.Surface, Point2D]) -> Dict[pygame.Surface, pygame.Rect]:
        text_rect = {text:text.get_rect(
            center=(self.scale[0] * text_pos[text][0], self.scale[1] * text_pos[text][1]))
                     for text in text_pos.keys()}
        self.screen.fill((0, 0, 0))
        for text, rect in text_rect.items():
            self.screen.blit(text, rect)
        pygame.display.flip()
        return text_rect
                    
    def victory_menu(self, lvl_num: int) \
        -> Tuple[Dict[pygame.Surface, pygame.Rect], Dict[pygame.Surface, Event]]:
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
        text_rect = self._show(text_pos)
        return text_rect, text_event
                    
    def start_menu(self) \
        -> Tuple[Dict[pygame.Surface, pygame.Rect], Dict[pygame.Surface, Event]]:
        title_text = TITLE_FONT.render("Sokoban", True, (255, 255, 255))
        start_text = BUTTON_FONT.render("Start Game", True, (255, 255, 255))
        generate_text = BUTTON_FONT.render("Generate Level", True, (255, 255, 255))
        exit_text = BUTTON_FONT.render("Exit", True, (255, 255, 255))
        text_event = {
            start_text: Event.START,
            generate_text: Event.GENERATE,
            exit_text: Event.EXIT
        }
        text_pos = {
            title_text: (0.5, 0.2),
            start_text: (0.5, 0.4),
            generate_text: (0.5, 0.5),
            exit_text: (0.5, 0.6)
        }
        text_rect = self._show(text_pos)
        return text_rect, text_event
                    
    def main_menu(self, lvl_num: int) \
        -> Tuple[Dict[pygame.Surface, pygame.Rect], Dict[pygame.Surface, Event]]:
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
        text_rect = self._show(text_pos)
        return text_rect, text_event
                    
    def run(self, map: map, lvl_num: int) \
        -> Tuple[Dict[pygame.Surface, pygame.Rect], Dict[pygame.Surface, Event]]:
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