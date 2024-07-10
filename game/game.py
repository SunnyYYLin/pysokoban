import pygame
from game.level import Level
from game.player import Player
from ui.display import Display
from ui.input_handler import InputHandler
import os

class Game:
    def __init__(self):
        self.lvl_num = 1
        assert self.load_level(self.lvl_num), "Failed to load level"
        self.running = True
        
    def load_level(self, lvl_num: int) -> bool:
        try:
            self.level = Level(os.path.join("levels", f"level{lvl_num}.txt"))
        except:
            return False
        self.player = Player(self.level)
        self.display = Display(self.level)
        self.input_handler = InputHandler(self.player)
        return True

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            key = self.input_handler.handle_events()
            self.player.update(key)
            self.display.render(self.level)
            pygame.display.flip()
            if self.level.is_terminal():
                print(f"Level {self.lvl_num} Complete!")
                self.lvl_num += 1
                if not self.load_level(self.lvl_num):
                    self.running = False
            clock.tick(60)
        pygame.quit()