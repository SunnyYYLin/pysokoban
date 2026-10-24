"""Base search algorithm protocols, diagnostic metrics, and search nodes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator, List, Optional, Set, Tuple

from pysokoban.core.board import Board
from pysokoban.core.enums import Action
from pysokoban.core.state import Coord, SokobanState


@dataclass(slots=True)
class SearchNode:
    """Node in the search tree."""

    state: SokobanState
    parent: Optional[SearchNode] = None
    action: Optional[Action] = None
    g: float = 0.0
    h: float = 0.0
    is_push: bool = False
    depth: int = 0

    @property
    def f(self) -> float:
        return self.g + self.h

    def __lt__(self, other: SearchNode) -> bool:
        if self.f != other.f:
            return self.f < other.f
        return self.g > other.g  # Tie-breaking: prefer deeper nodes


@dataclass
class SearchMetrics:
    """Diagnostic metrics representing the performance and complexity of a search execution."""

    algorithm_name: str = ""
    historical_year: int = 1950
    family: str = "Uninformed"
    generated_nodes: int = 0
    expanded_nodes: int = 0
    peak_frontier: int = 0
    duration_sec: float = 0.0
    solution_steps: int = 0
    solution_pushes: int = 0
    optimality_guaranteed: bool = False
    complete: bool = True
    notes: str = ""


@dataclass
class SearchResult:
    """The outcome of running a search algorithm on a board."""

    solved: bool
    actions: List[Action]
    states: List[SokobanState]
    metrics: SearchMetrics

    @classmethod
    def failure(cls, metrics: SearchMetrics) -> SearchResult:
        return cls(solved=False, actions=[], states=[], metrics=metrics)


@dataclass
class SearchStepEvent:
    """Snapshot yielded during search stepping (for UI and heatmap visualization)."""

    step_index: int
    current_state: SokobanState
    frontier_size: int
    closed_size: int
    explored_box_tiles: Set[Coord] = field(default_factory=set)


class SearchAlgorithm(ABC):
    """Abstract base class for all historical search algorithms."""

    def __init__(
        self,
        name: str,
        historical_year: int,
        family: str,
        optimality_guaranteed: bool = False,
        complete: bool = True,
    ):
        self.name = name
        self.historical_year = historical_year
        self.family = family
        self.optimality_guaranteed = optimality_guaranteed
        self.complete = complete

    @abstractmethod
    def solve(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 100_000,
        timeout_sec: float = 60.0,
    ) -> SearchResult:
        """Run the search to completion or until resource limits are reached."""
        pass

    def solve_steps(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 100_000,
        timeout_sec: float = 60.0,
        yield_interval: int = 20,
    ) -> Generator[SearchStepEvent, None, SearchResult]:
        """Generator variant of search that periodically yields intermediate state snapshots.

        Default implementation falls back to executing solve() and yielding start/end.
        """
        res = self.solve(board, initial_state, max_expansions, timeout_sec)
        init = initial_state or board.initial_state
        yield SearchStepEvent(
            step_index=res.metrics.expanded_nodes,
            current_state=res.states[-1] if res.states else init,
            frontier_size=res.metrics.peak_frontier,
            closed_size=res.metrics.expanded_nodes,
            explored_box_tiles=set(init.boxes),
        )
        return res

    @staticmethod
    def reconstruct_path(
        goal_node: SearchNode,
    ) -> Tuple[List[Action], List[SokobanState], int, int]:
        """Reconstruct the sequence of actions and states from initial node to goal node."""
        actions: List[Action] = []
        states: List[SokobanState] = []
        pushes = 0
        curr: Optional[SearchNode] = goal_node

        while curr is not None:
            states.append(curr.state)
            if curr.action is not None:
                actions.append(curr.action)
                if curr.is_push:
                    pushes += 1
            curr = curr.parent

        actions.reverse()
        states.reverse()
        return actions, states, len(actions), pushes
