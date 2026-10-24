"""Unit tests for core Sokoban domain logic, state hashing, and deadlock detection."""

from pysokoban.core.board import Board
from pysokoban.core.deadlock import (
    compute_static_deadlock_tiles,
    is_2x2_freeze_deadlock,
    is_corner_deadlock,
)
from pysokoban.core.enums import Action


def test_board_parsing_and_properties():
    lvl_text = """#######
#@ $ .#
#######"""
    board = Board.from_text(lvl_text, name="SimpleTest")
    assert board.height == 3
    assert board.width == 7
    assert len(board.walls) == 16
    assert len(board.goals) == 1
    assert len(board.initial_state.boxes) == 1
    assert board.initial_state.player == (1, 1)
    assert not board.is_goal(board.initial_state)


def test_state_transitions():
    lvl_text = """#######
#@ $ .#
#######"""
    board = Board.from_text(lvl_text)
    state = board.initial_state

    # Action 1: player moves right (1, 1) -> (1, 2)
    actions = board.get_valid_actions(state)
    assert len(actions) == 1
    act, state1, is_push = actions[0]
    assert act == Action.RIGHT
    assert is_push is False
    assert state1.player == (1, 2)
    assert state1.boxes == frozenset([(1, 3)])

    # Action 2: player pushes box right (1, 2) -> (1, 3), box moves (1, 3) -> (1, 4)
    actions2 = board.get_valid_actions(state1)
    right_action = [a for a in actions2 if a[0] == Action.RIGHT][0]
    _, state2, is_push2 = right_action
    assert is_push2 is True
    assert state2.player == (1, 3)
    assert state2.boxes == frozenset([(1, 4)])

    # Action 3: player pushes box right (1, 3) -> (1, 4), box moves to goal (1, 5)
    actions3 = board.get_valid_actions(state2)
    right_action2 = [a for a in actions3 if a[0] == Action.RIGHT][0]
    _, goal_state, is_push3 = right_action2
    assert is_push3 is True
    assert goal_state.player == (1, 4)
    assert goal_state.boxes == frozenset([(1, 5)])
    assert board.is_goal(goal_state)


def test_corner_deadlock():
    lvl_text = """#######
#@.   #
#  $  #
#     #
#######"""
    board = Board.from_text(lvl_text)
    # Box in corner (1, 5) next to upper and right walls
    corner_box = (1, 5)
    assert is_corner_deadlock(board, corner_box) is True

    # Box at center (2, 3) is not deadlocked
    center_box = (2, 3)
    assert is_corner_deadlock(board, center_box) is False

    # Goal tile (1, 2) is not considered a deadlock even if in a corner
    goal_box = (1, 2)
    assert is_corner_deadlock(board, goal_box) is False


def test_2x2_freeze_deadlock():
    # 2 boxes side-by-side against upper wall: (1, 3), (1, 4) are walls; (2, 3), (2, 4) are boxes
    lvl_text = """########
########
###$$###
#  ..  #
#  @   #
########"""
    board = Board.from_text(lvl_text)
    boxes = frozenset([(2, 3), (2, 4)])
    # The 2x2 square [(1, 3), (1, 4), (2, 3), (2, 4)] consists of 2 walls and 2 non-goal boxes
    assert is_2x2_freeze_deadlock(board, boxes) is True


def test_static_deadlocks_precomputation():
    lvl_text = """#######
#@.   #
#     #
#     #
#######"""
    board = Board.from_text(lvl_text)
    deadlocks = compute_static_deadlock_tiles(board)
    assert len(deadlocks) > 0
    # Any non-goal corner tile should be a static deadlock tile
    assert (1, 5) in deadlocks
    assert (3, 1) in deadlocks
    assert (3, 5) in deadlocks
    assert (1, 2) not in deadlocks  # The goal is not a static deadlock
