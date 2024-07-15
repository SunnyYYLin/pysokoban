from game.map import Map
from game.map import SPACE, GOALBOX, BOX, GOAL, GOALPLAYER, PLAYER
import pygame
from enum import Enum
from sealgo.sealgo_pkg.Problem import SearchProblem, State, Action
from os import path
from typing import TypeAlias

DIRECTIONS:dict[int,tuple[int,int]] = \
    {pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1), pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0)}

class SokobanAction(Enum):
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    LEFT = pygame.K_LEFT
    RIGHT = pygame.K_RIGHT

class SokobanProblem(SearchProblem):
    """
    Represents a Sokoban problem.

    Attributes:
    - State: The state of the problem, represented by a Map object.
    - Action: The possible actions that can be taken, represented by an enumeration.
    - level: The level of the problem, represented by a Map object.

    Methods:
    - __init__(self, level_path: path): Initializes the SokobanProblem object with a level path.
    - initial_state(self): Returns the initial state of the problem.
    - actions(self, map: State): Returns the possible actions for a given state.
    - result(self, map: State, action: Action) -> State: Returns the resulting state after taking an action.
    - is_goal(self, map: State): Checks if the given state is a goal state.
    - step_cost(self, map: State, action: Action): Returns the cost of taking an action in a given state.
    - _move(self, dx: int, dy: int, map: Map): Moves the player in a given direction.
    - _push(self, x: int, y: int, dx: int, dy: int, map: Map) -> bool: Pushes a box in a given direction.

    """

    State: TypeAlias = Map
    Action = SokobanAction
    
    def __init__(self, level_file: str):
        """
        Initializes the SokobanProblem object with a level path.

        Args:
        - level_path: The path to the level file.

        """
        self.level = Map(level_file)
        
    def initial_state(self) -> State:
        """
        Returns the initial state of the problem.

        Returns:
        - The initial state of the problem.

        """
        return self.level.__copy__()
    
    def actions(self, map: State):
        """
        Returns the possible actions for a given state.

        Args:
        - map: The current state of the problem.

        Returns:
        - The possible actions for the given state.

        """
        for action, dir in DIRECTIONS:
            new_x = map.player_x + dir[0]
            new_y = map.player_y + dir[1]
            if map.is_wall(new_x, new_y):
                continue
            if map.is_box(new_x, new_y):
                if map.is_wall(new_x + dir[0], new_y + dir[1]) or map.is_box(new_x + dir[0], new_y + dir[1]):
                    continue
            yield action
    
    def result(self, map: State, action: Action) -> State:
        """
        Returns the resulting state after taking an action.

        Args:
        - map: The current state of the problem.
        - action: The action to be taken.

        Returns:
        - The resulting state after taking the action.

        """
        match action:
            case self.Action.UP:
                return map.p_move(0, -1)
            case self.Action.DOWN:
                return map.p_move(0, 1)
            case self.Action.LEFT:
                return map.p_move(-1, 0)
            case self.Action.RIGHT:
                return map.p_move(1, 0)
            case _:
                return map
        
    def is_goal(self, map: State):
        """
        Checks if the given state is a goal state.

        Args:
        - map: The state to be checked.

        Returns:
        - True if the state is a goal state, False otherwise.

        """
        return map.is_all_boxes_in_place()
    
    def step_cost(self, map: State, action: Action):
        """
        Returns the cost of taking an action in a given state.

        Args:
        - map: The current state of the problem.
        - action: The action to be taken.

        Returns:
        - The cost of taking the action.

        """
        return 1
    
    def exists_dead_boxes(self, map: State) -> bool:
        """
        Checks if there are any dead boxes in the given state.

        Args:
        - map: The state to be checked.

        Returns:
        - True if there are dead boxes, False otherwise.

        """
        for x in range(map.width):
            for y in range(map.height):
                if map.is_box(x, y):
                    if map.is_goal(x, y):
                        continue
                    if map.is_wall(x - 1, y) and (map.is_wall(x, y - 1) or map.is_wall(x, y + 1)):
                        return True
                    if map.is_wall(x + 1, y) and (map.is_wall(x, y - 1) or map.is_wall(x, y + 1)):
                        return True
        return False