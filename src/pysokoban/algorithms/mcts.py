"""Monte Carlo Tree Search (MCTS, Coulom 2006, Kocsis & Szepesvári 2006).

In 2006, MCTS revolutionized game search by replacing minimax/brute-force evaluation
with statistical rollouts and UCB1 (Upper Confidence Bounds applied to Trees).
This module applies Single-Agent MCTS to Sokoban puzzle solving.
"""

from __future__ import annotations

import math
import random
import time
from typing import Dict, List, Optional, Tuple

from pysokoban.algorithms.base import (
    SearchAlgorithm,
    SearchMetrics,
    SearchResult,
)
from pysokoban.core.board import Board
from pysokoban.core.enums import Action
from pysokoban.core.state import SokobanState
from pysokoban.heuristics.heuristics import heuristic_manhattan


class MCTSNode:
    """A node in the Monte Carlo search tree."""

    def __init__(
        self,
        state: SokobanState,
        parent: Optional[MCTSNode] = None,
        action: Optional[Action] = None,
        is_push: bool = False,
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.is_push = is_push
        self.children: Dict[Action, MCTSNode] = {}
        self.visits: int = 0
        self.total_reward: float = 0.0
        self.untried_actions: Optional[List[Tuple[Action, SokobanState, bool]]] = None

    def is_fully_expanded(self) -> bool:
        return self.untried_actions is not None and len(self.untried_actions) == 0

    def best_child(self, c_param: float = 1.414) -> MCTSNode:
        """Select child maximizing UCB1 formula."""
        best_score = -math.inf
        best = None
        for child in self.children.values():
            if child.visits == 0:
                return child
            # Single-agent reward: higher is better
            exploitation = child.total_reward / child.visits
            exploration = c_param * math.sqrt(math.log(self.visits) / child.visits)
            score = exploitation + exploration
            if score > best_score:
                best_score = score
                best = child
        assert best is not None
        return best


class MonteCarloTreeSearch(SearchAlgorithm):
    """Single-Agent Monte Carlo Tree Search (UCT)."""

    def __init__(
        self,
        c_param: float = 1.414,
        max_rollout_depth: int = 30,
        name: str = "Monte Carlo Tree Search (MCTS)",
    ):
        super().__init__(
            name=name,
            historical_year=2006,
            family="Sampling",
            optimality_guaranteed=False,
            complete=False,
        )
        self.c_param = c_param
        self.max_rollout_depth = max_rollout_depth

    def _rollout_reward(self, board: Board, state: SokobanState) -> float:
        """Simulate random rollout from state and compute normalized reward."""
        curr = state
        for _ in range(self.max_rollout_depth):
            if board.is_goal(curr):
                return 100.0
            actions = board.get_valid_actions(curr)
            if not actions:
                break
            _, curr, _ = random.choice(actions)

        # Terminal state: reward based on negative Manhattan distance
        dist = heuristic_manhattan(board, curr)
        return max(0.0, 50.0 - dist)

    def solve(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 50_000,
        timeout_sec: float = 30.0,
    ) -> SearchResult:
        start_time = time.perf_counter()
        init_state = initial_state or board.initial_state

        metrics = SearchMetrics(
            algorithm_name=self.name,
            historical_year=self.historical_year,
            family=self.family,
            optimality_guaranteed=self.optimality_guaranteed,
            complete=self.complete,
        )

        if board.is_goal(init_state):
            metrics.duration_sec = time.perf_counter() - start_time
            return SearchResult(solved=True, actions=[], states=[init_state], metrics=metrics)

        root = MCTSNode(state=init_state)
        root.untried_actions = board.get_valid_actions(init_state)

        goal_node: Optional[MCTSNode] = None

        while (
            time.perf_counter() - start_time < timeout_sec
            and metrics.expanded_nodes < max_expansions
        ):
            metrics.expanded_nodes += 1

            # 1. Selection
            curr = root
            while curr.is_fully_expanded() and curr.children:
                curr = curr.best_child(self.c_param)

            # 2. Expansion
            if curr.untried_actions:
                act, next_state, is_push = curr.untried_actions.pop()
                child = MCTSNode(state=next_state, parent=curr, action=act, is_push=is_push)
                child.untried_actions = board.get_valid_actions(next_state)
                curr.children[act] = child
                curr = child
                metrics.generated_nodes += 1

                if board.is_goal(next_state):
                    goal_node = child
                    break
            elif not curr.children:
                # Terminal node or dead-end
                pass

            # 3. Simulation / Rollout
            reward = self._rollout_reward(board, curr.state)

            # 4. Backpropagation
            b_node: Optional[MCTSNode] = curr
            while b_node is not None:
                b_node.visits += 1
                b_node.total_reward += reward
                b_node = b_node.parent

        metrics.duration_sec = time.perf_counter() - start_time

        if goal_node is not None:
            # Reconstruct path
            actions: List[Action] = []
            states: List[SokobanState] = []
            pushes = 0
            n: Optional[MCTSNode] = goal_node
            while n is not None:
                states.append(n.state)
                if n.action is not None:
                    actions.append(n.action)
                    if n.is_push:
                        pushes += 1
                n = n.parent

            actions.reverse()
            states.reverse()
            metrics.solution_steps = len(actions)
            metrics.solution_pushes = pushes

            return SearchResult(solved=True, actions=actions, states=states, metrics=metrics)

        return SearchResult.failure(metrics)
