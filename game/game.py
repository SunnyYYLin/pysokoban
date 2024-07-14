import pygame
from game.level import Level
from game.player import Player
from ui.display import Display
from ui.input_handler import InputHandler
import os

class Game:
    """
    Represents the game logic and controls the game flow.

    Attributes:
        lvl_num (int): The current level number.
        level (Level): The current level object.
        player (Player): The player object.
        display (Display): The display object.
        input_handler (InputHandler): The input handler object.
        running (bool): Flag indicating if the game is running.

    Methods:
        __init__(): Initializes the Game object.
        load_level(lvl_num: int) -> bool: Loads the specified level.
        run(): Runs the game loop.
    """

    def __init__(self):
        """
        Initializes the Game object.

        It sets the initial level number, loads the first level,
        and initializes the player, display, and input handler objects.
        """
        self.lvl_num = 1
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
            self.level = Level(os.path.join("levels", f"level{lvl_num}.txt"))
        except:
            return False
        self.player = Player(self.level)
        self.display = Display(self.level)
        self.input_handler = InputHandler(self.player)
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