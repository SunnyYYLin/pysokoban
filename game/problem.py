from enum import Enum, auto
from typing import TypeAlias, List
from functools import lru_cache
import numpy as np
from scipy.optimize import linear_sum_assignment
from sealgo.problem import HeuristicSearchProblem, Action

from .map import Map

class SokobanAction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    
_action_dirs:dict[int,tuple[int,int]] = {
    SokobanAction.UP: (-1, 0),
    SokobanAction.DOWN: (1, 0),
    SokobanAction.LEFT: (0, -1),
    SokobanAction.RIGHT: (0, 1),
}

class SokobanProblem(HeuristicSearchProblem):
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
    """

    State: TypeAlias = Map
    Action = SokobanAction
    
    def __init__(self, init_state: Map):
        """
        Initializes the SokobanProblem object with a level path.

        Args:
        - level_path: The path to the level file.

        """
        self.level = init_state
        
    def initial_state(self) -> State:
        """
        Returns the initial state of the problem.

        Returns:
        - The initial state of the problem.

        """
        return self.level.__copy__()
    
    def actions(self, map: State) -> List[Action]:
        """
        Returns the possible actions for a given state.

        Args:
        - map: The current state of the problem.

        Returns:
        - The possible actions for the given state.

        """
        actions = []
        for action, dir in _action_dirs.items():
            new_x = map.player_x + dir[0]
            new_y = map.player_y + dir[1]
            if map.is_wall(new_x, new_y):
                continue
            if map.is_box(new_x, new_y):
                if not map.can_push(new_x, new_y, dir[0], dir[1]):
                    continue
            actions.append(action)
        return actions
    
    def result(self, map: State, action: Action) -> State:
        """
        Returns the resulting state after taking an action.

        Args:
        - map: The current state of the problem.
        - action: The action to be taken.

        Returns:
        - The resulting state after taking the action.

        """
        new_map = map.__copy__()
        del map
        if action == Action.STAY:
            return new_map
        return new_map.p_move(_action_dirs[action][0], _action_dirs[action][1])
    
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
    
    @lru_cache(maxsize=1_000_000)
    def heuristic(self, map: State) -> int:
        """
        Returns the heuristic value of a given state.

        Args:
        - map: The state to be evaluated.

        Returns:
        - The heuristic value of the state.

        """
        boxes = map.locate_boxes()
        goals = map.locate_goals()
        return 3*self._min_perfect_matching(boxes, goals) + map.player_to_boxes(boxes) + self._deadlock_punishment(map, boxes)
    
    def _min_perfect_matching(self, boxes: np.ndarray, goals: np.ndarray) -> int:
        """
        Calculates the minimum perfect matching between the boxes and the goals.

        Args:
            boxes (np.ndarray): The boxes in the state.
            goals (np.ndarray): The goals in the state.

        Returns:
            int: The heuristic value.
        """
        cost_matrix = Map.cost_matrix(boxes, goals)
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        return cost_matrix[row_ind, col_ind].sum()
    
    def _deadlock_punishment(self, map: Map, boxes: np.ndarray) -> int:
        """
        Calculates the punishment for deadlocks.

        Args:
            state (Map): The current state of the Sokoban problem.

        Returns:
            int: The heuristic value.
        """
        return 50 if map.count_deadlock(boxes) else 0