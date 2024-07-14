from os import path
from typing import List

WALL = 'W'
BOX = 'B'
GOALBOX = 'Y'
GOALPLAYER = 'X'
GOAL = 'G'
PLAYER = 'P'
SPACE = ' '
Pos = tuple[int, int]
Tile = str

class Level:
    def __init__(self, level_file: path):
        """
        Initializes a Level object.

        Args:
            level_file (path): The path to the level file.

        Returns:
            None
        """
        self.tiles:List[List[Tile]] = []
        self.scale = self.load_level(level_file)

    def load_level(self, level_file: path) -> Pos:
        """
        Loads the level from a file.

        Args:
            level_file (path): The path to the level file.

        Returns:
            Pos: The dimensions of the level (width, height).
        """
        with open(level_file, 'r') as file:
            for line in file:
                self.tiles.append(list(line.strip()))
        return len(self.tiles[0]), len(self.tiles)
                
    def locate_player(self) -> Pos|None:
        """
        Locates the player in the level.

        Returns:
            Pos|None: The position of the player, or None if not found.
        """
        for x in range(self.scale[0]):
            for y in range(self.scale[1]):
                if self.is_player(x, y):
                    return x, y
        assert False, 'Player not found'

    def get_tile(self, x:int , y: int) -> Tile:
        """
        Gets the tile at the specified position.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            Tile: The tile at the specified position.
        """
        return self.tiles[y][x]

    def set_tile(self, x: int, y: int, tile: Tile) -> None:
        """
        Sets the tile at the specified position.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.
            tile (Tile): The tile to set.

        Returns:
            None
        """
        self.tiles[y][x] = tile

    def is_wall(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a wall.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a wall, False otherwise.
        """
        return self.tiles[y][x] == WALL

    def is_box(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a box.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a box, False otherwise.
        """
        return self.tiles[y][x] == BOX or self.tiles[y][x] == GOALBOX

    def is_goal(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a goal.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a goal, False otherwise.
        """
        return self.tiles[y][x] == GOAL or self.tiles[y][x] == GOALBOX or self.tiles[y][x] == GOALPLAYER
    
    def is_space(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a space.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a space, False otherwise.
        """
        return self.tiles[y][x] == SPACE or self.tiles[y][x] == GOAL
    
    def is_player(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is the player.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is the player, False otherwise.
        """
        return self.tiles[y][x] == PLAYER or self.tiles[y][x] == GOALPLAYER
    
    def is_terminal(self) -> bool:
        """
        Checks if the level is in a terminal state.

        Returns:
            bool: True if the level is in a terminal state, False otherwise.
        """
        for row in self.tiles:
            if BOX in row:
                return False
        return True