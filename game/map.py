from typing import List
import numpy as np
from enum import Enum, auto
from copy import copy
import random

class Tile(Enum):
    WALL = auto()
    BOX = auto()
    GOALBOX = auto()
    GOALPLAYER = auto()
    GOAL = auto()
    PLAYER = auto()
    SPACE = auto()

Pos = tuple[int, int]
dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
_char_tiles = {
    '#': Tile.WALL,
    '$': Tile.BOX,
    '+': Tile.GOALBOX,
    '-': Tile.GOALPLAYER,
    '.': Tile.GOAL,
    '@': Tile.PLAYER,
    ' ': Tile.SPACE,
}
_tiles_char = {
    Tile.WALL: '#',
    Tile.BOX: '$',
    Tile.GOALBOX: '+',
    Tile.GOALPLAYER: '-',
    Tile.GOAL: '.',
    Tile.PLAYER: '@',
    Tile.SPACE: ' ',
}
_tile_alphabet = {
    Tile.WALL: 'W',
    Tile.BOX: 'B',
    Tile.GOALBOX: 'Y',
    Tile.GOALPLAYER: 'X',
    Tile.GOAL: 'G',
    Tile.PLAYER: 'P',
    Tile.SPACE: ' ',
}
_alphabet_tiles = {
    'W': Tile.WALL,
    'B': Tile.BOX,
    'Y': Tile.GOALBOX,
    'X': Tile.GOALPLAYER,
    'G': Tile.GOAL,
    'P': Tile.PLAYER,
    ' ': Tile.SPACE,
}

class Map:
    """
    Represents a Sokoban game map.

    Attributes:
        tiles (np.ndarray): The array representing the map tiles.
        scale (Pos): The dimensions of the map (width, height).
        player_x (int): The x-coordinate of the player's position.
        player_y (int): The y-coordinate of the player's position.

    Methods:
        locate_player(self) -> Pos: Locates the player in the map.
        locate_boxes(self) -> np.ndarray: Locates the boxes in the map.
        locate_goals(self) -> List[Pos]: Locates the goals in the map.
        get_tile(self, x: int, y: int) -> Tile: Gets the tile at the specified position.
        set_tile(self, x: int, y: int, tile: Tile) -> None: Sets the tile at the specified position.
        is_wall(self, x: int, y: int) -> bool: Checks if the tile at the specified position is a wall.
        is_box(self, x: int, y: int) -> bool: Checks if the tile at the specified position is a box.
        is_goal(self, x: int, y: int) -> bool: Checks if the tile at the specified position is a goal.
        is_space(self, x: int, y: int) -> bool: Checks if the tile at the specified position is a space.
        is_blocked(self, x: int, y: int) -> bool: Checks if the tile at the specified position is blocked.
        is_player(self, x: int, y: int) -> bool: Checks if the tile at the specified position is the player.
        is_all_boxes_in_place(self) -> bool: Checks if all boxes are in their designated places.
        set_to_goal(self) -> None: Sets all boxes to their designated places.
        p_move(self, dx: int, dy: int) -> "Map": Moves the player in a given direction.
        count_deadlock(self) -> int: Counts the number of boxes in deadlock.
    """
    def __init__(self, level_file: str = ''):
        """
        Initializes a Map object. If the level file is provided, it loads the map from the file.

        Args:
            level_file (path): The path to the level file of map.

        Returns:
            None
        """
        if level_file != '':
            self._load(level_file)
            self.scale = self.tiles.shape
            self.player_x, self.player_y = self.locate_player()
            
    def __str__(self) -> str:
        return '\n'.join([''.join([str(_tile_alphabet[tile]) for tile in row]) for row in self.tiles])+'\n'
    
    def __hash__(self) -> int:
        return hash(self.tiles.tobytes())
    
    def __eq__(self, other: "Map") -> bool:
        return np.array_equal(self.tiles, other.tiles)
    
    def __lt__(self, other: "Map") -> bool:
        return hash(self) < hash(other)
    
    def __copy__(self) -> "Map":
        """
        Copies the map.

        Returns:
            Map: The copied map.
        """
        new_map = Map()
        new_map.tiles = np.copy(self.tiles)
        new_map.scale = self.scale
        new_map.player_x, new_map.player_y = self.player_x, self.player_y
        return new_map

    def _load(self, level_file: str) -> None:
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
                tiles.append([_char_tiles[char] for char in line.rstrip('\n')])
        self.tiles = np.array(tiles, dtype=object)

    def locate_player(self) -> Pos:
        """
        Locates the player in the map.

        Returns:
            Pos|None: The position of the player, or None if not found.
        """
        player_pos = np.where((self.tiles == Tile.PLAYER) | (self.tiles == Tile.GOALPLAYER))
        assert len(player_pos[0]) == 1, "There should be only one player in the map."
        self.player_x, self.player_y = player_pos[0][0], player_pos[1][0]
        return self.player_x, self.player_y

    def locate_boxes(self) -> np.ndarray:
        """
        Locates the boxes in the map.
        
        Returns:
            np.ndarray: The positions of the boxes.
        """
        box_pos = np.array(np.where((self.tiles == Tile.BOX) | (self.tiles == Tile.GOALBOX)))
        assert box_pos.shape[1]>0, "There should be at least one box in the map."
        return box_pos.T

    def locate_goals(self) -> np.ndarray:
        """
        Locates the goals in the map.
        
        Returns:
            np.ndarray: The positions of the goals.
        """
        goal_pos = np.array(np.where((self.tiles == Tile.GOAL) |
                                     (self.tiles == Tile.GOALBOX) | (self.tiles == Tile.GOALPLAYER)))
        assert goal_pos.shape[1]>0, "There should be at least one goal in the map."
        return goal_pos.T

    def get_tile(self, x: int, y: int) -> Tile:
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
        return self.tiles[x][y] == Tile.WALL

    def is_box(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a box.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a box(BOX/GOALBOX), False otherwise.
        """
        return self.tiles[x][y] == Tile.BOX or self.tiles[x][y] == Tile.GOALBOX

    def is_goal(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a goal.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a goal(GOAL/GOALBOX/GOALPLAYER), False otherwise.
        """
        return self.tiles[x][y] == Tile.GOAL or self.tiles[x][y] == Tile.GOALBOX or self.tiles[x][y] == Tile.GOALPLAYER

    def is_space(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is a space.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is a space(SPACE/GOAL), False otherwise.
        """
        return self.tiles[x][y] == Tile.SPACE or self.tiles[x][y] == Tile.GOAL
    
    def is_blocked(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is blocked.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is blocked(WALL/BOX), False otherwise.
        """
        return self.is_wall(x, y) or self.is_box(x, y)

    def is_player(self, x: int, y: int) -> bool:
        """
        Checks if the tile at the specified position is the player.

        Args:
            x (int): The x-coordinate of the position.
            y (int): The y-coordinate of the position.

        Returns:
            bool: True if the tile is the player(PLAYER/GOALPLAYER), False otherwise.
        """
        return self.tiles[x][y] == Tile.PLAYER or self.tiles[x][y] == Tile.GOALPLAYER

    def is_all_boxes_in_place(self) -> bool:
        """
        Check if all boxes are in their designated places.

        Returns:
            bool: True if all boxes are in place, False otherwise.
        """
        for row in self.tiles:
            if Tile.BOX in row:
                return False
        return True

    def p_move(self, dx: int, dy: int) -> "Map":
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

        # check if the player will push a box
        if self.is_box(new_x, new_y):
            self._push(new_x, new_y, dx, dy)
            return self.p_move(dx, dy)

        # move freely
        # move off
        if self.is_goal(self.player_x, self.player_y):
            self.set_tile(self.player_x, self.player_y, Tile.GOAL)
        else:
            self.set_tile(self.player_x, self.player_y, Tile.SPACE)
        # move onto
        if self.is_goal(new_x, new_y):
            self.set_tile(new_x, new_y, Tile.GOALPLAYER)
        else:
            self.set_tile(new_x, new_y, Tile.PLAYER)
        # update map-player coordinates
        self.player_x += dx
        self.player_y += dy
        return self
    
    def can_push(self, x: int, y: int, dx: int, dy: int) -> bool:
        """
        Checks if a box can be pushed in a given direction.

        Args:
        - x: The x-coordinate of the box.
        - y: The y-coordinate of the box.
        - dx: The change in x-coordinate.
        - dy: The change in y-coordinate.

        Returns:
        - True if the box can be pushed, False otherwise.
        """
        return not (self.is_blocked(x+dx, y+dy) or self.is_blocked(x-dx, y-dy))

    def _push(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Pushes a box in the specified direction.

        Args:
            x (int): The x-coordinate of the box.
            y (int): The y-coordinate of the box.
            dx (int): The change in x-coordinate for the push.
            dy (int): The change in y-coordinate for the push.

        Returns:
            None
        """
        new_x = x + dx
        new_y = y + dy
        
        # push off
        if self.is_goal(x, y):
            self.set_tile(x, y, Tile.GOAL)
        else:
            self.set_tile(x, y, Tile.SPACE)
        
        # push onto
        if self.is_goal(new_x, new_y):
            self.set_tile(new_x, new_y, Tile.GOALBOX)
        else:
            self.set_tile(new_x, new_y, Tile.BOX)
    
    def count_deadlock(self, _boxes: np.ndarray) -> int:
        """
        Counts the number of boxes in deadlock.
        
        Args:
            boxes (np.ndarray): The positions of the boxes
        
        Returns:
            int: The number of boxes in deadlock.
        """
        map = copy(self)
        boxes = copy(_boxes)
        while np.any(boxes):
            to_delete = []
            for i, (x, y) in enumerate(boxes):
                if (map.can_push(x, y, -1, 0) or
                    map.can_push(x, y, 1, 0) or
                    map.can_push(x, y, 0, -1) or
                    map.can_push(x, y, 0, 1)):
                    map.set_tile(x, y, Tile.SPACE)
                    to_delete.append(i)
            if len(to_delete) == 0:
                return boxes.shape[0]
            if len(to_delete) == boxes.shape[0]:
                return 0
            boxes = np.delete(boxes, to_delete, axis=0)
        return boxes.shape[0]
    
    def player_to_boxes(self, boxes) -> int:
        """
        Calculates the minimum cost for the player to reach the boxes.

        Returns:
            int: The minimum cost for the player to reach the boxes.
        """
        player = np.array((self.player_x, self.player_y)).reshape(1,2)
        cost_matrix = self.cost_matrix(player, boxes)
        return np.amin(cost_matrix).item()
    
    def boxes_to_goals(self) -> int:
        """
        Calculates the sum of minimum cost of moving boxes to goals.

        Returns:
            int: The sum of minimum cost of moving boxes to goals.
        """
        boxes = self.locate_boxes()
        goals = self.locate_goals()
        cost_matrix = self.cost_matrix(boxes, goals)
        return np.amin(cost_matrix, axis=0).sum().item()
    
    @staticmethod
    def cost_matrix(pos1: np.ndarray, pos2: np.ndarray) -> np.ndarray:
        """
        Calculates the cost matrix between two sets of positions.

        Args:
            pos1 (np.ndarray): The first set of positions.
            pos2 (np.ndarray): The second set of positions.

        Returns:
            np.ndarray: The cost matrix representing the distances between each pair of positions.
        """
        distances = np.abs(pos1[:, np.newaxis, :] - pos2[np.newaxis, :, :])
        return distances.sum(axis=2)
    
    def set_to_goal(self, num: int = 10) -> List["Map"]:
        """
        Sets all boxes to their designated places.

        Returns:
            None
        """
        if self.is_goal(self.player_x, self.player_y) == Tile.GOALPLAYER:
            self.set_tile(self.player_x, self.player_y, Tile.GOAL)
        else:
            self.set_tile(self.player_x, self.player_y, Tile.SPACE)
        self.tiles[self.tiles == Tile.BOX] = Tile.SPACE
        self.tiles[self.tiles == Tile.GOAL] = Tile.GOALBOX
        boxes = self.locate_boxes()
        goals = []
        n = 0
        for dir in dirs:
            for box in boxes:
                if self.is_space(box[0]+dir[0], box[1]+dir[1]):
                    if n > num:
                        break
                    n += 1
                    new_map = copy(self)
                    new_map.set_tile(box[0]+dir[0], box[1]+dir[1], Tile.PLAYER)
                    goals.append(new_map)
        return goals
        
    def can_pull(self, x, y, dx, dy) -> bool:
        """
        Checks if a box can be pulled in a given direction.

        Args:
        - x: The x-coordinate of the box.
        - y: The y-coordinate of the box.
        - dx: The change in x-coordinate.
        - dy: The change in y-coordinate.

        Returns:
        - True if the box can be pulled, False otherwise.
        """
        return not (self.is_blocked(x+dx, y+dy) or self.is_blocked(x+2*dx, y+2*dy))
    
    def _pull(self, x, y, dx, dy) -> bool:
        """
        Pulls a box in a given direction.

        Args:
        - x: The x-coordinate of the box.
        - y: The y-coordinate of the box.
        - dx: The change in x-coordinate.
        - dy: The change in y-coordinate.

        Returns:
        - True if the box can be pulled, False otherwise.
        """
        new_x = x + dx
        new_y = y + dy
        
        # pull off
        if self.is_goal(x, y):
            self.set_tile(x, y, Tile.GOAL)
        else:
            self.set_tile(x, y, Tile.SPACE)
        # pull onto
        if self.is_goal(new_x, new_y):
            self.set_tile(new_x, new_y, Tile.GOALBOX)
        else:
            self.set_tile(new_x, new_y, Tile.BOX)
        return True
    
    def p_undo(self, dx, dy, pull: bool = True) -> None:
        last_x = self.player_x - dx
        last_y = self.player_y - dy
        
        # move off
        if self.is_goal(self.player_x, self.player_y):
            self.set_tile(self.player_x, self.player_y, Tile.GOAL)
        else:
            self.set_tile(self.player_x, self.player_y, Tile.SPACE)
        # move onto
        if self.is_goal(last_x, last_y):
            self.set_tile(last_x, last_y, Tile.GOALPLAYER)
        else:
            self.set_tile(last_x, last_y, Tile.PLAYER)
        # pull boxes
        if pull:
            self._pull(last_x, last_y, dx, dy)