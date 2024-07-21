import pygame
import os
import logging
from datetime import datetime
from ui.display import Display, State
from ui.input_handler import InputHandler, Event
from ai.ai import AI
from generation.mcts import mcts

from .problem import SokobanProblem, SokobanAction
from .map import Map, Tile

SOLUTION_DISPLAY_TIME = 5_000 # total time to display a solution of each level (ms)
MAX_LEVEL = 20 # maximum level number
# Mapping of key codes to Sokoban actions
key_actions = {
    pygame.K_UP: SokobanAction.UP,
    pygame.K_DOWN: SokobanAction.DOWN,
    pygame.K_LEFT: SokobanAction.LEFT,
    pygame.K_RIGHT: SokobanAction.RIGHT,
}
assets_path = "assets"

class Game:
    """
    Represents the Sokoban game.

    Attributes:
        lvl_num (int): The current level number.
        input_handler (InputHandler): The input handler object.
        display (Display): The display object.
        running (bool): Flag indicating if the game is running.
        map (Map): The game map object.

    Methods:
        run(self, start_level=1): Runs the game.
        test(self, end_lvl: int = 20): Runs a test on multiple levels.
    """

    def __init__(self, lvl_num: int = 0, icon_style: str = "image_v1"):
        """
        Initializes the Game object.

        It sets the initial level number, loads the first level, display, and input handler objects.

        Args:
            lvl_num (int): The initial level number. Default is 0.
            icon_style (str): The style of the game icons. Default is "image_v1".
        """
        self.lvl_num = lvl_num
        self.input_handler = InputHandler(key_actions)
        icon_paths = {
            Tile.GOALBOX: os.path.join(assets_path, icon_style, "goalbox.png"),
            Tile.GOALPLAYER: os.path.join(assets_path, icon_style, "goalplayer.png"),
            Tile.BOX: os.path.join(assets_path, icon_style, "box.png"),
            Tile.GOAL: os.path.join(assets_path, icon_style, "goal.png"),
            Tile.WALL: os.path.join(assets_path, icon_style, "wall.png"),
            Tile.PLAYER: os.path.join(assets_path, icon_style, "player.png"),
            Tile.SPACE: os.path.join(assets_path, icon_style, "space.png"),
        }
        self.display = Display(icon_paths)
        self.running = True
        self.map = Map()
        logging.info(f"Game initialized at {datetime.now()}")

    def _load_level(self, lvl_num: int) -> None:
        """
        Loads a level.

        Args:
            lvl_num (int): The level number to load.
        """
        levels_folder = "levels"
        map = Map(os.path.join(levels_folder, f"level{lvl_num}.txt"))
        self.problem = SokobanProblem(map)
        self.map = self.problem.initial_state()

    def run(self, start_level=1):
        """
        Runs the game.

        Args:
            start_level (int): The level number to start from. Default is 1.
        """
        clock = pygame.time.Clock()
        self.lvl_num = start_level - 1
        while self.running:
            self._handle_event()
            clock.tick(60)

    def test(self, end_lvl: int = 20):
        """
        Runs a test on multiple levels.

        Args:
            end_lvl (int): The last level number to test. Default is 20.
        """
        start_lvl = self.lvl_num
        for lvl_num in range(start_lvl, end_lvl + 1):
            self._load_level(lvl_num)
            problem = SokobanProblem(self.map)
            start_time = os.times()
            solutions = []
            while len(solutions) == 0:
                ai = AI(problem)
                solutions = ai.search()
            finish_time = os.times()
            elapsed_time = finish_time.elapsed - start_time.elapsed
            self.lvl_num += 1
            logging.info(f"Level {lvl_num}: Solution found in {elapsed_time:.2f} seconds.")
            logging.info(f"Solution length: {[len(solution) for solution in solutions]}")

    def _handle_event(self):
        """
        Handles game events.
        """
        text_rect, text_event = self.display.run(self.map, self.lvl_num)
        input = self.input_handler.handle_inputs(text_rect, text_event)
        match self.display.state:
            case State.START_MENU:
                self._handle_start_menu(input)
            case State.MAIN_MENU:
                self._handle_main_menu(input)
            case State.GAMING:
                self._handle_gaming(input)
            case State.VICTORY_MENU:
                self._handle_victory_menu(input)
            case _:
                raise ValueError(f"Invalid state: {self.display.state}")

    def _handle_start_menu(self, input: Event) -> None:
        """
        Handles start menu events.

        Args:
            input (Event): The event to handle.
        """
        match input:
            case Event.START:
                self._load_level(self.lvl_num)
                self.display.state = State.GAMING
            case Event.GENERATE:
                initialState = Generate_map(width=6,height=6)
                searcher = mcts(timeLimit=6000)
                bestaction = searcher.search(initialState=initialState)
            case Event.EXIT:
                pygame.quit()
                quit()

    def _handle_main_menu(self, input: Event) -> None:
        """
        Handles main menu events.

        Args:
            input (Event): The event to handle.
        """
        match input:
            case Event.CONTINUE:
                self.display.state = State.GAMING
            case Event.ASK_AI:
                ai = AI(self.problem)
                solutions = ai.search()
                if len(solutions) == 0:
                    logging.info(f"Failed to find a solution for {self.lvl_num}")
                    print("Failed to find a solution")
                    self.display.state = State.MAIN_MENU
                else:
                    while len(solutions) > 0:
                        self.map = self.problem.initial_state()
                        solution = solutions.pop(0)
                        delay = SOLUTION_DISPLAY_TIME // len(solution)
                        logging.info(f"Solution for Level{self.lvl_num}: {solution}")
                        for action in solution:
                            self.map = self.problem.result(self.map, action)
                            self.display.render(self.map)
                            pygame.time.wait(delay)
                    assert self.problem.is_goal(self.map), "Invalid solution"
                    self.display.state = State.VICTORY_MENU
            case Event.RESTART:
                self.map = self.problem.initial_state()
                self.display.state = State.GAMING
            case Event.EXIT:
                pygame.quit()
                quit()

    def _handle_gaming(self, input: SokobanAction) -> None:
        """
        Handles gaming events.

        Args:
            input (SokobanAction): The action to handle.
        """
        match input:
            case SokobanAction():
                self.map = self.problem.result(self.map, input)
                self.display.render(self.map)
                if self.problem.is_goal(self.map):
                    self.display.state = State.VICTORY_MENU
            case Event.PAUSE:
                self.display.state = State.MAIN_MENU
            case Event.EXIT:
                pygame.quit()
                quit()

    def _handle_victory_menu(self, input: Event) -> None:
        """
        Handles victory menu events.

        Args:
            input (Event): The event to handle.
        """
        match input:
            case Event.START:
                self.lvl_num += 1
                if self.lvl_num > MAX_LEVEL:
                    self.lvl_num = 1
                self._load_level(self.lvl_num)
                self.display.state = State.GAMING
            case Event.EXIT:
                pygame.quit()
                quit()
