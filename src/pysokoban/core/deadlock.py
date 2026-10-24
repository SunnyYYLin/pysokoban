"""Deadlock detection algorithms for Sokoban.

In AI history, Junghanns & Schaeffer (1997-2001, Rolling Stone) demonstrated that
without domain-specific deadlock detection, search spaces in Sokoban explode exponentially
due to irreversible state transitions.

This module implements:
1. Simple Corner Deadlock: Immediate detection of non-goal boxes stuck in corners.
2. Static Deadlock Precomputation: Reverse reachability pull-search to find all tiles
   from which a box can never reach any goal.
3. 2x2 Freeze Deadlock: Detection of 2x2 blocks of walls and boxes that can never be unlocked.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, FrozenSet, Set, Tuple

if TYPE_CHECKING:
    from pysokoban.core.board import Board
    from pysokoban.core.state import SokobanState

Coord = Tuple[int, int]


def is_corner_deadlock(board: Board, box: Coord) -> bool:
    """Check if a box is trapped in a corner (non-goal tile surrounded by orthogonal walls)."""
    if box in board.goals:
        return False

    r, c = box
    up_wall = (r - 1, c) in board.walls
    down_wall = (r + 1, c) in board.walls
    left_wall = (r, c - 1) in board.walls
    right_wall = (r, c + 1) in board.walls

    return (
        (up_wall and left_wall)
        or (up_wall and right_wall)
        or (down_wall and left_wall)
        or (down_wall and right_wall)
    )


def compute_static_deadlock_tiles(board: Board) -> Set[Coord]:
    """Precompute all floor tiles from which a box can never reach any goal.

    Uses backward pull-search from all goals:
    A box at B can be pulled to B_next in direction D if:
    1. B_next is within bounds and not a wall.
    2. The player position required to pull (B_next + D) is within bounds and not a wall.

    Any walkable tile that cannot be reached by pulling from any goal is a static deadlock tile.
    """
    alive_tiles: Set[Coord] = set()
    queue: deque[Coord] = deque()

    # Seed with all goal positions
    for goal in board.goals:
        if goal not in board.walls:
            alive_tiles.add(goal)
            queue.append(goal)

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        curr_box = queue.popleft()
        cr, cc = curr_box

        for dr, dc in directions:
            # Box would move from curr_box to next_box
            next_box = (cr + dr, cc + dc)
            # Player pulls the box, meaning player stands on the other side of next_box
            puller_pos = (cr + 2 * dr, cc + 2 * dc)

            if (
                next_box not in board.walls
                and puller_pos not in board.walls
                and 0 <= next_box[0] < board.height
                and 0 <= next_box[1] < board.width
                and 0 <= puller_pos[0] < board.height
                and 0 <= puller_pos[1] < board.width
            ):
                if next_box not in alive_tiles:
                    alive_tiles.add(next_box)
                    queue.append(next_box)

    # Any non-wall, in-board tile that is not alive and not a goal is dead
    dead_tiles: Set[Coord] = set()
    for r in range(board.height):
        for c in range(board.width):
            pos = (r, c)
            if pos not in board.walls and pos not in board.goals and pos not in alive_tiles:
                dead_tiles.add(pos)

    return dead_tiles


def is_2x2_freeze_deadlock(board: Board, boxes: FrozenSet[Coord]) -> bool:
    """Check if any 2x2 square consists entirely of walls and boxes with at least one non-goal box.

    A 2x2 solid block of walls/boxes can never be pushed apart, rendering the game unwinnable
    if any of those boxes are not already on goals.
    """
    for box in boxes:
        r, c = box
        # Check all 4 2x2 squares containing (r, c)
        for dr, dc in [(-1, -1), (-1, 0), (0, -1), (0, 0)]:
            r0, c0 = r + dr, c + dc
            tiles = [(r0, c0), (r0 + 1, c0), (r0, c0 + 1), (r0 + 1, c0 + 1)]

            all_blocked = True
            has_non_goal_box = False

            for tr, tc in tiles:
                tpos = (tr, tc)
                if tpos in board.walls:
                    continue
                elif tpos in boxes:
                    if tpos not in board.goals:
                        has_non_goal_box = True
                else:
                    all_blocked = False
                    break

            if all_blocked and has_non_goal_box:
                return True

    return False


def is_state_deadlocked(
    board: Board,
    state: SokobanState,
    static_deadlocks: Set[Coord] | None = None,
    check_freeze: bool = True,
) -> bool:
    """Master deadlock check combining static and dynamic deadlock checks."""
    # 1. Static deadlock check (O(N_boxes))
    if static_deadlocks:
        for box in state.boxes:
            if box in static_deadlocks and box not in board.goals:
                return True

    # 2. Corner deadlock check (O(N_boxes))
    for box in state.boxes:
        if is_corner_deadlock(board, box):
            return True

    # 3. 2x2 freeze deadlock check
    if check_freeze and is_2x2_freeze_deadlock(board, state.boxes):
        return True

    return False
