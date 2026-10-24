"""Heuristic functions for informed search in Sokoban.

In AI history, Hart, Nilsson & Raphael (1968) introduced the A* algorithm, establishing
the principle that an admissible heuristic (one that never overestimates the true remaining cost)
guarantees optimal solutions.

For Sokoban:
1. Manhattan Distance (Sum of Min): Fast admissible baseline.
2. Hungarian Matching (Minimum Weight Bipartite Matching): Solves optimal 1-to-1 pairing
   between boxes and goals via Kuhn-Munkres (Scipy linear_sum_assignment), yielding
   a strictly tighter admissible bound.
3. Deadlock-Aware Heuristic: Adds infinite penalty to states identified as irreversible deadlocks.
"""

from __future__ import annotations

import math
from typing import Callable, List

import numpy as np
from scipy.optimize import linear_sum_assignment

from pysokoban.core.board import Board
from pysokoban.core.deadlock import is_state_deadlocked
from pysokoban.core.state import Coord, SokobanState

HeuristicFunc = Callable[[Board, SokobanState], float]


def manhattan_distance(p1: Coord, p2: Coord) -> int:
    """Compute L1 Manhattan distance between two coordinates."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def heuristic_manhattan(board: Board, state: SokobanState) -> float:
    """Sum of minimum Manhattan distances from each box to its nearest goal.

    Admissible and O(N_boxes * N_goals).
    """
    if board.is_goal(state):
        return 0.0

    total_dist = 0
    for box in state.boxes:
        min_d = min(manhattan_distance(box, goal) for goal in board.goals)
        total_dist += min_d

    return float(total_dist)


class HungarianMatchingHeuristic:
    """Computes minimum-cost perfect bipartite matching between boxes and goals.

    Since every goal must receive exactly one distinct box, solving the assignment problem
    via the Kuhn-Munkres algorithm produces a tighter lower bound than naive sum of minimums.
    """

    def __init__(self, board: Board):
        self.goals_list: List[Coord] = list(board.goals)
        self.num_goals = len(self.goals_list)

    def __call__(self, board: Board, state: SokobanState) -> float:
        if board.is_goal(state):
            return 0.0

        boxes_list = list(state.boxes)
        n_boxes = len(boxes_list)
        if n_boxes == 0 or self.num_goals == 0:
            return 0.0

        # Construct cost matrix
        cost_matrix = np.zeros((n_boxes, self.num_goals), dtype=np.int32)
        for i, box in enumerate(boxes_list):
            for j, goal in enumerate(self.goals_list):
                cost_matrix[i, j] = manhattan_distance(box, goal)

        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        total_cost = cost_matrix[row_ind, col_ind].sum()
        return float(total_cost)


class DeadlockAwareHeuristic:
    """Wraps an underlying admissible heuristic and adds static/dynamic deadlock pruning."""

    def __init__(
        self,
        base_heuristic: HeuristicFunc,
        use_static_deadlocks: bool = True,
        use_freeze_deadlocks: bool = True,
    ):
        self.base_heuristic = base_heuristic
        self.use_static = use_static_deadlocks
        self.use_freeze = use_freeze_deadlocks

    def __call__(self, board: Board, state: SokobanState) -> float:
        static_set = board.static_deadlocks if self.use_static else None
        if is_state_deadlocked(
            board, state, static_deadlocks=static_set, check_freeze=self.use_freeze
        ):
            return math.inf

        return self.base_heuristic(board, state)
