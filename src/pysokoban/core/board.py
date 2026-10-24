"""Board representation and state transitions for Sokoban."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import FrozenSet, List, Set, Tuple

from pysokoban.core.deadlock import compute_static_deadlock_tiles
from pysokoban.core.enums import Action, Tile
from pysokoban.core.state import Coord, SokobanState


class Board:
    """Represents the static structure of a Sokoban level (walls and goals)

    along with methods to transition states according to standard Sokoban rules.
    """

    def __init__(
        self,
        walls: FrozenSet[Coord],
        goals: FrozenSet[Coord],
        initial_state: SokobanState,
        height: int,
        width: int,
        name: str = "Level",
    ):
        self.walls = walls
        self.goals = goals
        self.initial_state = initial_state
        self.height = height
        self.width = width
        self.name = name

        # Precompute static deadlock tiles using reverse box-pull search
        self.static_deadlocks: Set[Coord] = compute_static_deadlock_tiles(self)

    @classmethod
    def from_text(cls, text: str, name: str = "Level") -> Board:
        """Parse a board from a multiline string in standard Sokoban ASCII notation.

        Notation support:
            '#' = Wall
            '.' = Goal
            '$' = Box
            '*' = Box on Goal
            '+' = Box on Goal (legacy) or Player on Goal
            '-' = Player on Goal (legacy)
            '@' = Player
            ' ' = Floor
        """
        lines = [line.rstrip("\r\n") for line in text.strip("\n").split("\n")]
        if not lines:
            raise ValueError("Level text cannot be empty.")

        height = len(lines)
        width = max(len(line) for line in lines)

        walls: Set[Coord] = set()
        goals: Set[Coord] = set()
        boxes: Set[Coord] = set()
        player: Coord | None = None

        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                pos = (r, c)
                if ch == Tile.WALL.value:
                    walls.add(pos)
                elif ch == Tile.GOAL.value:
                    goals.add(pos)
                elif ch == Tile.BOX.value:
                    boxes.add(pos)
                elif ch == Tile.BOX_ON_GOAL.value:
                    goals.add(pos)
                    boxes.add(pos)
                elif ch == Tile.PLAYER.value:
                    player = pos
                elif ch == Tile.PLAYER_ON_GOAL.value:
                    # In legacy pysokoban '+' was box on goal, but standard is player on goal.
                    # We can disambiguate: if there are already players, or based on box count vs goal count.
                    # To be robust: if player is already found, '+' is box on goal, otherwise player on goal.
                    if player is None:
                        player = pos
                        goals.add(pos)
                    else:
                        goals.add(pos)
                        boxes.add(pos)
                elif ch == "-":  # legacy player on goal
                    player = pos
                    goals.add(pos)
                elif ch in (" ", "_"):
                    pass

        if player is None:
            raise ValueError("No player '@' found in level definition.")

        if len(boxes) != len(goals):
            # If '+' was parsed as player but count doesn't match, we still support valid boards
            pass

        return cls(
            walls=frozenset(walls),
            goals=frozenset(goals),
            initial_state=SokobanState(player=player, boxes=frozenset(boxes)),
            height=height,
            width=width,
            name=name,
        )

    @classmethod
    def from_file(cls, path: str | Path) -> Board:
        """Load a board from a file path."""
        p = Path(path)
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        return cls.from_text(content, name=p.stem)

    def is_goal(self, state: SokobanState) -> bool:
        """Check if all boxes are positioned on goals."""
        return state.boxes == self.goals

    def is_walkable(self, pos: Coord, state: SokobanState) -> bool:
        """Check if a position is not a wall and not occupied by a box."""
        return (
            pos not in self.walls
            and pos not in state.boxes
            and 0 <= pos[0] < self.height
            and 0 <= pos[1] < self.width
        )

    def get_valid_actions(self, state: SokobanState) -> List[Tuple[Action, SokobanState, bool]]:
        """Compute all legally executable actions from the current state.

        Returns a list of tuples: (Action, NextState, is_push)
        """
        successors: List[Tuple[Action, SokobanState, bool]] = []
        pr, pc = state.player

        for act in Action:
            dr, dc = act.delta
            nr, nc = pr + dr, pc + dc
            target_pos = (nr, nc)

            # Check bounds and walls
            if target_pos in self.walls:
                continue

            if target_pos in state.boxes:
                # Pushing a box: check tile behind the box
                box_target = (nr + dr, nc + dc)
                if (
                    box_target not in self.walls
                    and box_target not in state.boxes
                    and 0 <= box_target[0] < self.height
                    and 0 <= box_target[1] < self.width
                ):
                    next_state = state.push_box(
                        old_box=target_pos, new_box=box_target, new_player=target_pos
                    )
                    successors.append((act, next_state, True))
            else:
                # Simple player movement
                next_state = state.move_player(target_pos)
                successors.append((act, next_state, False))

        return successors

    def get_player_reachable(self, state: SokobanState) -> Set[Coord]:
        """Compute all floor tiles reachable by the player without pushing any box."""
        reachable: Set[Coord] = set()
        queue: deque[Coord] = deque([state.player])
        reachable.add(state.player)

        while queue:
            curr = queue.popleft()
            r, c = curr
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nxt = (r + dr, c + dc)
                if nxt not in reachable and self.is_walkable(nxt, state):
                    reachable.add(nxt)
                    queue.append(nxt)

        return reachable

    def render_ascii(self, state: SokobanState) -> str:
        """Render the board state as an ASCII string."""
        grid: List[List[str]] = []
        for r in range(self.height):
            row: List[str] = []
            for c in range(self.width):
                pos = (r, c)
                is_wall = pos in self.walls
                is_goal = pos in self.goals
                is_box = pos in state.boxes
                is_player = pos == state.player

                if is_wall:
                    row.append("#")
                elif is_player and is_goal:
                    row.append("+")
                elif is_player:
                    row.append("@")
                elif is_box and is_goal:
                    row.append("*")
                elif is_box:
                    row.append("$")
                elif is_goal:
                    row.append(".")
                else:
                    row.append(" ")
            grid.append(row)

        return "\n".join("".join(row).rstrip() for row in grid)
