from typing import List
from queue import PriorityQueue

from .problem import BiSearchProblem, Action, State
from .search import Search

class BiDirectional(Search):
    def __init__(self, problem:BiSearchProblem, f_eval = lambda x: 1, b_eval = lambda x: 1) -> None:
        self.problem = problem
        self.f_frontier = PriorityQueue()
        self.b_frontier = PriorityQueue()
        self.predecessors = {self.problem.initial_state(): (None, Action.STAY)}
        self.f_costs = {self.problem.initial_state(): 0}
        self.f_frontier.put((0, self.problem.initial_state()))
        
        goal_states = self.problem.goal_states()
        self.successors = {state: (None, Action.STAY) for state in goal_states}
        self.b_costs = {state: 0 for state in goal_states}
        for state in goal_states:
            self.b_frontier.put((0, state))
            
        self.f_eval = f_eval
        self.b_eval = b_eval
        
    def search(self) -> List[List[Action]]:
        while not self.f_frontier.empty() and not self.b_frontier.empty():
            f_state = self.f_frontier.get()[1]
            b_state = self.b_frontier.get()[1]
            if b_state in self.predecessors:
                return self._reconstruct_path(b_state)
            for action in self.problem.actions(f_state):
                f_new_state = self.problem.result(f_state, action)
                f_cost = self.f_costs[f_state] + self.problem.action_cost(f_state, action)
                if f_new_state not in self.f_costs or f_cost < self.f_costs[f_new_state]:
                    self.predecessors[f_new_state] = (f_state, action)
                    self.f_costs[f_new_state] = f_cost
                    f_eval = f_eval(f_new_state)
                    self.f_frontier.put((f_eval, f_new_state))
            for action in self.problem.actions(b_state):
                b_new_state = self.problem.result(b_state, action)
                b_cost = self.b_costs[b_state] + self.problem.action_cost(b_new_state, action)
                if b_new_state not in self.b_costs or b_cost < self.b_costs[b_new_state]:
                    self.successors[b_new_state] = (b_state, action)
                    self.b_costs[b_new_state] = b_cost
                    b_eval = b_eval(b_new_state)
                    self.b_frontier.put((b_eval, b_new_state))
        return []
    
    def _reconstruct_path(self, inter_state: State) -> List[Action]:
        f_solution = []
        b_state = inter_state
        while self.predecessors[b_state][0] is not None:
            f_solution.append(self.predecessors[b_state][1])
            b_state = self.predecessors[b_state][0]
        f_solution.reverse()
        f_solution.pop()
        
        b_solution = []
        f_state = inter_state
        while self.successors[f_state][0] is not None:
            b_solution.append(self.successors[f_state][1])
            f_state = self.successors[f_state][0]
        
        return f_solution + b_solution
    
class BiAStar(BiDirectional):
    def __init__(self, problem:BiSearchProblem) -> None:
        super().__init__(problem)
        self.f_eval = lambda x: self.f_costs[x] + self.problem.heuristic(x)
        self.b_eval = lambda x: self.b_costs[x] + self.problem.re_heuristic(x)