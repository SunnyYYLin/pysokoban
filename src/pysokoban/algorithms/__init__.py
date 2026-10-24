"""The Pantheon of AI Search Algorithms (Chronological Order)."""

from typing import Dict, List, Tuple

from pysokoban.algorithms.base import (
    SearchAlgorithm,
    SearchMetrics,
    SearchNode,
    SearchResult,
    SearchStepEvent,
)
from pysokoban.algorithms.bidirectional import BidirectionalSearch
from pysokoban.algorithms.informed import (
    AStar,
    GreedyBestFirstSearch,
    IDAStar,
)
from pysokoban.algorithms.mcts import MonteCarloTreeSearch
from pysokoban.algorithms.pruning import DeadlockPrunedAStar
from pysokoban.algorithms.uninformed import (
    BreadthFirstSearch,
    DepthFirstSearch,
    IterativeDeepeningSearch,
)
from pysokoban.heuristics.heuristics import HungarianMatchingHeuristic, heuristic_manhattan

# Factory functions for registered algorithms
ALGORITHM_REGISTRY: Dict[str, Tuple[str, type]] = {
    "dfs": ("Depth-First Search (DFS, 1950)", DepthFirstSearch),
    "bfs": ("Breadth-First Search (BFS, 1959)", BreadthFirstSearch),
    "gbfs": ("Greedy Best-First Search (GBFS, 1960)", GreedyBestFirstSearch),
    "astar": ("A* Search - Manhattan (1968)", AStar),
    "astar-hungarian": (
        "A* Search - Hungarian Matching (1968)",
        lambda: AStar(
            heuristic=lambda b, s: HungarianMatchingHeuristic(b)(b, s),
            name="A* Search (Hungarian Matching)",
        ),
    ),
    "weighted-astar": (
        "Weighted A* Search (w=1.5, Pohl 1970)",
        lambda: AStar(weight=1.5, name="Weighted A* (w=1.5)"),
    ),
    "bidirectional": ("Bidirectional Search (Pohl 1971)", BidirectionalSearch),
    "ids": ("Iterative Deepening Search (IDS, Korf 1985)", IterativeDeepeningSearch),
    "ida": ("Iterative Deepening A* (IDA*, Korf 1985)", IDAStar),
    "deadlock-astar": (
        "Deadlock-Pruned A* (Rolling Stone style, 1999)",
        DeadlockPrunedAStar,
    ),
    "mcts": ("Monte Carlo Tree Search (MCTS, 2006)", MonteCarloTreeSearch),
}


def get_algorithm(key: str) -> SearchAlgorithm:
    """Retrieve an instantiated search algorithm by key."""
    norm_key = key.lower().strip()
    if norm_key not in ALGORITHM_REGISTRY:
        valid_keys = ", ".join(ALGORITHM_REGISTRY.keys())
        raise ValueError(f"Unknown algorithm key: '{key}'. Available algorithms: {valid_keys}")

    _, factory_or_cls = ALGORITHM_REGISTRY[norm_key]
    if callable(factory_or_cls) and not isinstance(factory_or_cls, type):
        return factory_or_cls()
    return factory_or_cls()


def list_algorithms() -> List[Tuple[str, str, int]]:
    """List all registered algorithms sorted by historical year."""
    items = []
    for key, (label, _factory_or_cls) in ALGORITHM_REGISTRY.items():
        algo = get_algorithm(key)
        items.append((key, label, algo.historical_year))
    items.sort(key=lambda x: x[2])
    return items


__all__ = [
    "heuristic_manhattan",
    "HungarianMatchingHeuristic",
    "SearchAlgorithm",
    "SearchNode",
    "SearchMetrics",
    "SearchResult",
    "SearchStepEvent",
    "BreadthFirstSearch",
    "DepthFirstSearch",
    "IterativeDeepeningSearch",
    "AStar",
    "GreedyBestFirstSearch",
    "IDAStar",
    "DeadlockPrunedAStar",
    "BidirectionalSearch",
    "MonteCarloTreeSearch",
    "ALGORITHM_REGISTRY",
    "get_algorithm",
    "list_algorithms",
]
