from queue import PriorityQueue, Queue, LifoQueue
from typing import List, Callable

from sealgo.problem import State

from .search import Search
from .problem import *

# TEST
# from ui.display import Display
# from game.map import Tile
# assets_path = "assets"
# icon_style = "images_v1"
# icon_paths = {
#         Tile.GOALBOX: os.path.join(assets_path, icon_style, "goalbox.png"),
#         Tile.GOALPLAYER: os.path.join(assets_path, icon_style, "goalplayer.png"),
#         Tile.BOX: os.path.join(assets_path, icon_style, "box.png"),
#         Tile.GOAL: os.path.join(assets_path, icon_style, "goal.png"),
#         Tile.WALL: os.path.join(assets_path, icon_style, "wall.png"),
#         Tile.PLAYER: os.path.join(assets_path, icon_style, "player.png"),
#         Tile.SPACE: os.path.join(assets_path, icon_style, "space.png"),
#     }
# d = Display(icon_paths)

class BestFirstSearch(Search):
    def __init__(self, problem:SearchProblem) -> None:
        self.problem = problem
        self.frontier = PriorityQueue()
        init = self.problem.initial_state()
        if isinstance(init, list):
            self.g_costs = {} # cost so far
            self.predecessors = {}
            for state in init:
                self.g_costs[state] = 0
                self.predecessors[state] = (None, Action.STAY)
                self.frontier.put((-1, state))
        else:
            self.g_costs = {init: 0} # cost so far
            self.predecessors = {init: (None, Action.STAY)}
            self.frontier.put((-1, init))
        self.eval_f: Callable = lambda s: 0
        # self.eval_f must be defined in the subclass
        
    def search(self) -> List[List[Action]]:
        while not self.frontier.empty():
            state = self.frontier.get()[1]
            if self.problem.is_goal(state):
                return [self._reconstruct_path(state)]
            self._extend(state)
        return []
    
    def _extend(self, state: State) -> None:
        # d.render(state)
        for action in self.problem.actions(state):
            next_state = self.problem.result(state, action)
            # d.render(next_state)
            g_cost = self.g_costs[state] + self.problem.action_cost(state, action)
            if next_state not in self.g_costs or g_cost < self.g_costs[next_state]:
                self.predecessors[next_state] = (state, action)
                self.g_costs[next_state] = g_cost
                eval = self.eval_f(next_state)
                self.frontier.put((eval, next_state))
    
    def _reconstruct_path(self, state: State) -> List[Action]:
        actions = []
        while state:
            state, action = self.predecessors[state]
            actions.append(action)
        actions.reverse()
        return actions

class BFS(BestFirstSearch):
    def __init__(self, problem:SearchProblem):
        self.problem = problem
        self.frontier = Queue()
        self.predecessors = {self.problem.initial_state(): (None, Action.STAY)}
        self.frontier.put(self.problem.initial_state())
        
    def search(self) -> List[List[Action]]:
        while not self.frontier.empty():
            state = self.frontier.get()
            if self.problem.is_goal(state):
                return [self._reconstruct_path(state)]
            self._extend(state)
        return []
    
    def _extend(self, state: State) -> None:
        for action in self.problem.actions(state):
            next_state = self.problem.result(state, action)
            if next_state not in self.predecessors:
                self.predecessors[next_state] = (state, action)
                self.frontier.put(next_state)
    
class DFS(BestFirstSearch):
    def __init__(self, problem:SearchProblem, max_depth = 100):
        self.problem = problem
        self.frontier = LifoQueue()
        self.predecessors = {self.problem.initial_state(): (None, Action.STAY)}
        self.frontier.put(self.problem.initial_state())
        self.max_depth = max_depth
        
    def search(self) -> List[List[Action]]:
        while not self.frontier.empty():
            state = self.frontier.get()
            if self.problem.is_goal(state):
                return [self._reconstruct_path(state)]
            if len(self._reconstruct_path(state)) < self.max_depth:
                for action in self.problem.actions(state):
                    next_state = self.problem.result(state, action)
                    if next_state not in self.predecessors:
                        self.predecessors[next_state] = (state, action)
                        self.frontier.put(next_state)
        return []
        
class Dijkstra(BestFirstSearch):
    def __init__(self, problem:SearchProblem):
        super().__init__(problem)
        self.eval_f = lambda s: self.g_costs[s]
        
class GBFS(BestFirstSearch):
    def __init__(self, problem:HeuristicSearchProblem):
        super().__init__(problem)
        self.eval_f = lambda s: self.problem.heuristic(s)
        
class AStar(BestFirstSearch):
    def __init__(self, problem:HeuristicSearchProblem, weight:float|int=1):
        super().__init__(problem)
        self.eval_f = lambda s: self.g_costs[s] + weight * self.problem.heuristic(s)