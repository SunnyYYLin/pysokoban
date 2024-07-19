import pygame
from game.problem import SokobanProblem, SokobanAction
from game.map import Map
from ui.display import Display, Event, State
from ui.input_handler import InputHandler
from ai.ai import AI
import os
import logging
from datetime import datetime

SOLUTION_DISPLAY_TIME = 5_000
class Game:

    def __init__(self, lvl_num: int = 0):
        """
        Initializes the Game object.

        It sets the initial level number, loads the first level, display, and input handler objects.
        """
        self.lvl_num = lvl_num
        self.input_handler = InputHandler()
        self.display = Display()
        self.running = True
        self.map = Map()
        logging.info(f"Game initialized at {datetime.now()}")
        
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

    def run(self, start_level=1):
            """
            Runs the game loop.

            It handles player input, updates the player, renders the display,
            checks if the level is complete, and manages the game flow.
            """
            clock = pygame.time.Clock()
            self.lvl_num = start_level - 1
            while self.running:
                match self.display.run(self.map, self.lvl_num):
                    case Event.RUN:
                        action = self.input_handler.handle_events()
                        if action == SokobanAction.PAUSE:
                            self.display.state = State.MAIN_MENU
                        elif action:
                            logging.info(f"Action: {action.name}")
                            self.map = self.problem.result(self.map, action)
                            self.display.state = State.GAMING
                        if self.problem.is_goal(self.map):
                            self.display.state = State.VICTORY_MENU
                    case Event.CONTINUE:
                        self.display.state = State.GAMING
                    case Event.EXIT:
                        logging.info(f"Exited the game at {datetime.now()}")
                        pygame.quit()
                        quit()
                    case Event.START:
                        self.lvl_num += 1
                        try:
                            self._load_level(self.lvl_num)
                            self.display.state = State.GAMING
                        except:
                            logging.info("No more levels to load.")
                            self.lvl_num = 0
                            self.display.state = State.START_MENU
                    case Event.RESTART:
                        self.map = self.problem.initial_state()
                        self.display.state = State.GAMING
                    case Event.ASK_AI:
                        problem = SokobanProblem(self.map)
                        ai = AI(problem)
                        solutions = ai.search()
                        if len(solutions) == 0:
                            logging.info(f"Failed to find a solution for {self.lvl_num}")
                        else:
                            for solution in solutions:
                                delay = SOLUTION_DISPLAY_TIME // len(solution)
                                logging.info(f"Solution for Level{self.lvl_num}: {solution}")
                                for action in solution:
                                    self.map = self.problem.result(self.map, action)
                                    self.display.render(self.map)
                                    pygame.time.wait(delay)
                        self.display.state = State.GAMING
                    case _:
                        raise ValueError("Invalid event")
                clock.tick(60)
            
    def test(self, end_lvl: int = 20):
        start_lvl = self.lvl_num
        for lvl_num in range(start_lvl, end_lvl):
            self.lvl_num += 1
            self._load_level(lvl_num)
            problem = SokobanProblem(self.map)
            start_time = os.times()
            solutions = []
            while len(solutions) == 0:
                ai = AI(problem)
                solutions = ai.search()
            finish_time = os.times()
            elapsed_time = finish_time.elapsed - start_time.elapsed  
            logging.info(f"Level {lvl_num}: Solution found in {elapsed_time:.2f} seconds.")
            logging.info(f"Solution length: {[len(solution) for solution in solutions]}")
            