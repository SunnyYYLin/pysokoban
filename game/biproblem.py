from typing import TypeAlias, List, Generator, Tuple
from copy import copy
from functools import lru_cache
from sealgo.problem import BiSearchProblem, Action, State

from .map import Map
from .problem import SokobanAction, SokobanProblem, _action_dirs

class BiSokobanProblem(SokobanProblem, BiSearchProblem):
    def __init__(self, init_state: Map) -> None:
        super().__init__(init_state)
        self.init_boxes = init_state.locate_boxes()
        
    def __copy__(self) -> "BiSokobanProblem":
        return BiSokobanProblem(self.level)
    
    def goal_states(self, num: int = 10) -> List[Map]:
        """
        Returns the goal states of the problem.

        Returns:
        - The list of goal states of the problem.

        """
        return self.level.possible_goals(num)
    
    def actions_to(self, map: Map) -> List[SokobanAction]:
        """
        Returns the list of actions that can be executed to reach the given state.

        Args:
        - state (SokobanProblem.State): The state to get the actions for.

        Returns:
        - The list of actions that can be executed to reach the given state.
        
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
        last_map = copy(map)
        del map
        if action == Action.STAY:
            return last_map
        last_map.p_undo(_action_dirs[action[0]][0], _action_dirs[action[0]][1], pull=action[1])
        return last_map
    
    @lru_cache(maxsize=1_000_000)
    def re_heuristic(self, map: Map) -> int:
        boxes = map.locate_boxes()
        return self._min_perfect_matching(boxes, self.init_boxes) + self._player_to_start(map)
        
    def _player_to_start(self, map: Map) -> int:
        return abs(map.player_x - self.level.player_x) + abs(map.player_y - self.level.player_y)