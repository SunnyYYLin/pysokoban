from typing import List
import numpy as np
from enum import Enum, auto
from typing import List
import numpy as np

class Tile(Enum):
    WALL = auto()
    BOX = auto()
    GOALBOX = auto()
    GOALPLAYER = auto()
    GOAL = auto()
    PLAYER = auto()
    SPACE = auto()

Pos = tuple[int, int]
_char_tiles = {
    'W': Tile.WALL,
    'B': Tile.BOX,
    'Y': Tile.GOALBOX,
    'X': Tile.GOALPLAYER,
    'G': Tile.GOAL,
    'P': Tile.PLAYER,
    ' ': Tile.SPACE,
}
_tile_chars = {
    Tile.WALL: 'W',
    Tile.BOX: 'B',
    Tile.GOALBOX: 'Y',
    Tile.GOALPLAYER: 'X',
    Tile.GOAL: 'G',
    Tile.PLAYER: 'P',
    Tile.SPACE: ' ',
}

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
            
    def __str__(self) -> str:
        return '\n'.join([''.join([str(_tile_chars[tile]) for tile in row]) for row in self.tiles])+'\n'
    
    def __hash__(self) -> int:
        return hash(str(self))
    
    def __eq__(self, other: "Map") -> bool:
        return np.array_equal(self.tiles, other.tiles)
    
    def __lt__(self, other: "Map") -> bool:
        return hash(self) < hash(other)

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
                tiles.append([_char_tiles[char] for char in line.rstrip('\n')])
        self.tiles = np.array(tiles, dtype=object)
        print(f"Loaded map: \n{self}")
        return tuple(self.tiles.shape)

    def locate_player(self) -> Pos:
        """
        Locates the player in the map.

        Returns:
            Pos|None: The position of the player, or None if not found.
        """
        player_pos = np.where((self.tiles == Tile.PLAYER) | (self.tiles == Tile.GOALPLAYER))
        assert len(player_pos[0]) == 1, "There should be only one player in the map."
        return player_pos[0][0], player_pos[1][0]

    def locate_boxes(self) -> List[Pos]:
        """
        Locates the boxes in the map.

        Returns:
            List[Pos]: The positions of the boxes.
        """
        box_pos = np.where((self.tiles == Tile.BOX) | (self.tiles == Tile.GOALBOX))
        assert len(box_pos[0]) > 0, "There should be at least one box in the map."
        return [(x, y) for x, y in zip(box_pos[0], box_pos[1])]

    def locate_goals(self) -> List[Pos]:
        """
        Locates the goals in the map.

        Returns:
            List[Pos]: The positions of the goals.
        """
        goal_pos = np.where((self.tiles == Tile.GOAL) | (self.tiles == Tile.GOALBOX) | (self.tiles == Tile.GOALPLAYER))
        assert len(goal_pos[0]) > 0, "There should be at least one goal in the map."
        return [(x, y) for x, y in zip(goal_pos[0], goal_pos[1])]

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
    
    def set_to_goal(self) -> None:
        """
        Sets all boxes to their designated places.

        Returns:
            None
        """
        self.tiles[self.tiles == Tile.BOX] = Tile.SPACE
        self.tiles[self.tiles == Tile.GOALBOX] = Tile.GOAL
        

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
            self.set_tile(x, y, Tile.GOAL)
        else:
            self.set_tile(x, y, Tile.SPACE)
        # push onto
        if self.is_goal(new_x, new_y):
            self.set_tile(new_x, new_y, Tile.GOALBOX)
        else:
            self.set_tile(new_x, new_y, Tile.BOX)
        return True
    
    def is_deadlock(self, x: int, y: int) -> bool:
        """
        Checks if the box at the specified position is in a deadlock.

        Args:
            x (int): The x-coordinate of the box.
            y (int): The y-coordinate of the box.

        Returns:
            bool: True if the box is in a deadlock, False otherwise.
        """
        if self.is_goal(x, y):
            return False
        if self.is_blocked(x - 1, y) and self.is_blocked(x, y - 1):
            return True
        if self.is_blocked(x - 1, y) and self.is_blocked(x, y + 1):
            return True
        if self.is_blocked(x + 1, y) and self.is_blocked(x, y - 1):
            return True
        if self.is_blocked(x + 1, y) and self.is_blocked(x, y + 1):
            return True
        return False
    
    def _manhatten_d(self, pos1: Pos, pos2: Pos) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def player_to_boxes(self) -> int:
        boxes = self.locate_boxes()
        return min([self._manhatten_d((self.player_x, self.player_y), box) for box in boxes])
    
    def boxes_to_goals(self) -> int:
        boxes = self.locate_boxes()
        goals = self.locate_goals()
        return sum([min([self._manhatten_d(box, goal) for goal in goals]) for box in boxes])