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
        self.tiles:List[List[Tile]] = []
        self.scale = self.load_level(level_file)

    def load_level(self, level_file: path) -> Pos:
        with open(level_file, 'r') as file:
            for line in file:
                self.tiles.append(list(line.strip()))
        return len(self.tiles[0]), len(self.tiles)
                
    def locate_player(self) -> Pos|None:
        for x in range(self.scale[0]):
            for y in range(self.scale[1]):
                if self.is_player(x, y):
                    return x, y
        assert False, 'Player not found'

    def get_tile(self, x:int , y: int) -> Tile:
        return self.tiles[y][x]

    def set_tile(self, x: int, y: int, tile: Tile) -> None:
        self.tiles[y][x] = tile

    def is_wall(self, x: int, y: int) -> bool:
        return self.tiles[y][x] == WALL

    def is_box(self, x: int, y: int) -> bool:
        return self.tiles[y][x] == BOX or self.tiles[y][x] == GOALBOX

    def is_goal(self, x: int, y: int) -> bool:
        return self.tiles[y][x] == GOAL or self.tiles[y][x] == GOALBOX or self.tiles[y][x] == GOALPLAYER
    
    def is_space(self, x: int, y: int) -> bool:
        return self.tiles[y][x] == SPACE or self.tiles[y][x] == GOAL
    
    def is_player(self, x: int, y: int) -> bool:
        return self.tiles[y][x] == PLAYER or self.tiles[y][x] == GOALPLAYER
    
    def is_terminal(self) -> bool:
        for row in self.tiles:
            if BOX in row:
                return False
        return True