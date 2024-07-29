from typing import TypeAlias, List, Generator, Tuple
from copy import copy
from functools import lru_cache
from sealgo.problem import BiSearchProblem, Action, State

from .map import Map
from .problem import SokobanAction, SokobanProblem, _action_dirs

class BiSokobanProblem(SokobanProblem, BiSearchProblem):
    """
    Represents a bi-directional Sokoban problem.

    Inherits from SokobanProblem and BiSearchProblem.

    Attributes:
        init_state (Map): The initial state of the problem.
        init_boxes (List[Tuple[int, int]]): The initial positions of the boxes.

    Methods:
        __init__(self, init_state: Map) -> None: Initializes the BiSokobanProblem object.
        __copy__(self) -> "BiSokobanProblem": Creates a copy of the BiSokobanProblem object.
        goal_states(self, num: int = 10) -> List[Map]: Returns a list of possible goal states.
        actions_to(self, map: Map) -> List[SokobanAction]: Returns a list of actions that can be taken to reach a given map state.
        reason(self, map: Map, action: Tuple[SokobanAction, bool]|Action) -> Map: Returns the resulting map after taking a given action.
        re_heuristic(self, map: Map) -> int: Returns the heuristic value for a given map state.
        _player_to_start(self, map: Map) -> int: Returns the distance between the player and the starting position.
    """
    def __init__(self, init_state: Map) -> None:
        super().__init__(init_state)
        self.init_boxes = init_state.locate_boxes()
        
    def __copy__(self) -> "BiSokobanProblem":
        return BiSokobanProblem(self.level)
    
    def goal_states(self, num: int = 10) -> List[Map]:
        """
        Returns a list of possible goal states for the problem.

        Args:
            num (int): The number of goal states to return. Defaults to 10.

        Returns:
            List[Map]: A list of possible goal states.
        """
        return self.level.possible_goals(num)
    
    def actions_to(self, map: Map) -> List[SokobanAction]:
        """
        Generates a list of possible Sokoban actions that can reach the current map state.

        Args:
            map (Map): The current Sokoban map.

        Returns:
            List[SokobanAction]: A list of possible Sokoban actions, where each action is a tuple
            containing the action name and a boolean indicating whether it involves pulling a box.
        """
        actions = []
        for action, dir in _action_dirs.items():
            last_x, last_y = map.player_x - dir[0], map.player_y - dir[1]
            if map.is_blocked(last_x, last_y):
                continue
            actions.append((action, False))
            if map.can_pull(map.player_x+dir[0], map.player_y+dir[1], -dir[0], -dir[1]):
                actions.append((action, True))
        return actions
    
    def reason(self, map: Map, action: Tuple[SokobanAction, bool]|Action) -> Map:
        """
        Returns the previous map before taking a given action to reach the current map state.
        
        Args:
            map (Map): The current Sokoban map.
            action (Tuple[SokobanAction, bool]|Action): The action to undo.
        
        Returns:
            Map: The previous Sokoban map.
        """
        last_map = copy(map)
        del map
        if action == Action.STAY:
            return last_map
        last_map.p_undo(_action_dirs[action[0]][0], _action_dirs[action[0]][1], pull=action[1])
        return last_map
    
    @lru_cache(maxsize=1_000_000)
    def re_heuristic(self, map: Map) -> int:
        """
        Calculates the backwards heuristic value for the given map.

        Args:
            map (Map): The map object representing the current state.

        Returns:
            int: The backwards heuristic value.

        """
        boxes = map.locate_boxes()
        return self._min_perfect_matching(boxes, self.init_boxes) + self._player_to_start(map)
        
    def _player_to_start(self, map: Map) -> int:
        return abs(map.player_x - self.level.player_x) + abs(map.player_y - self.level.player_y)