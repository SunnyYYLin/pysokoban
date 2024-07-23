from queue import PriorityQueue, Queue, LifoQueue
from typing import List
import logging
import math

from sealgo.problem import State

from .search import Search
from .problem import *

class BestFirstSearch(Search):
    def __init__(self, problem:SearchProblem) -> None:
        self.problem = problem
        self.frontier = PriorityQueue()
        self.g_costs = {self.problem.initial_state(): 0} # cost so far
        self.predecessors = {self.problem.initial_state(): (None, Action.STAY)}
        self.frontier.put((-1, problem.initial_state()))
        def eval_f(state: State) -> int|float:
            return 1
        self.eval_f = eval_f
        # self.eval_f must be defined in the subclass
        
    def search(self) -> List[List[Action]]:
        while not self.frontier.empty():
            state = self.frontier.get()[1]
            if self.problem.is_goal(state):
                return [self._reconstruct_path(state)]
            self._extend(state)
        return []
    
    def _extend(self, state: State) -> None:
        for action in self.problem.actions(state):
            next_state = self.problem.result(state, action)
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
        logging.info(f"b-factor: {math.log(len(self.predecessors), len(actions))}")
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