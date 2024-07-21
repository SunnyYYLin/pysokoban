from abc import ABC, abstractmethod
from typing import List

from .problem import SearchProblem, Action

class Search(ABC):
    @abstractmethod
    def __init__(self, problem: SearchProblem) -> None:
        self.problem = problem
    
    @abstractmethod
    def search(self) -> List[List[Action]]:
        pass