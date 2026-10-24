"""Immutable, hashable state representation for Sokoban."""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Tuple

Coord = Tuple[int, int]


@dataclass(frozen=True, slots=True)
class SokobanState:
    """Represents a discrete state in Sokoban: the player location and all box locations.

    Attributes:
        player: (row, col) coordinate of the player.
        boxes: FrozenSet of (row, col) coordinates of all boxes.
    """

    player: Coord
    boxes: FrozenSet[Coord]

    def __hash__(self) -> int:
        return hash((self.player, self.boxes))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SokobanState):
            return False
        return self.player == other.player and self.boxes == other.boxes

    def move_player(self, new_player: Coord) -> SokobanState:
        """Return a new state with updated player position (no box moved)."""
        return SokobanState(player=new_player, boxes=self.boxes)

    def push_box(self, old_box: Coord, new_box: Coord, new_player: Coord) -> SokobanState:
        """Return a new state after pushing a box from old_box to new_box."""
        new_boxes = (self.boxes - {old_box}) | {new_box}
        return SokobanState(player=new_player, boxes=frozenset(new_boxes))
