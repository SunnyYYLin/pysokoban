from typing import List
import numpy as np

WALL = 'W'
BOX = 'B'
GOALBOX = 'Y'
GOALPLAYER = 'X'
GOAL = 'G'
PLAYER = 'P'
SPACE = ' '
Pos = tuple[int, int]
Tile = str

class Map:
    def __init__(self, level_file: str = ''):
        """
        Initializes a Map object. If the level file is provided, it loads the map from the file.

        Args:
            level_file (path): The path to the level file of map.

        Returns:
            None
        """
        if level_file != '':
            self.scale: Pos = self._load(level_file)
            self.player_x, self.player_y = self.locate_player()


    def _load(self, level_file: str) -> Pos:
        """
        Loads the map from a level file.

        Args:
            level_file (path): The path to the level file.

        Returns:
            Pos: The dimensions of the level (width, height).
        """
        tiles = []
        with open(level_file, 'r') as file:
            for line in file:
                tiles.append(list(line.strip()))
        self.tiles = np.array(tiles)
        return tuple(self.tiles.shape)
                
    def locate_player(self) -> Pos:
        """
        Locates the player in the map.

        Returns:
            Pos|None: The position of the player, or None if not found.
        """
        player_pos = tuple(np.where(self.tiles == PLAYER))
        assert len(player_pos[0]) == 1, "There should be only one player in the map."
        return player_pos[0][0], player_pos[1][0]

    def get_tile(self, x:int , y: int) -> Tile:
        """
        Gets the tile at the specified position.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            Tile: The tile at the specified position.
        """
        return self.tiles[x][y]

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
        self.tiles[x][y] = tile

    def is_wall(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a wall.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a wall, False otherwise.
        """
        return self.tiles[x][y] == WALL

    def is_box(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a box.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a box(BOX/GOALBOX), False otherwise.
        """
        return self.tiles[x][y] == BOX or self.tiles[x][y] == GOALBOX

    def is_goal(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a goal.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a goal(GOAL/GOALBOX/GOALPLAYER), False otherwise.
        """
        return self.tiles[x][y] == GOAL or self.tiles[x][y] == GOALBOX or self.tiles[x][y] == GOALPLAYER
    
    def is_space(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a space.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a space(SPACE/GOAL), False otherwise.
        """
        return self.tiles[x][y] == SPACE or self.tiles[x][y] == GOAL
    
    def is_player(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is the player.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is the player(PLAYER/GOALPLAYER), False otherwise.
        """
        return self.tiles[x][y] == PLAYER or self.tiles[x][y] == GOALPLAYER
    
    def is_all_boxes_in_place(self) -> bool:
            """
            Check if all boxes are in their designated places.
            
            Returns:
                bool: True if all boxes are in place, False otherwise.
            """
            for row in self.tiles:
                if BOX in row:
                    return False
            return True
    
    def __copy__(self) -> "Map":
        """
        Copies the map.

        Returns:
            Map: The copied map.
        """
        new_map = Map()
        new_map.tiles = [row.copy() for row in self.tiles]
        new_map.scale = self.scale
        new_map.player_x, new_map.player_y = self.player_x, self.player_y
        return new_map
    
    def p_move(self, dx: int, dy: int):
        """
        Moves the player in a given direction.

        Args:
        - dx: The change in x-coordinate.
        - dy: The change in y-coordinate.

        Returns:
        - The new state after moving the player.

        """
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        # assert self.is_player(self.player_x, self.player_y), "Only the player can move."

        # check if the player will move into the wall
        if self.is_wall(new_x, new_y):
            return self

        # check if the player will push a box
        if self.is_box(new_x, new_y):
            if self._push(new_x, new_y, dx, dy):
                return self.p_move(dx, dy)
            else:
                return self

        # move freely
        # move off
        if self.is_goal(self.player_x, self.player_y):
            self.set_tile(self.player_x, self.player_y, GOAL)
        else:
            self.set_tile(self.player_x, self.player_y, SPACE)
        # move onto
        if self.is_goal(new_x, new_y):
            self.set_tile(new_x, new_y, GOALPLAYER)
        else:
            self.set_tile(new_x, new_y, PLAYER)
        # update map-player coordinates
        self.player_x += dx
        self.player_y += dy
        return self

    def _push(self, x: int, y: int, dx: int, dy: int) -> bool:
        """
        Pushes a box in a given direction.

        Args:
        - x: The x-coordinate of the box.
        - y: The y-coordinate of the box.
        - dx: The change in x-coordinate.
        - dy: The change in y-coordinate.

        Returns:
        - True if the box can be pushed, False otherwise.

        """
        new_x = x + dx
        new_y = y + dy
        # assert self.is_box(x, y), "Only boxes can be pushed."
        
        # check if the box can be pushed
        if self.is_wall(new_x, new_y) or self.is_box(new_x, new_y):
            return False
        # push off
        if self.is_goal(x, y):
            self.set_tile(x, y, GOAL)
        else:
            self.set_tile(x, y, SPACE)
        # push onto
        if self.is_goal(new_x, new_y):
            self.set_tile(new_x, new_y, GOALBOX)
        else:
            self.set_tile(new_x, new_y, BOX)
        return True