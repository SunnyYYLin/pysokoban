import pygame
from game.level import Level, SPACE, GOALBOX, BOX, GOAL, GOALPLAYER, PLAYER

class Player:
    def __init__(self, level: Level) -> None:
        self.level = level
        self.on_goal = False
        self.x, self.y = self.level.locate_player()

    def update(self, key: int) -> bool:
        match key:
            case pygame.K_UP:
                return self.move(0, -1)
            case pygame.K_DOWN:
                return self.move(0, 1)
            case pygame.K_LEFT:
                return self.move(-1, 0)
            case pygame.K_RIGHT:
                return self.move(1, 0)
            case _:
                return False
            
    def leave(self) -> None:
        if self.on_goal:
            self.level.set_tile(self.x, self.y, GOAL)
        else:
            self.level.set_tile(self.x, self.y, SPACE)
            
    # def towards(self, dx:int, dy:int) -> None:
    #     new_x = self.x + dx
    #     new_y = self.y + dy
    #     if not self.level.is_space(new_x, new_y):
    #         assert False, "Cannot move to box"
            
    #     self.x = new_x
    #     self.y = new_y
    #     if self.level.is_goal(new_x, new_y):
    #         self.level.set_tile(new_x, new_y, GOALPLAYER)
    #     else:
    #         self.level.set_tile(new_x, new_y, PLAYER)

    def move(self, dx: int, dy:int) -> bool:
        new_x = self.x + dx
        new_y = self.y + dy

        if self.level.is_wall(new_x, new_y):    
            return False

        if self.level.is_box(new_x, new_y):
            if self.push(new_x, new_y, dx, dy):
                return self.move(dx, dy)
            else:
                return False
        elif self.level.is_space(new_x, new_y):
            self.leave()
            self.x = new_x
            self.y = new_y
            if self.level.is_goal(new_x, new_y):
                self.on_goal = True
                self.level.set_tile(new_x, new_y, GOALPLAYER)
            else:
                self.on_goal = False
                self.level.set_tile(new_x, new_y, PLAYER)
        return True
        
    def push(self, x: int, y: int, dx: int, dy: int) -> bool:
        new_x = x + dx
        new_y = y + dy
        
        if self.level.is_wall(new_x, new_y) or self.level.is_box(new_x, new_y):
            return False
        
        self.level.set_tile(x, y, SPACE)
        if self.level.is_goal(new_x, new_y):
            self.level.set_tile(new_x, new_y, GOALBOX)
        else:
            self.level.set_tile(new_x, new_y, BOX)
        return True