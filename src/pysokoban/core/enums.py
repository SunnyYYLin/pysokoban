"""Core enumerations and definitions for Sokoban."""

from __future__ import annotations

from enum import Enum
from typing import Tuple


class Tile(str, Enum):
    """Standard Sokoban board tile representations.

    Supports both standard Soko notation:
        '#' = Wall
        ' ' = Empty floor
        '.' = Goal
        '$' = Box
        '*' = Box on goal (standard notation)
        '+' = Box on goal (legacy compatibility) or Player on goal
        '@' = Player
    """

    WALL = "#"
    FLOOR = " "
    GOAL = "."
    BOX = "$"
    BOX_ON_GOAL = "*"
    PLAYER = "@"
    PLAYER_ON_GOAL = "+"


class Action(Enum):
    """Actions the player can execute (UP, DOWN, LEFT, RIGHT)."""

    UP = (-1, 0, "U")
    DOWN = (1, 0, "D")
    LEFT = (0, -1, "L")
    RIGHT = (0, 1, "R")

    def __init__(self, drow: int, dcol: int, char: str):
        self.drow = drow
        self.dcol = dcol
        self.char = char

    @property
    def delta(self) -> Tuple[int, int]:
        return (self.drow, self.dcol)

    @classmethod
    def from_char(cls, char: str) -> Action:
        upper = char.upper()
        for act in cls:
            if act.char == upper:
                return act
        raise ValueError(f"Unknown action character: {char}")

    def opposite(self) -> Action:
        if self == Action.UP:
            return Action.DOWN
        elif self == Action.DOWN:
            return Action.UP
        elif self == Action.LEFT:
            return Action.RIGHT
        else:
            return Action.LEFT
