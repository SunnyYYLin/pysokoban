from typing import Type

from .search import Search
from .problem import SearchProblem
from .best_first_search import DFS

class IterativeDeepen(Search):
    def __init__(self, problem:SearchProblem, algo: Type[Search]= DFS, max_depth = 100):
        super().__init__(problem)
        self.max_depth = max_depth
        self.algo = algo
        
    def search(self):
        for depth in range(1, self.max_depth):
            dfs = self.algo(self.problem, depth=depth)
            result = dfs.search()
            if len(result) > 0:
                return result
        return []