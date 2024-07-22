from queue import PriorityQueue, Queue, LifoQueue
from typing import List
import logging
import math

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
            for action in self.problem.actions(state):
                next_state = self.problem.result(state, action)
                g_cost = self.g_costs[state] + self.problem.action_cost(state, action)
                if next_state not in self.g_costs or g_cost < self.g_costs[next_state]:
                    self.predecessors[next_state] = (state, action)
                    self.g_costs[next_state] = g_cost
                    eval = self.eval_f(next_state)
                    self.frontier.put((eval, next_state))
        return []
    
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
            for action in self.problem.actions(state):
                next_state = self.problem.result(state, action)
                if next_state not in self.predecessors:
                    self.predecessors[next_state] = (state, action)
                    self.frontier.put(next_state)
        return []
    
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
        
class IDS(Search):
    def __init__(self, problem:SearchProblem, max_depth = 100):
        super().__init__(problem)
        self.max_depth = max_depth
        
    def search(self):
        for depth in range(1, self.max_depth):
            dfs = DFS(self.problem, depth)
            result = dfs.search()
            if len(result) > 0:
                return result
        return []
        
class Dijkstra(BestFirstSearch):
    def __init__(self, problem:SearchProblem):
        super().__init__(problem)
        def eval_f(state: State) -> int|float:
            return self.g_costs[state]
        
class GBFS(BestFirstSearch):
    def __init__(self, problem:HeuristicSearchProblem):
        super().__init__(problem)
        def eval_f(state: State) -> int|float:
            return self.problem.heuristic(state)
        self.eval_f = eval_f
        
class AStar(BestFirstSearch):
    def __init__(self, problem:HeuristicSearchProblem, weight:float|int=1):
        super().__init__(problem)
        def eval_f(state: State) -> int|float:
            return self.g_costs[state] + \
                weight * self.problem.heuristic(state)
        self.eval_f = eval_f
        
class BiBFS(Search):
    def __init__(self, problem:BiSearchProblem):
        self.problem = problem
        self.f_frontier = PriorityQueue()
        self.b_frontier = PriorityQueue()
        self.predecessors = {self.problem.initial_state(): (None, Action.STAY)}
        goal_states = self.problem.goal_states()
        self.successors = {state: (None, Action.STAY) for state in goal_states}
        self.f_frontier.put((0, self.problem.initial_state()))
        for state in goal_states:
            self.b_frontier.put((0, state))
        
    def search(self) -> List[List[Action]]:
        while not self.f_frontier.empty() and not self.b_frontier.empty():
            f_state = self.f_frontier.get()[1]
            b_state = self.b_frontier.get()[1]
            if b_state in self.predecessors:
                return self._reconstruct_path(f_state) + self._reconstruct_path(b_state)
            for action in self.problem.actions(f_state):
                next_state = self.problem.result(f_state, action)
                if next_state not in self.predecessors:
                    self.predecessors[next_state] = (f_state, action)
                    self.f_frontier.put((1, next_state))
            for action in self.problem.actions(b_state):
                next_state = self.problem.result(b_state, action)
                if next_state not in self.successors:
                    self.successors[next_state] = (b_state, action)
                    self.b_frontier.put((1, next_state))
        return []