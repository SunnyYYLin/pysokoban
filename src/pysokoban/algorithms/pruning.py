"""Domain Knowledge & Deadlock-Pruned Search (The 1990s Paradigm).

In 1997-2001, Junghanns & Schaeffer built 'Rolling Stone', the world-champion Sokoban solver.
Their key finding was that heuristic search without aggressive deadlock pruning is futile on Sokoban
because state space branches into irreversible dead ends.

This module implements Deadlock-Pruned A*, showing the staggering reduction in expanded nodes
when domain knowledge is applied.
"""

from __future__ import annotations

from typing import Optional

from pysokoban.algorithms.base import SearchAlgorithm, SearchResult
from pysokoban.algorithms.informed import AStar
from pysokoban.core.board import Board
from pysokoban.core.state import SokobanState
from pysokoban.heuristics.heuristics import (
    DeadlockAwareHeuristic,
    HungarianMatchingHeuristic,
    heuristic_manhattan,
)


class DeadlockPrunedAStar(SearchAlgorithm):
    """A* Search coupled with comprehensive Static and Dynamic Deadlock Detection.

    Prunes non-goal boxes in corners, precomputed static deadzones, and 2x2 frozen blocks.
    Demonstrates the 'Search vs Knowledge' principle from Junghanns & Schaeffer (AI Journal 2001).
    """

    def __init__(
        self,
        use_hungarian: bool = True,
        weight: float = 1.0,
        name: str = "Deadlock-Pruned A* (Rolling Stone style)",
    ):
        super().__init__(
            name=name,
            historical_year=1999,
            family="Domain-Pruned",
            optimality_guaranteed=(weight == 1.0),
            complete=True,
        )
        self.use_hungarian = use_hungarian
        self.weight = weight

    def solve(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 100_000,
        timeout_sec: float = 60.0,
    ) -> SearchResult:
        base_h = HungarianMatchingHeuristic(board) if self.use_hungarian else heuristic_manhattan
        deadlock_h = DeadlockAwareHeuristic(
            base_heuristic=base_h,
            use_static_deadlocks=True,
            use_freeze_deadlocks=True,
        )

        solver = AStar(
            heuristic=deadlock_h,
            weight=self.weight,
            name=self.name,
        )
        solver.historical_year = self.historical_year
        solver.family = self.family

        return solver.solve(board, initial_state, max_expansions, timeout_sec)
