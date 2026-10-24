"""Core domain models for Sokoban."""

from pysokoban.core.board import Board
from pysokoban.core.deadlock import (
    compute_static_deadlock_tiles,
    is_2x2_freeze_deadlock,
    is_corner_deadlock,
    is_state_deadlocked,
)
from pysokoban.core.enums import Action, Tile
from pysokoban.core.state import Coord, SokobanState

__all__ = [
    "Board",
    "SokobanState",
    "Coord",
    "Action",
    "Tile",
    "compute_static_deadlock_tiles",
    "is_corner_deadlock",
    "is_2x2_freeze_deadlock",
    "is_state_deadlocked",
]
