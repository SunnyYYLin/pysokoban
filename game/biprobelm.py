from typing import TypeAlias, List
from sealgo.problem import BiSearchProblem

from .map import Map
from .problem import SokobanAction, SokobanProblem

class BiSokobanProblem(SokobanProblem):
    def goal_states(self) -> List[SokobanProblem.Action]:
        """
        Returns the goal states of the problem.

        Returns:
        - The list of goal states of the problem.

        """
        return self.level.__copy__().set_to_goal()