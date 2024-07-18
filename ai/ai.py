from sealgo.sealgo_pkg.Problem import SearchProblem
from game.problem import SokobanAction as A
from sealgo.sealgo_pkg.BestFirstSearch import BFS

class ToyAI():
    def __init__(self, problem: SearchProblem):
        self.problem = problem
        self.state = problem.initial_state()
        
    def search(self):
        solutions = []
        solution = [
            A.LEFT, A.UP, A.LEFT, A.DOWN, A.RIGHT, A.RIGHT, A.RIGHT, A.DOWN,
            A.RIGHT, A.UP, A.LEFT, A.UP, A.LEFT, A.LEFT, A.DOWN, A.DOWN,
            A.RIGHT, A.RIGHT
        ]
        solutions.append(solution)
        return solutions
    
AI = BFS
    