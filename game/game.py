import pygame
from game.problem import SokobanProblem
from ui.display import Display
from ui.input_handler import InputHandler
import os

class Game:

    def __init__(self):
        """
        Initializes the Game object.

        It sets the initial level number, loads the first level, display, and input handler objects.
        """
        self.lvl_num = 1
        self.input_handler = InputHandler()
        assert self.load_level(self.lvl_num), "Failed to load level"
        self.running = True
        
    def load_level(self, lvl_num: int) -> bool:
        """
        Loads the specified level.

        Args:
            lvl_num (int): The level number to load.

        Returns:
            bool: True if the level is loaded successfully, False otherwise.
        """
        try:
            self.problem = SokobanProblem(os.path.join("levels", f"level{lvl_num}.txt"))
        except:
            return False
        self.map = self.problem.initial_state()
        self.display = Display(self.map)
        
        return True

    def run(self):
        """
        Runs the game loop.

        It handles player input, updates the player, renders the display,
        checks if the level is complete, and manages the game flow.
        """
        clock = pygame.time.Clock()
        while self.running:
            key = self.input_handler.handle_events()
            if key:
                print(key.name)
                self.map = self.problem.result(self.map, key)
            self.display.render(self.map)
            pygame.display.flip()
            if self.problem.is_goal(self.map):
                print(f"Level {self.lvl_num} Complete!")
                self.lvl_num += 1
                if not self.load_level(self.lvl_num):
                    self.running = False
            clock.tick(60)
        pygame.quit()