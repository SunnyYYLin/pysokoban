import pygame
from game.problem import SokobanProblem, SokobanAction
from ui.display import Display, Event, State
from ui.input_handler import InputHandler
import os

class Game:

    def __init__(self):
        """
        Initializes the Game object.

        It sets the initial level number, loads the first level, display, and input handler objects.
        """
        self.lvl_num = 0
        self.input_handler = InputHandler()
        self.display = Display()
        self.running = True
        
    def _load_level(self, lvl_num: int) -> bool:
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
        return True

    def run(self):
        """
        Runs the game loop.

        It handles player input, updates the player, renders the display,
        checks if the level is complete, and manages the game flow.
        """
        clock = pygame.time.Clock()
        while self.running:
            match self.display.run():
                case Event.RUN:
                    key = self.input_handler.handle_events()
                    if key == SokobanAction.PAUSE:
                        self.display.state = State.MAIN_MENU
                    elif key:
                        print(key.name)
                        self.map = self.problem.result(self.map, key)
                        self.display.state = State.GAMING
                    if self.problem.is_goal(self.map):
                        self.display.state = State.VICTORY_MENU
                case Event.CONTINUE:
                    self.display.state = State.GAMING
                case Event.EXIT:
                    print("Exiting game...")
                    pygame.quit()
                    quit()
                case Event.START:
                    self.lvl_num += 1
                    self._load_level(self.lvl_num)
                    self.display.load_map(self.map, self.lvl_num)
                    self.display.state = State.GAMING
                case Event.ASK_AI:
                    pass
                case _:
                    raise ValueError("Invalid event")
            clock.tick(60)