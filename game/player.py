import pygame
from game.level import Level, SPACE, GOALBOX, BOX, GOAL, GOALPLAYER, PLAYER

class Player:
    def __init__(self, level: Level) -> None:
        """
        Initializes a Player object.

        Args:
            level (Level): The level object representing the game level.

        Returns:
            None
        """
        self.level = level
        self.on_goal = False
        self.x, self.y = self.level.locate_player()

    def update(self, key: int) -> bool:
        """
        Updates the player's position based on the given key.

        Args:
            key (int): The key representing the player's movement direction.

        Returns:
            bool: True if the player successfully moved, False otherwise.
        """
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
        """
        Updates the tile at the player's current position when the player leaves.

        Args:
            None

        Returns:
            None
        """
        if self.on_goal:
            self.level.set_tile(self.x, self.y, GOAL)
        else:
            self.level.set_tile(self.x, self.y, SPACE)

    def move(self, dx: int, dy:int) -> bool:
        """
        Moves the player in the specified direction.

        Args:
            dx (int): The change in x-coordinate.
            dy (int): The change in y-coordinate.

        Returns:
            bool: True if the player successfully moved, False otherwise.
        """
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
        """
        Pushes a box in the specified direction.

        Args:
            x (int): The x-coordinate of the box.
            y (int): The y-coordinate of the box.
            dx (int): The change in x-coordinate.
            dy (int): The change in y-coordinate.

        Returns:
            bool: True if the box was successfully pushed, False otherwise.
        """
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