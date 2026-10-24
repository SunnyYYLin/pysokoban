"""Bidirectional Search (Pohl 1971, Kaindl & Kainz 1997).

Bidirectional search runs two simultaneous searches:
1. Forward search from the initial state toward the goals (pushing boxes).
2. Backward search from the goal state toward the initial state (pulling boxes).

When the two search frontiers intersect, a complete solution is stitched together,
theoretically cutting the effective search depth in half (b^(d/2) + b^(d/2) << b^d).
"""

from __future__ import annotations

import time
from collections import deque
from typing import Dict, List, Optional, Tuple

from pysokoban.algorithms.base import (
    SearchAlgorithm,
    SearchMetrics,
    SearchNode,
    SearchResult,
)
from pysokoban.core.board import Board
from pysokoban.core.enums import Action
from pysokoban.core.state import SokobanState


class BidirectionalSearch(SearchAlgorithm):
    """Bidirectional Search combining forward pushing with backward pulling."""

    def __init__(self, name: str = "Bidirectional Search"):
        super().__init__(
            name=name,
            historical_year=1971,
            family="Bidirectional",
            optimality_guaranteed=True,
            complete=True,
        )

    def _get_backward_predecessors(
        self, board: Board, state: SokobanState
    ) -> List[Tuple[Action, SokobanState, bool]]:
        """Compute states that could have led to this state via forward action.

        In reverse, player at P pulls a box from P + D into P, moving player to P - D.
        Or player at P simply steps back to P - D (without pulling a box).
        """
        predecessors: List[Tuple[Action, SokobanState, bool]] = []
        pr, pc = state.player

        for act in Action:
            dr, dc = act.delta
            # Previous player position would be (pr - dr, pc - dc)
            prev_player = (pr - dr, pc - dc)

            if (
                prev_player in board.walls
                or not (0 <= prev_player[0] < board.height)
                or not (0 <= prev_player[1] < board.width)
            ):
                continue

            # Case 1: Pure player step (no box pulled)
            if prev_player not in state.boxes:
                pred_state = state.move_player(prev_player)
                predecessors.append((act, pred_state, False))

            # Case 2: Player pulled a box from (pr + dr, pc + dc) into (pr, pc)
            box_pos = (pr + dr, pc + dc)
            if box_pos in state.boxes and prev_player not in state.boxes:
                # The box was at prev_box (pr), now at box_pos (pr + dr)
                # In predecessor state: box was at pr, pc; player was at prev_player
                pred_boxes = (state.boxes - {box_pos}) | {(pr, pc)}
                pred_state = SokobanState(player=prev_player, boxes=frozenset(pred_boxes))
                predecessors.append((act, pred_state, True))

        return predecessors

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

        # Forward search structures
        f_frontier: deque[SearchNode] = deque([SearchNode(state=init_state, depth=0)])
        f_visited: Dict[SokobanState, SearchNode] = {init_state: f_frontier[0]}

        # Backward search structures: seed with goal states
        # The goals have boxes on board.goals. For player, choose walkable tiles adjacent to goals.
        b_frontier: deque[SearchNode] = deque()
        b_visited: Dict[SokobanState, SearchNode] = {}

        # Candidate player positions for goal states
        for gr, gc in board.goals:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                pr, pc = gr + dr, gc + dc
                ppos = (pr, pc)
                if (
                    ppos not in board.walls
                    and ppos not in board.goals
                    and 0 <= pr < board.height
                    and 0 <= pc < board.width
                ):
                    goal_state = SokobanState(player=ppos, boxes=board.goals)
                    if goal_state not in b_visited:
                        b_node = SearchNode(state=goal_state, depth=0)
                        b_visited[goal_state] = b_node
                        b_frontier.append(b_node)

        metrics.generated_nodes = len(f_visited) + len(b_visited)

        meeting_state: Optional[SokobanState] = None

        while f_frontier and b_frontier:
            if time.perf_counter() - start_time > timeout_sec:
                metrics.notes = "Timeout reached"
                break
            if metrics.expanded_nodes >= max_expansions:
                metrics.notes = f"Max expansions ({max_expansions}) exceeded"
                break

            # 1. Expand Forward Frontier
            f_node = f_frontier.popleft()
            metrics.expanded_nodes += 1

            for action, next_state, is_push in board.get_valid_actions(f_node.state):
                if next_state not in f_visited:
                    child = SearchNode(
                        state=next_state,
                        parent=f_node,
                        action=action,
                        g=f_node.g + 1,
                        is_push=is_push,
                        depth=f_node.depth + 1,
                    )
                    metrics.generated_nodes += 1
                    f_visited[next_state] = child

                    # Check if meeting backward search
                    if next_state in b_visited:
                        meeting_state = next_state
                        break

                    f_frontier.append(child)

            if meeting_state is not None:
                break

            # 2. Expand Backward Frontier
            b_node = b_frontier.popleft()
            metrics.expanded_nodes += 1

            for action, pred_state, is_push in self._get_backward_predecessors(board, b_node.state):
                if pred_state not in b_visited:
                    child = SearchNode(
                        state=pred_state,
                        parent=b_node,
                        action=action,
                        g=b_node.g + 1,
                        is_push=is_push,
                        depth=b_node.depth + 1,
                    )
                    metrics.generated_nodes += 1
                    b_visited[pred_state] = child

                    # Check intersection
                    if pred_state in f_visited:
                        meeting_state = pred_state
                        break

                    b_frontier.append(child)

            if meeting_state is not None:
                break

            metrics.peak_frontier = max(metrics.peak_frontier, len(f_frontier) + len(b_frontier))

        metrics.duration_sec = time.perf_counter() - start_time

        if meeting_state is not None:
            # Reconstruct forward half
            f_curr = f_visited[meeting_state]
            f_actions, f_states, f_steps, f_pushes = self.reconstruct_path(f_curr)

            # Reconstruct backward half
            b_curr = b_visited[meeting_state]
            b_actions: List[Action] = []
            b_states: List[SokobanState] = []
            b_pushes = 0
            curr: Optional[SearchNode] = b_curr
            while curr is not None and curr.parent is not None:
                if curr.action:
                    b_actions.append(curr.action)
                    if curr.is_push:
                        b_pushes += 1
                curr = curr.parent
                if curr:
                    b_states.append(curr.state)

            total_actions = f_actions + b_actions
            total_states = f_states + b_states
            metrics.solution_steps = len(total_actions)
            metrics.solution_pushes = f_pushes + b_pushes

            return SearchResult(
                solved=True,
                actions=total_actions,
                states=total_states,
                metrics=metrics,
            )

        return SearchResult.failure(metrics)
