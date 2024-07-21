import time
import math
import random
from typing import List, Callable

from .search import Search
from .problem import State, Action, SearchProblem

class MCTSNode:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.children = {}
        self.num_visits = 0
        self.total_reward = 0
        self.is_terminal = parent.problem.is_goal(state)
        self.is_fully_expanded = self.is_terminal
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return f"<Node {self.state}>"

    def expand(self, problem: SearchProblem):
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem: SearchProblem, action):
        next_state = problem.result(self.state, action)
        return MCTSNode(next_state, self, action,
                    problem.action_cost(self.state, action))

    def solution(self):
        return [node.action for node in self.path()[1:]]

    def path(self):
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

class MCTS(Search):
    def __init__(self, problem: SearchProblem, time_limit=None, iteration_limit=None, exploration_constant=1 / math.sqrt(2),
                 rollout_policy: Callable[[State], int|float] = None) -> None:
        super().__init__(problem)
        if time_limit is not None:
            if iteration_limit is not None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            self.time_limit = time_limit
            self.limit_type = 'time'
        else:
            if iteration_limit is None:
                raise ValueError("Must have either a time limit or an iteration limit")
            if iteration_limit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.search_limit = iteration_limit
            self.limit_type = 'iterations'
        self.exploration_constant = exploration_constant
        self.rollout_policy = rollout_policy or self.default_rollout_policy

    def default_rollout_policy(self, state: State) -> int|float:
        while not self.problem.is_goal(state):
            actions = self.problem.actions(state)
            if not actions:
                raise Exception("Non-terminal state has no possible actions: " + str(state))
            action = random.choice(actions)
            state = self.problem.result(state, action)
        return self.problem.action_cost(state, Action.STAY)

    def search(self) -> List[List[Action]]:
        self.root = MCTSNode(self.problem.initial_state(), None)
        
        if self.limit_type == 'time':
            time_limit = time.time() + self.time_limit / 1000
            while time.time() < time_limit:
                self.execute_round()
        else:
            for _ in range(self.search_limit):
                self.execute_round()

        best_child = self.get_best_child(self.root, 0)
        action = next(action for action, node in self.root.children.items() if node is best_child)
        return [self._reconstruct_path(best_child)]

    def execute_round(self) -> None:
        node = self.select_node(self.root)
        reward = self.rollout_policy(node.state)
        self.backpropagate(node, reward)

    def select_node(self, node: "MCTSNode") -> "MCTSNode":
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_child(node, self.exploration_constant)
            else:
                return self.expand(node)
        return node

    def expand(self, node: "MCTSNode") -> "MCTSNode":
        actions = self.problem.actions(node.state)
        for action in actions:
            if action not in node.children:
                new_node = MCTSNode(self.problem.result(node.state, action), node)
                node.children[action] = new_node
                if len(actions) == len(node.children):
                    node.is_fully_expanded = True
                return new_node
        raise Exception("Should never reach here")

    def backpropagate(self, node: "MCTSNode", reward: int|float) -> None:
        while node is not None:
            node.num_visits += 1
            node.total_reward += reward
            node = node.parent

    def get_best_child(self, node: "MCTSNode", exploration_value: float) -> "MCTSNode":
        best_value = float("-inf")
        best_nodes = []
        for child in node.children.values():
            node_value = (child.total_reward / child.num_visits +
                          exploration_value * math.sqrt(2 * math.log(node.num_visits) / child.num_visits))
            if node_value > best_value:
                best_value = node_value
                best_nodes = [child]
            elif node_value == best_value:
                best_nodes.append(child)
        return random.choice(best_nodes)

    def _reconstruct_path(self, node: "MCTSNode") -> List[Action]:
        actions = []
        while node.parent is not None:
            actions.append(node.action)
            node = node.parent
        actions.reverse()
        return actions
