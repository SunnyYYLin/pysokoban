"""Uninformed (blind) search algorithms from the classical AI era (1950s - 1980s).

Algorithms:
1. Breadth-First Search (BFS, Moore 1959): Optimal for unit-cost step problems, but
   suffers catastrophic exponential memory explosion O(b^d).
2. Depth-First Search (DFS): Explores deep branches; non-optimal, risks infinite paths.
3. Uniform Cost Search (UCS, Dijkstra 1959): Priority queue ordered strictly by path cost g(n).
4. Iterative Deepening Search (IDS, Korf 1985): Combines BFS's optimality with DFS's O(bd) linear space.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Generator, List, Optional, Set

from pysokoban.algorithms.base import (
    SearchAlgorithm,
    SearchMetrics,
    SearchNode,
    SearchResult,
    SearchStepEvent,
)
from pysokoban.core.board import Board
from pysokoban.core.state import Coord, SokobanState


class BreadthFirstSearch(SearchAlgorithm):
    """Breadth-First Search (Moore, 1959).

    Explores shallowest unexpanded nodes first using a FIFO queue.
    Guarantees the shortest step sequence for Sokoban, but state space explodes rapidly.
    """

    def __init__(self):
        super().__init__(
            name="Breadth-First Search (BFS)",
            historical_year=1959,
            family="Uninformed",
            optimality_guaranteed=True,
            complete=True,
        )

    def solve(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 100_000,
        timeout_sec: float = 60.0,
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

        root = SearchNode(state=init_state, depth=0)
        frontier: deque[SearchNode] = deque([root])
        visited: Set[SokobanState] = {init_state}

        metrics.generated_nodes = 1
        metrics.peak_frontier = 1

        while frontier:
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions limit ({max_expansions}) exceeded"
                break

            node = frontier.popleft()
            metrics.expanded_nodes += 1

            for action, next_state, is_push in board.get_valid_actions(node.state):
                if next_state not in visited:
                    child = SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=node.g + 1,
                        is_push=is_push,
                        depth=node.depth + 1,
                    )
                    metrics.generated_nodes += 1

                    if board.is_goal(next_state):
                        metrics.duration_sec = time.perf_counter() - start_time
                        actions, states, steps, pushes = self.reconstruct_path(child)
                        metrics.solution_steps = steps
                        metrics.solution_pushes = pushes
                        return SearchResult(
                            solved=True,
                            actions=actions,
                            states=states,
                            metrics=metrics,
                        )

                    visited.add(next_state)
                    frontier.append(child)

            metrics.peak_frontier = max(metrics.peak_frontier, len(frontier))

        metrics.duration_sec = time.perf_counter() - start_time
        return SearchResult.failure(metrics)

    def solve_steps(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 100_000,
        timeout_sec: float = 60.0,
        yield_interval: int = 50,
    ) -> Generator[SearchStepEvent, None, SearchResult]:
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
            res = SearchResult(solved=True, actions=[], states=[init_state], metrics=metrics)
            yield SearchStepEvent(0, init_state, 1, 1, set(init_state.boxes))
            return res

        root = SearchNode(state=init_state, depth=0)
        frontier: deque[SearchNode] = deque([root])
        visited: Set[SokobanState] = {init_state}
        explored_boxes: Set[Coord] = set(init_state.boxes)

        metrics.generated_nodes = 1
        metrics.peak_frontier = 1

        while frontier:
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions limit ({max_expansions}) exceeded"
                break

            node = frontier.popleft()
            metrics.expanded_nodes += 1
            explored_boxes.update(node.state.boxes)

            if metrics.expanded_nodes % yield_interval == 0:
                yield SearchStepEvent(
                    step_index=metrics.expanded_nodes,
                    current_state=node.state,
                    frontier_size=len(frontier),
                    closed_size=len(visited),
                    explored_box_tiles=set(explored_boxes),
                )

            for action, next_state, is_push in board.get_valid_actions(node.state):
                if next_state not in visited:
                    child = SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=node.g + 1,
                        is_push=is_push,
                        depth=node.depth + 1,
                    )
                    metrics.generated_nodes += 1

                    if board.is_goal(next_state):
                        metrics.duration_sec = time.perf_counter() - start_time
                        actions, states, steps, pushes = self.reconstruct_path(child)
                        metrics.solution_steps = steps
                        metrics.solution_pushes = pushes
                        res = SearchResult(
                            solved=True,
                            actions=actions,
                            states=states,
                            metrics=metrics,
                        )
                        yield SearchStepEvent(
                            step_index=metrics.expanded_nodes,
                            current_state=next_state,
                            frontier_size=len(frontier),
                            closed_size=len(visited),
                            explored_box_tiles=set(explored_boxes),
                        )
                        return res

                    visited.add(next_state)
                    frontier.append(child)

            metrics.peak_frontier = max(metrics.peak_frontier, len(frontier))

        metrics.duration_sec = time.perf_counter() - start_time
        return SearchResult.failure(metrics)


class DepthFirstSearch(SearchAlgorithm):
    """Depth-First Search (DFS).

    Explores deepest nodes first using a LIFO stack. Non-optimal.
    """

    def __init__(self, max_depth: int = 1_000):
        super().__init__(
            name="Depth-First Search (DFS)",
            historical_year=1950,
            family="Uninformed",
            optimality_guaranteed=False,
            complete=False,
        )
        self.max_depth = max_depth

    def solve(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 100_000,
        timeout_sec: float = 60.0,
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

        root = SearchNode(state=init_state, depth=0)
        stack: List[SearchNode] = [root]
        visited: Set[SokobanState] = {init_state}

        metrics.generated_nodes = 1
        metrics.peak_frontier = 1

        while stack:
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions ({max_expansions}) exceeded"
                break

            node = stack.pop()
            metrics.expanded_nodes += 1

            if board.is_goal(node.state):
                metrics.duration_sec = time.perf_counter() - start_time
                actions, states, steps, pushes = self.reconstruct_path(node)
                metrics.solution_steps = steps
                metrics.solution_pushes = pushes
                return SearchResult(solved=True, actions=actions, states=states, metrics=metrics)

            if node.depth < self.max_depth:
                for action, next_state, is_push in board.get_valid_actions(node.state):
                    if next_state not in visited:
                        visited.add(next_state)
                        child = SearchNode(
                            state=next_state,
                            parent=node,
                            action=action,
                            g=node.g + 1,
                            is_push=is_push,
                            depth=node.depth + 1,
                        )
                        stack.append(child)
                        metrics.generated_nodes += 1

            metrics.peak_frontier = max(metrics.peak_frontier, len(stack))

        metrics.duration_sec = time.perf_counter() - start_time
        return SearchResult.failure(metrics)


class IterativeDeepeningSearch(SearchAlgorithm):
    """Iterative Deepening Search (IDS, Korf 1985).

    Repeatedly runs depth-limited search with increasing depth thresholds.
    Optimal like BFS, but memory consumption is bounded by O(bd).
    """

    def __init__(self, step_size: int = 1, max_depth_limit: int = 50):
        super().__init__(
            name="Iterative Deepening Search (IDS)",
            historical_year=1985,
            family="Uninformed",
            optimality_guaranteed=True,
            complete=True,
        )
        self.step_size = step_size
        self.max_depth_limit = max_depth_limit

    def solve(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 100_000,
        timeout_sec: float = 60.0,
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

        for limit in range(1, self.max_depth_limit + 1, self.step_size):
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions ({max_expansions}) exceeded"
                break

            # Depth-limited search with loop prevention on current path
            root = SearchNode(state=init_state, depth=0)
            stack: List[SearchNode] = [root]
            path_set: Set[SokobanState] = {init_state}

            while stack:
                if time.perf_counter() - start_time > timeout_sec:
                    break
                if metrics.expanded_nodes >= max_expansions:
                    break

                node = stack.pop()
                metrics.expanded_nodes += 1

                if board.is_goal(node.state):
                    metrics.duration_sec = time.perf_counter() - start_time
                    actions, states, steps, pushes = self.reconstruct_path(node)
                    metrics.solution_steps = steps
                    metrics.solution_pushes = pushes
                    return SearchResult(
                        solved=True, actions=actions, states=states, metrics=metrics
                    )

                if node.depth < limit:
                    for action, next_state, is_push in board.get_valid_actions(node.state):
                        if next_state not in path_set:
                            path_set.add(next_state)
                            child = SearchNode(
                                state=next_state,
                                parent=node,
                                action=action,
                                g=node.g + 1,
                                is_push=is_push,
                                depth=node.depth + 1,
                            )
                            stack.append(child)
                            metrics.generated_nodes += 1

                metrics.peak_frontier = max(metrics.peak_frontier, len(stack))

        metrics.duration_sec = time.perf_counter() - start_time
        return SearchResult.failure(metrics)
