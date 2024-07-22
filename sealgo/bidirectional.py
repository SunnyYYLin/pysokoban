from typing import List
from queue import PriorityQueue
import os

from .problem import BiSearchProblem, Action, State
from .search import Search

from ui.display import Display
from game.map import Tile
assets_path = "assets"
icon_style = "images_v1"
icon_paths = {
        Tile.GOALBOX: os.path.join(assets_path, icon_style, "goalbox.png"),
        Tile.GOALPLAYER: os.path.join(assets_path, icon_style, "goalplayer.png"),
        Tile.BOX: os.path.join(assets_path, icon_style, "box.png"),
        Tile.GOAL: os.path.join(assets_path, icon_style, "goal.png"),
        Tile.WALL: os.path.join(assets_path, icon_style, "wall.png"),
        Tile.PLAYER: os.path.join(assets_path, icon_style, "player.png"),
        Tile.SPACE: os.path.join(assets_path, icon_style, "space.png"),
    }
d = Display(icon_paths)

class BiDirectional(Search):
    def __init__(self, problem:BiSearchProblem, f_eval = lambda x: 1, b_eval = lambda x: 1) -> None:
        self.problem = problem
        self.f_frontier = PriorityQueue()
        self.b_frontier = PriorityQueue()
        self.predecessors = {self.problem.initial_state(): (None, Action.STAY)}
        self.f_costs = {self.problem.initial_state(): 0}
        self.f_frontier.put((0, self.problem.initial_state()))
        
        goals = self.problem.goal_states()
        self.successors = {state: (None, Action.STAY) for state in goals}
        self.b_costs = {state: 0 for state in goals}
        for state in goals:
            self.b_frontier.put((0, state))
            
        self.f_eval = f_eval
        self.b_eval = b_eval
        
    def search(self) -> List[List[Action]]:
        while not self.f_frontier.empty() and not self.b_frontier.empty():
            f_state = self.f_frontier.get()[1]
            b_state = self.b_frontier.get()[1]
            if f_state in self.successors:
                return [self._reconstruct_path(f_state)]
            for action in self.problem.actions(f_state):
                # d.render(f_state)
                f_new_state = self.problem.result(f_state, action)
                # d.render(f_new_state)
                f_cost = self.f_costs[f_state] + self.problem.action_cost(f_state, action)
                if f_new_state not in self.f_costs or f_cost < self.f_costs[f_new_state]:
                    self.predecessors[f_new_state] = (f_state, action)
                    self.f_costs[f_new_state] = f_cost
                    f_eval = self.f_eval(f_new_state)
                    self.f_frontier.put((f_eval, f_new_state))
            for action in self.problem.actions_to(b_state):
                # d.render(b_state)
                b_new_state = self.problem.reason(b_state, action)
                # d.render(b_new_state)
                b_cost = self.b_costs[b_state] + self.problem.action_cost(b_new_state, action)
                if b_new_state not in self.b_costs or b_cost < self.b_costs[b_new_state]:
                    self.successors[b_new_state] = (b_state, action)
                    self.b_costs[b_new_state] = b_cost
                    b_eval = self.b_eval(b_new_state)
                    self.b_frontier.put((b_eval, b_new_state))
        return []
    
    def _reconstruct_path(self, inter_state: State) -> List[Action]:
        f_solution = []
        b_state = inter_state
        while self.predecessors[b_state][0] is not None:
            # d.render(b_state)
            f_solution.append(self.predecessors[b_state][1])
            b_state = self.predecessors[b_state][0]
        f_solution.reverse()
        f_solution.pop()
        
        b_solution = []
        f_state = inter_state
        while self.successors[f_state][0] is not None:
            # d.render(f_state)
            b_solution.append(self.successors[f_state][1][0])
            f_state = self.successors[f_state][0]
        
        return f_solution + b_solution
    
class BiAStar(BiDirectional):
    def __init__(self, problem:BiSearchProblem) -> None:
        super().__init__(problem)
        self.f_eval = lambda x: self.f_costs[x] + 2*self.problem.heuristic(x)
        self.b_eval = lambda x: self.b_costs[x] + 2*self.problem.re_heuristic(x)