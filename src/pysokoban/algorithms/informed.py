"""Informed (heuristic) search algorithms from the golden era of AI (1960s - 1980s).

Algorithms:
1. Greedy Best-First Search (GBFS): Guided strictly by heuristic h(n). Fast but suboptimal.
2. A* Search (Hart, Nilsson, Raphael 1968): Combines actual cost g(n) and admissible heuristic h(n).
3. Weighted A* (WA*, Pohl 1970): Scales heuristic weight w > 1 to trade optimality for speed.
4. Iterative Deepening A* (IDA*, Korf 1985): Memory-bounded A* using f-value thresholds.
"""

from __future__ import annotations

import heapq
import itertools
import math
import time
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
from pysokoban.heuristics.heuristics import HeuristicFunc, heuristic_manhattan


class AStar(SearchAlgorithm):
    """A* Search Algorithm (Hart, Nilsson, Raphael 1968).

    Expands nodes in order of estimated total cost f(n) = g(n) + w * h(n).
    If w = 1 and h is admissible, A* guarantees the optimal solution.
    If w > 1, it becomes Weighted A* (Pohl 1970), bounded epsilon-admissible.
    """

    def __init__(
        self,
        heuristic: Optional[HeuristicFunc] = None,
        weight: float = 1.0,
        name: Optional[str] = None,
    ):
        self.heuristic = heuristic or heuristic_manhattan
        self.weight = weight
        disp_name = name if name else (f"A* (weight={weight})" if weight != 1.0 else "A* Search")
        super().__init__(
            name=disp_name,
            historical_year=1968 if weight == 1.0 else 1970,
            family="Informed",
            optimality_guaranteed=(weight == 1.0),
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

        counter = itertools.count()
        init_h = self.heuristic(board, init_state)
        root = SearchNode(state=init_state, g=0.0, h=init_h, depth=0)

        # Priority queue entries: (f, -g, counter, node)
        frontier: List[tuple[float, float, int, SearchNode]] = [
            (root.g + self.weight * root.h, -root.g, next(counter), root)
        ]
        # Track best g-cost seen for each state
        best_g: dict[SokobanState, float] = {init_state: 0.0}
        explored_boxes: Set[Coord] = set(init_state.boxes)

        metrics.generated_nodes = 1
        metrics.peak_frontier = 1

        while frontier:
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions ({max_expansions}) exceeded"
                break

            f_val, neg_g, _, node = heapq.heappop(frontier)
            curr_state = node.state

            # If we found a strictly better path to this state already, skip
            if node.g > best_g.get(curr_state, math.inf):
                continue

            metrics.expanded_nodes += 1
            explored_boxes.update(curr_state.boxes)

            if board.is_goal(curr_state):
                metrics.duration_sec = time.perf_counter() - start_time
                actions, states, steps, pushes = self.reconstruct_path(node)
                metrics.solution_steps = steps
                metrics.solution_pushes = pushes
                return SearchResult(
                    solved=True,
                    actions=actions,
                    states=states,
                    metrics=metrics,
                    explored_tiles=explored_boxes,
                )

            for action, next_state, is_push in board.get_valid_actions(curr_state):
                step_cost = 1.0  # Unit cost
                new_g = node.g + step_cost

                if new_g < best_g.get(next_state, math.inf):
                    h_val = self.heuristic(board, next_state)
                    if math.isinf(h_val):
                        # Pruned by deadlock heuristic
                        continue

                    best_g[next_state] = new_g
                    child = SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=new_g,
                        h=h_val,
                        is_push=is_push,
                        depth=node.depth + 1,
                    )
                    metrics.generated_nodes += 1
                    f_child = child.g + self.weight * child.h
                    heapq.heappush(frontier, (f_child, -child.g, next(counter), child))

            metrics.peak_frontier = max(metrics.peak_frontier, len(frontier))

        metrics.duration_sec = time.perf_counter() - start_time
        return SearchResult.failure(metrics, explored_tiles=explored_boxes)

    def solve_steps(
        self,
        board: Board,
        initial_state: Optional[SokobanState] = None,
        max_expansions: int = 100_000,
        timeout_sec: float = 60.0,
        yield_interval: int = 20,
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

        counter = itertools.count()
        init_h = self.heuristic(board, init_state)
        root = SearchNode(state=init_state, g=0.0, h=init_h, depth=0)
        frontier: List[tuple[float, float, int, SearchNode]] = [
            (root.g + self.weight * root.h, -root.g, next(counter), root)
        ]
        best_g: dict[SokobanState, float] = {init_state: 0.0}
        explored_boxes: Set[Coord] = set(init_state.boxes)

        metrics.generated_nodes = 1
        metrics.peak_frontier = 1

        while frontier:
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions ({max_expansions}) exceeded"
                break

            f_val, neg_g, _, node = heapq.heappop(frontier)
            curr_state = node.state

            if node.g > best_g.get(curr_state, math.inf):
                continue

            metrics.expanded_nodes += 1
            explored_boxes.update(curr_state.boxes)

            if metrics.expanded_nodes % yield_interval == 0:
                yield SearchStepEvent(
                    step_index=metrics.expanded_nodes,
                    current_state=curr_state,
                    frontier_size=len(frontier),
                    closed_size=len(best_g),
                    explored_box_tiles=set(explored_boxes),
                )

            if board.is_goal(curr_state):
                metrics.duration_sec = time.perf_counter() - start_time
                actions, states, steps, pushes = self.reconstruct_path(node)
                metrics.solution_steps = steps
                metrics.solution_pushes = pushes
                res = SearchResult(solved=True, actions=actions, states=states, metrics=metrics)
                yield SearchStepEvent(
                    step_index=metrics.expanded_nodes,
                    current_state=curr_state,
                    frontier_size=len(frontier),
                    closed_size=len(best_g),
                    explored_box_tiles=set(explored_boxes),
                )
                return res

            for action, next_state, is_push in board.get_valid_actions(curr_state):
                new_g = node.g + 1.0

                if new_g < best_g.get(next_state, math.inf):
                    h_val = self.heuristic(board, next_state)
                    if math.isinf(h_val):
                        continue

                    best_g[next_state] = new_g
                    child = SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=new_g,
                        h=h_val,
                        is_push=is_push,
                        depth=node.depth + 1,
                    )
                    metrics.generated_nodes += 1
                    f_child = child.g + self.weight * child.h
                    heapq.heappush(frontier, (f_child, -child.g, next(counter), child))

            metrics.peak_frontier = max(metrics.peak_frontier, len(frontier))

        metrics.duration_sec = time.perf_counter() - start_time
        return SearchResult.failure(metrics, explored_tiles=explored_boxes)


class GreedyBestFirstSearch(SearchAlgorithm):
    """Greedy Best-First Search (GBFS).

    Evaluates nodes purely on h(n), driving aggressively toward the goal.
    Extremely fast when heuristic gradients are clean, but highly vulnerable
    to local minima and dead-ends. Suboptimal.
    """

    def __init__(self, heuristic: Optional[HeuristicFunc] = None):
        super().__init__(
            name="Greedy Best-First Search (GBFS)",
            historical_year=1960,
            family="Informed",
            optimality_guaranteed=False,
            complete=False,
        )
        self.heuristic = heuristic or heuristic_manhattan

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

        counter = itertools.count()
        init_h = self.heuristic(board, init_state)
        root = SearchNode(state=init_state, g=0.0, h=init_h, depth=0)
        frontier: List[tuple[float, int, SearchNode]] = [(root.h, next(counter), root)]
        visited: Set[SokobanState] = {init_state}
        explored_boxes: Set[Coord] = set(init_state.boxes)

        metrics.generated_nodes = 1
        metrics.peak_frontier = 1

        while frontier:
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions ({max_expansions}) exceeded"
                break

            h_val, _, node = heapq.heappop(frontier)
            metrics.expanded_nodes += 1
            explored_boxes.update(node.state.boxes)

            if board.is_goal(node.state):
                metrics.duration_sec = time.perf_counter() - start_time
                actions, states, steps, pushes = self.reconstruct_path(node)
                metrics.solution_steps = steps
                metrics.solution_pushes = pushes
                return SearchResult(
                    solved=True,
                    actions=actions,
                    states=states,
                    metrics=metrics,
                    explored_tiles=explored_boxes,
                )

            for action, next_state, is_push in board.get_valid_actions(node.state):
                if next_state not in visited:
                    h_next = self.heuristic(board, next_state)
                    if math.isinf(h_next):
                        continue
                    visited.add(next_state)
                    child = SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=node.g + 1,
                        h=h_next,
                        is_push=is_push,
                        depth=node.depth + 1,
                    )
                    metrics.generated_nodes += 1
                    heapq.heappush(frontier, (child.h, next(counter), child))

            metrics.peak_frontier = max(metrics.peak_frontier, len(frontier))

        metrics.duration_sec = time.perf_counter() - start_time
        return SearchResult.failure(metrics, explored_tiles=explored_boxes)


class IDAStar(SearchAlgorithm):
    """Iterative Deepening A* (IDA*, Korf 1985).

    Combines the admissibility and power of A* with the O(d) linear memory of depth-first search.
    Iteratively increases an f-cost bound.
    """

    def __init__(self, heuristic: Optional[HeuristicFunc] = None):
        super().__init__(
            name="IDA* Search",
            historical_year=1985,
            family="Informed",
            optimality_guaranteed=True,
            complete=True,
        )
        self.heuristic = heuristic or heuristic_manhattan

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

        bound = self.heuristic(board, init_state)
        root = SearchNode(state=init_state, g=0.0, h=bound, depth=0)
        metrics.generated_nodes = 1
        explored_boxes: Set[Coord] = set(init_state.boxes)

        def search_rec(
            node: SearchNode, g: float, current_bound: float, path: set[SokobanState]
        ) -> tuple[float, Optional[SearchNode]]:
            metrics.expanded_nodes += 1
            explored_boxes.update(node.state.boxes)
            f = g + node.h
            if f > current_bound:
                return f, None
            if board.is_goal(node.state):
                return -1.0, node

            if time.perf_counter() - start_time > timeout_sec:
                return math.inf, None
            if metrics.expanded_nodes >= max_expansions:
                return math.inf, None

            min_excess = math.inf
            for action, next_state, is_push in board.get_valid_actions(node.state):
                if next_state not in path:
                    h_val = self.heuristic(board, next_state)
                    if math.isinf(h_val):
                        continue

                    child = SearchNode(
                        state=next_state,
                        parent=node,
                        action=action,
                        g=g + 1.0,
                        h=h_val,
                        is_push=is_push,
                        depth=node.depth + 1,
                    )
                    metrics.generated_nodes += 1
                    path.add(next_state)

                    t, goal_node = search_rec(child, g + 1.0, current_bound, path)
                    if goal_node is not None:
                        return -1.0, goal_node
                    if t < min_excess:
                        min_excess = t

                    path.remove(next_state)

            return min_excess, None

        while True:
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions ({max_expansions}) exceeded"
                break

            t, goal_node = search_rec(root, 0.0, bound, {init_state})
            if goal_node is not None:
                metrics.duration_sec = time.perf_counter() - start_time
                actions, states, steps, pushes = self.reconstruct_path(goal_node)
                metrics.solution_steps = steps
                metrics.solution_pushes = pushes
                return SearchResult(
                    solved=True,
                    actions=actions,
                    states=states,
                    metrics=metrics,
                    explored_tiles=explored_boxes,
                )
            if math.isinf(t):
                break
            bound = t

        metrics.duration_sec = time.perf_counter() - start_time
        return SearchResult.failure(metrics, explored_tiles=explored_boxes)
