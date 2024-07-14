from game.level import Level
import pygame
from enum import Enum

class SokobanProblem():
    def State(Level):
        pass
    
    def Action(Enum):
        UP = pygame.K_UP
        DOWN = pygame.K_DOWN
        LEFT = pygame.K_LEFT
        RIGHT = pygame.K_RIGHT
    
    def __init__(self, game):
        self.level = game.level
        self.player = game.player
        
    def initial_state(self):
        return self.level
    
    def actions(self, state: State):
        return [action for action in self.Action]
    
    def result(self, state: State, action: Action):
        self.player.update(action)
        
    def is_goal(self, state: State):
        return state.is_terminal()
    
    def step_cost(self, state: State, action: Action):
        return 1