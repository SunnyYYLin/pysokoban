from abc import abstractmethod
import random
from math import exp
from typing import List, Type, Callable

from .search import Search
from .problem import HeuristicSearchProblem, Action

class LocalSearch(Search):
    @abstractmethod
    def __init__(self, problem: HeuristicSearchProblem, max_iter: int = 1000) -> None:
        self.problem = problem
        self.state = problem.initial_state()
        self.solution: List[Action] = []
        self.max_iter = max_iter
        
    @abstractmethod
    def search(self) -> List[List[Action]]:
        pass
    
class HillClimbing(LocalSearch):
    def __init__(self, problem: HeuristicSearchProblem, max_iter: int = 1000) -> None:
        super().__init__(problem, max_iter)
    
    def climb(self, actions: list[Action]) -> Action|None:
        """Execute a hill climbing search algorithm pattern to return an action and decide whether to end."""
        action = min(actions, key=lambda a: self.problem.heuristic(self.problem.result(self.state, a)))
        print(f"From:\n{self.state}\nTo:\n{self.problem.result(self.state, action)}\n")
        h_before = self.problem.heuristic(self.state)
        h_after = self.problem.heuristic(self.problem.result(self.state, action))
        print(f"Before: {h_before}, After: {h_after}")
        slope = h_after - h_before
        if slope >= 0:
            return None
        return action
    
    def search(self) -> List[List[Action]]:
        for _ in range(self.max_iter):
            actions = self.problem.actions(self.state)
            if not actions:
                return []
            chosen_action = self.climb(actions)
            if not chosen_action:
                return []
            print(f"Solution: {chosen_action}\nFrom:\n{self.state}To:\n{self.problem.result(self.state, chosen_action)}\n")
            self.state = self.problem.result(self.state, chosen_action)
            self.solution.append(chosen_action)
            if self.problem.is_goal(self.state):
                return [self.solution]
        return []
    
class StochasticHillClimbing(HillClimbing):
    """
    Stochastic Hill Climbing algorithm for heuristic search problems.
    
    Args:
        problem (HeuristicSearchProblem): The heuristic search problem to solve.
        max_iter (int): The maximum number of iterations (default: 1000).
        p (Callable): The probability function to determine whether to accept a worse move (default: lambda x: 1 if x < 0 else 0.1).
    
    Attributes:
        p (Callable): The probability function to determine whether to accept a worse move.
    
    Methods:
        climb(actions: list[Action]) -> Action: Selects an action to climb based on the stochastic hill climbing algorithm.
    """
    def __init__(self, problem: HeuristicSearchProblem, max_iter: int = 1000, p: Callable = lambda x: 1 if x < 0 else 0.1) -> None:
        super().__init__(problem, max_iter)
        self.p = p
        
    def climb(self, actions: list[Action]) -> Action:
        """
        Selects an action to climb based on the stochastic hill climbing algorithm.
        
        Args:
            actions (list[Action]): The available actions to choose from.
        
        Returns:
            Action: The selected action to climb.
        """
        action = random.choice(actions)
        h_before = self.problem.heuristic(self.state)
        h_after = self.problem.heuristic(self.problem.result(self.state, action))
        slope = h_after - h_before
        prob = self.p(slope)
        if random.random() < prob:
            return action
        else:
            return Action.STAY
    
class FirstChoiceHillClimbing(StochasticHillClimbing):
    def __init__(self, problem: HeuristicSearchProblem, max_iter: int = 1000) -> None:
        super().__init__(problem, max_iter, p=lambda x: 1 if x < 0 else 0)
        
class SimulatedAnnealing(StochasticHillClimbing):
    def __init__(self, problem: HeuristicSearchProblem, max_iter: int = 1000, T_0: float = 1.0, alpha: float = 0.9) -> None:
        super().__init__(problem, max_iter, self.p)
        self.T_0 = T_0
        self.T = self.T_0
        self.alpha = alpha
        
    def p(self, slope: float) -> float:
        p_annealing = 1 if slope < 0 else exp(-slope/self.T)
        self.T = self.T_0 * self.alpha
        return p_annealing
        
class RandomRestart(LocalSearch):
    def __init__(self, problem: HeuristicSearchProblem, algorithm: Type[LocalSearch], max_iter: int = 1000, max_restarts: int = 10):
        super().__init__(problem, max_iter)
        self.max_restarts = max_restarts
        self.algorithm = algorithm
        self.solutions: List[List[Action]] = []
        
    def search(self) -> List[List[Action]]:
        for _ in range(self.max_restarts):
            search = self.algorithm(self.problem, self.max_iter)
            solutions = search.search()
            if len(solutions) > 0:
                self.solutions.append(solutions)
        return self.solutions
    
# TODO
# class LocalBeamSearch(LocalSearch):
#     def __init__(self, problem: HeuristicSearchProblem, k:int=8, max_iter: int = 1000):
#         """
#         Initialize the local beam search algorithm with the given problem, number of states to keep, and maximum number of iterations.
#         """
#         super().__init__(problem, max_iter)
#         self.k = k
#         self.states = [problem.initial_state() for _ in range(k)]
        
#     def search(self) -> List[List[Action]]:
#         """
#         Execute a local beam search algorithm to find a solution to the given problem.
#         Returns a solution or indicates failure.
#         """
#         for _ in range(self.max_iter):
#             new_states = []
#             for state in self.states:
#                 actions = self.problem.actions(state)
#                 if not actions:
#                     return []
#                 new_states.extend([self.problem.result(state, action) for action in actions])
#             self.states = sorted(new_states, key=lambda x: self.problem.heuristic(x))[:self.k]
#             if any(self.problem.is_goal(state) for state in self.states):
#                 self.state = next(filter(lambda x: self.problem.is_goal(x), self.states))
#                 return state
#         return None

# class GeneticAlgorithm(LocalSearch):
#     def __init__(self, problem: HeuristicSearchProblem, max_iter: int = 1000, pop_size: int = 100, mutation_rate: float = 0.1):
#         """
#         Initialize the genetic algorithm with the given problem, maximum number of iterations, population size, and mutation rate.
#         """
#         super().__init__(problem, max_iter)
#         self.pop_size = pop_size
#         self.mutation_rate = mutation_rate
#         self.population = [problem.initial_state() for _ in range(pop_size)]
        
#     def transcribe(self, state: State) -> str:
#         pass
    
#     def revtranscribe(self, string: str) -> State:
#         pass
    
#     def crossover(self, parent1: State, parent2: State) -> State:
#         """
#         Execute a crossover operation on two parent states to return a child state.
#         """
#         raise NotImplementedError("Crossover operation not implemented.")
        
#     def mutate(self, state: State) -> State:
#         """
#         Execute a mutation operation on a state to return a mutated state.
#         """
#         raise NotImplementedError("Mutation operation not implemented.")
        
#     def search(self) -> Optional[State]:
#         """
#         Execute a genetic algorithm to find a solution to the given problem.
#         Returns a solution or indicates failure.
#         """
#         for _ in range(self.max_iter):
#             new_population = []
#             for _ in range(self.pop_size):
#                 parent1 = random.choice(self.population)
#                 parent2 = random.choice(self.population)
#                 child = self.crossover(parent1, parent2)
#                 if random.random() < self.mutation_rate:
#                     child = self.mutate(child)
#                 new_population.append(child)
#             self.population = new_population
#             if any(self.problem.is_goal(state) for state in self.population):
#                 self.state = next(filter(lambda x: self.problem.is_goal(x), self.population))
#                 return True
#         return False
    
# class LRTSAStar(LocalSearch):
#     ''' Learning Real-time A* Algorithm '''
#     def __init__(self, problem: HeuristicSearchProblem, max_iter: int = 100000, pop_size: int = 100, mutation_rate: float = 0.1):
#         super().__init__(problem, max_iter)
#         self.approx_costs = {}
        
#     def approx_h(self, state: State) -> int:
#         if state not in self.approx_costs:
#             self.approx_costs[state] = problem.heuristic(state)
#         return self.approx_costs[state]
        
#     def search(self) -> Optional[State]:
#         for _ in range(self.max_iter):
#             if self.problem.is_goal(self.state):
#                 return self.state
#             actions = self.problem.actions(self.state)
#             if not actions:
#                 return None
#             action = min(actions, key=lambda n: self.approx_h(self.problem.result(self.state, n)))
#             self.state = self.problem.result(self.state, action)
#             self.approx_costs[self.state] += self.state.cost
#         return self.state if self.problem.is_goal(self.state) else None