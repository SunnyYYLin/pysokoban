from typing import List, Type
from queue import PriorityQueue
from copy import copy
import os

from .problem import SearchProblem, HeuristicSearchProblem, BiSearchProblem, Action, State
from .search import Search
from .best_first_search import BestFirstSearch, AStar

# TEST
# from ui.display import Display
# from game.map import Tile
# assets_path = "assets"
# icon_style = "images_v1"
# icon_paths = {
#         Tile.GOALBOX: os.path.join(assets_path, icon_style, "goalbox.png"),
#         Tile.GOALPLAYER: os.path.join(assets_path, icon_style, "goalplayer.png"),
#         Tile.BOX: os.path.join(assets_path, icon_style, "box.png"),
#         Tile.GOAL: os.path.join(assets_path, icon_style, "goal.png"),
#         Tile.WALL: os.path.join(assets_path, icon_style, "wall.png"),
#         Tile.PLAYER: os.path.join(assets_path, icon_style, "player.png"),
#         Tile.SPACE: os.path.join(assets_path, icon_style, "space.png"),
#     }
# d = Display(icon_paths)

class BiDirectional(Search):
    """
    BiDirectional class represents a bidirectional search algorithm.

    Args:
        problem (BiSearchProblem): The bidirectional search problem.
        f_algo (Type[BestFirstSearch]): The forward search algorithm.
        b_algo (Type[BestFirstSearch]|None, optional): The backward search algorithm. Defaults to None.
        b_weight (int, optional): The the proportion of backwards to forwards, at least 1. Defaults to 1.
        *args: Additional arguments to be passed to the search algorithms.
        **kwargs: Additional keyword arguments to be passed to the search algorithms.

    Attributes:
        f_algo (BestFirstSearch): The forward search algorithm.
        b_algo (BestFirstSearch): The backward search algorithm.
        b_weight (int): The weight of the backward search.

    Methods:
        search(): Perform the bidirectional search and return the path from the initial state to the goal state.
        _init_problem(problem: BiSearchProblem): Initialize the forward and backward search problems.
        _reconstruct_path(inter_state: State): Reconstruct the path from the initial state to the goal state.

    """

    def __init__(self, problem: BiSearchProblem, f_algo: Type[BestFirstSearch], b_algo: Type[BestFirstSearch]|None = None, b_weight: int = 1, *args, **kwargs) -> None:
        self._init_problem(problem)
        if b_algo is None:
            b_algo = f_algo
        if args or kwargs:
            self.f_algo = f_algo(self.f_problem, *args, **kwargs)
            self.b_algo = b_algo(self.b_problem, *args, **kwargs)
        else:
            self.f_algo = f_algo(self.f_problem)
            self.b_algo = b_algo(self.b_problem)
        self.b_weight = b_weight
        
    def search(self) -> List[List[Action]]:
        """
        Perform the bidirectional search and return the path from the initial state to the goal state.

        Returns:
            List[List[Action]]: The path from the initial state to the goal state.

        """
        b_times = 0
        while not self.f_algo.frontier.empty() and not self.b_algo.frontier.empty():
            if b_times >= self.b_weight:
                b_times = 0
                # forward search
                f_state = self.f_algo.frontier.get()[1]
                self.f_algo._extend(f_state)
            # backward search
            b_state = self.b_algo.frontier.get()[1]
            if b_state in self.f_algo.predecessors:
                return [self._reconstruct_path(b_state)]
            self.b_algo._extend(b_state)
            b_times += 1
        return []

    def _init_problem(self, problem: BiSearchProblem) -> None:
        """
        Initialize the forward and backward search problems.

        Args:
            problem (BiSearchProblem): The bidirectional search problem.

        """
        f_problem = copy(problem)
        b_problem = copy(problem)
        f_problem.initial_state = problem.initial_state
        b_problem.initial_state = problem.goal_states
        f_problem.is_goal = problem.is_goal
        b_problem.is_goal = problem.is_goal
        f_problem.actions = problem.actions
        b_problem.actions = problem.actions_to
        f_problem.result = problem.result
        b_problem.result = problem.reason
        f_problem.action_cost = problem.action_cost
        b_problem.action_cost = problem.action_cost
        if hasattr(problem, "heuristic"):
            f_problem.heuristic = problem.heuristic
        if hasattr(problem, "re_heuristic"):
            b_problem.heuristic = problem.re_heuristic
        self.f_problem = f_problem
        self.b_problem = b_problem
    
    def _reconstruct_path(self, inter_state: State) -> List[Action]:
        """
        Reconstruct the path from the initial state to the goal state.

        Args:
            inter_state (State): The intermediate state where the forward and backward paths meet.

        Returns:
            List[Action]: The path from the initial state to the goal state.

        """
        f_solution = []
        f_state = inter_state
        while self.f_algo.predecessors[f_state][0] is not None:
            # d.render(f_state)
            f_solution.append(self.f_algo.predecessors[f_state][1])
            f_state = self.f_algo.predecessors[f_state][0]
        f_solution.reverse()
        
        b_solution = []
        b_state = inter_state
        while self.b_algo.predecessors[b_state][0] is not None:
            # d.render(b_state)
            b_solution.append(self.b_algo.predecessors[b_state][1][0])
            b_state = self.b_algo.predecessors[b_state][0]
        
        return f_solution + b_solution