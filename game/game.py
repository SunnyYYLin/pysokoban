import pygame
from game.problem import SokobanProblem, SokobanAction
from game.map import Map
from ui.display import Display, Event, State
from ui.input_handler import InputHandler
from ai.ai import AI
import os

SOLUTION_DISPLAY_TIME = 5_000
class Game:

    def __init__(self):
        """
        Initializes the Game object.

        It sets the initial level number, loads the first level, display, and input handler objects.
        """
        self.lvl_num = -1
        self.input_handler = InputHandler()
        self.display = Display()
        self.running = True
        
    def _load_level(self, lvl_num: int) -> None:
        """
        Loads the specified level.

        Args:
            lvl_num (int): The level number to load.

        Returns:
            bool: True if the level is loaded successfully, False otherwise.
        """
        levels_folder = "levels"
        map = Map(os.path.join(levels_folder, f"level{lvl_num}.txt"))
        self.problem = SokobanProblem(map)
        self.map = self.problem.initial_state()

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
                    action = self.input_handler.handle_events()
                    if action == SokobanAction.PAUSE:
                        self.display.state = State.MAIN_MENU
                    elif action:
                        print(action.name)
                        self.map = self.problem.result(self.map, action)
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
                    problem = SokobanProblem(self.map)
                    ai = AI(problem)
                    solutions = ai.search()
                    if len(solutions) == 0:
                        print("Failed to find a solution.")
                    else:
                        for solution in solutions:
                            delay = SOLUTION_DISPLAY_TIME // len(solution)
                            print(solution)
                            for action in solution:
                                self.map = self.problem.result(self.map, action)
                                self.display.render()
                                pygame.time.wait(delay)
                    self.display.state = State.GAMING
                case _:
                    raise ValueError("Invalid event")
            clock.tick(60)