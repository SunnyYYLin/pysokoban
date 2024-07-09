import pygame
from game.level import Level
from game.player import Player
from ui.display import Display
from ui.input_handler import InputHandler
import os

class Game:
    def __init__(self):
        self.display = Display()
        self.lvl_num = 1
        self.level = Level(os.path.join("levels", f"level{self.lvl_num}.txt"))
        self.player = Player(self.level)
        self.input_handler = InputHandler(self.player)
        self.running = True

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            key = self.input_handler.handle_events()
            self.player.update(key)
            self.display.render(self.level)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()