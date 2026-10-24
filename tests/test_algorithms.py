"""Integration tests for all search algorithms in the Chronicle."""

import pytest

from pysokoban.algorithms import ALGORITHM_REGISTRY, get_algorithm
from pysokoban.core.board import Board


@pytest.fixture
def tier1_board():
    return Board.from_file("levels/02_benchmark/tier1_micro_1box.txt")


@pytest.fixture
def tier2_board():
    return Board.from_file("levels/02_benchmark/tier2_dual_2box.txt")


@pytest.mark.parametrize("algo_key", list(ALGORITHM_REGISTRY.keys()))
def test_all_algorithms_on_tier1(tier1_board, algo_key):
    """Ensure every single algorithm in the registry solves the 1-box micro level."""
    algo = get_algorithm(algo_key)
    result = algo.solve(tier1_board, timeout_sec=10.0)

    assert result.solved is True
    assert result.metrics.solution_steps == 3
    assert result.metrics.solution_pushes == 2
    assert result.metrics.expanded_nodes > 0
    assert result.metrics.duration_sec >= 0.0


def test_deadlock_pruning_efficiency(tier2_board):
    """Verify that Deadlock-Pruned A* expands significantly fewer nodes than standard BFS."""
    bfs = get_algorithm("bfs")
    dl_astar = get_algorithm("deadlock-astar")

    res_bfs = bfs.solve(tier2_board)
    res_dl = dl_astar.solve(tier2_board)

    assert res_bfs.solved is True
    assert res_dl.solved is True
    assert res_dl.metrics.expanded_nodes < res_bfs.metrics.expanded_nodes
    # Deadlock A* should prune at least 40% of the nodes
    assert res_dl.metrics.expanded_nodes < res_bfs.metrics.expanded_nodes * 0.6
