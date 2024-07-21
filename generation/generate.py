from game.map import Map, Tile
import numpy as np
from ui.display import Display

class Generate_map:
    def __init__(self,
                 width: int=4,
                 height: int=4,
                 rate: float = 1.9,
                 generate: bool = True) -> None:
        # 初始化棋盘，将所有的地方都设置为墙壁，并随机确定玩家位置
        if generate:
            self.map = Map()
            self.map.tiles = np.full((width, height),
                                     fill_value=Tile.WALL,
                                     dtype=object)
            self.map.scale = self.map.tiles.shape
            self.width = width
            self.height = height
            self.space_limit=66#magic

            #self.x = np.random.randint(0, width)
            #self.y = np.random.randint(0, height)
            self.x=int(self.width/2)
            self.y=int(self.height/2)
            self.map.set_tile(self.x, self.y, Tile.PLAYER)
################################################################为了防止不良结果出现
            self.currentplayer = 1
            self.iter_limits = int(width * height * rate)
            self.iter_times = 0
            self.a=False
            self.move_time = 0
            self.move_time_limit=50000#magic
            self.count_a=0
            self.count_a_limit=20000#magic
            self.all_time=0#!!

            self.frozen = 0             #0表示随机游走，1表示放置箱子，2表示模拟游戏
            self.terminal = False       #表示是否结束状态
            self.new_map = self.map
            
    def restart(self):
            self.map = Map()
            self.map.tiles = np.full((self.width, self.height),
                                     fill_value=Tile.WALL,
                                     dtype=object)
            self.map.scale = self.map.tiles.shape
            self.frozen = 0
            self.terminal = False
            self.iter_times = 0
            self.a=False
            self.move_time = 0
            self.count_a=0
            
            self.x=int(self.width/2)
            self.y=int(self.height/2)
            #self.x = np.random.randint(0, self.map.scale[0])
            #self.y = np.random.randint(0, self.map.scale[1])
            self.map.set_tile(self.x, self.y, Tile.PLAYER)
            
            self.new_map = self.map
            
    def getCurrentPlayer(self):#对齐接口，默认是1
        return self.currentplayer

    def getPossibleActions(self):
        #根据forzen选择不同的actions，对齐库的接口
        possibleActions_0 = []
        possibleActions_1 = []
        possibleActions_2 = []
        
        for x in range(self.map.scale[0]):
            for y in range(self.map.scale[1]):
                possibleActions_1.append(
                    lambda x=x, y=y: self.generate_box(x, y))
                
        for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
            possibleActions_0.append(
                lambda dx=dx, dy=dy: self.move(dx, dy))
            possibleActions_2.append(
                lambda dx=dx, dy=dy: self.move(dx, dy))
            
        possibleActions_0.append(self.freeze)
        possibleActions_1.append(self.end_gene_box)
        possibleActions_2.append(self.end_all)
        
        if self.frozen == 0:
            return possibleActions_0
        elif self.frozen == 1:
            return possibleActions_1
        elif self.frozen == 2:
            return possibleActions_2

    def takeAction(self, action):
        #选取action,对齐库的接口
        c = action()
        self.all_time+=1
        return self

    def isTerminal(self):
        #判断是否进入结束状态，对齐mcts库的接口
        #!!!为了防止直接进入终止加入的判断，理论上不需要这一部分
        if self.terminal:
            #'terminal')
            #input()

            return True
        return False

    def getReward(self):
        #计算激励，对齐库的接口
        value = Value(map=self.map)
        reward = value.reward#-self.all_time*0.0005
        if reward>150:
            print('reward')
            print(reward)
            display=Display()
            display.render(self.map)
        
        self.restart()
        self.all_time=0
        self.terminal = False
        return reward

    def freeze(self) -> bool:
        #从未冻结状态进入冻结状态
        #!!!!!!!!
        self.map.spacelist = []
        for x in range(self.map.scale[0]):
            for y in range(self.map.scale[1]):
                pos = (x, y)
                if self.map.is_space(x, y):
                    self.map.spacelist.append(pos)
        if len(self.map.spacelist)<self.space_limit:   #magic
            pass
        #!!!!!
        else:
            self.frozen = 1
            #print('frozen')
            #print(self.map.tiles)
            return True
        return False

    def leave(self) -> bool:
        self.map.set_tile(self.x, self.y, Tile.SPACE)
        return True

    def push(self, x: int, y: int, dx: int, dy: int) -> bool:
        new_x = x + dx
        new_y = y + dy
        
        if new_x < 0 or new_y < 0 or new_x >= self.map.scale[0] or new_y >= self.map.scale[1]:
            return False
        if self.new_map.is_wall(new_x, new_y) or self.new_map.is_box(new_x, new_y):
            return False

        self.new_map.set_tile(x, y, Tile.SPACE)
        self.new_map.set_tile(new_x, new_y, Tile.BOX)
        #"push()")
        return True

    def move(self, dx, dy) -> bool:
        new_x = self.x + dx
        new_y = self.y + dy
        if new_x < 0 or new_y < 0 or new_x >= self.map.scale[
                0] or new_y >= self.map.scale[1]:
            return False
        if self.frozen == 2:
            if self.new_map.is_wall(new_x, new_y):
                #print('1')#!!!!!!死循环？？？？？？？？？？？？？？？？？
                self.count_a +=1
                if self.count_a>self.count_a_limit:#magic
                    self.restart()
                return False
            if self.new_map.is_box(new_x, new_y):
                if self.push(new_x, new_y, dx, dy):
                    #print('2')
                    return self.move(dx, dy)
                else :
                    self.count_a +=1
                    if self.count_a>self.count_a_limit:#magic
                        self.restart()
                return False
            elif self.new_map.is_space(new_x, new_y):
                self.new_map.set_tile(self.x, self.y, Tile.SPACE)
                self.x = new_x
                self.y = new_y
                self.new_map.set_tile(self.x, self.y, Tile.PLAYER)
                self.move_time+=1###################################################
                #(self.new_map.tiles)

        elif self.frozen == 0:
            self.leave()
            self.x = new_x
            self.y = new_y
            self.map.set_tile(self.x, self.y, Tile.PLAYER)
        return True

    def end_all(self) -> bool:
        if self.new_map.is_box(self.player_x, self.player_y):
            #print('冲突')################################################
            self.restart()
            return False
        if self.move_time>self.move_time_limit:##magic
            self.terminal = True
        #print('end all')
        #print(self.map.tiles)
            self.remove_boxes()
            self.set_goals()
            #print('generated_all')
            #print(self.map.tiles)
            #print('frozen')
            #print(self.frozen)
            self.frozen=0
            self.get_list()
            if len(self.boxlist)<=3:
                self.restart()
                #rint('重开')
                
            return True

    def remove_boxes(self):
        for x in range(self.map.scale[0]):
            for y in range(self.map.scale[1]):
                if self.map.is_box(x, y) and self.new_map.is_box(x, y):
                    self.map.set_tile(x, y, Tile.WALL)

    def set_goals(self):
        for x in range(self.map.scale[0]):
            for y in range(self.map.scale[1]):
                if self.map.is_space(x, y) and self.new_map.is_box(x, y):
                    self.map.set_tile(x, y, Tile.GOAL)

    def __copy__(self) -> "Map":
        self.new_map = Map()
        self.new_map.tiles = [row.copy() for row in self.map.tiles]
        self.new_map.scale = self.map.scale
        self.player_x, self.player_y = self.x, self.y
        return self.new_map

    def end_gene_box(self) -> None:
        ##!!!!!!!!
        self.boxlist = []
        for x in range(self.map.scale[0]):
            for y in range(self.map.scale[1]):
                pos = (x, y)
                if self.map.is_box(x, y):
                    self.boxlist.append(pos)
        if self.frozen == 1 and len(self.boxlist) > 13:#magic
            self.frozen = 2
            #print('generated_box')
            #print(self.map.tiles)
            self.__copy__()

    def generate_box(self, x, y) -> bool:
        ###!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.boxlist = []
        for i in range(self.map.scale[0]):
            for j in range(self.map.scale[1]):
                pos = (i, j)
                if self.map.is_box(i, j):
                    self.boxlist.append(pos)

        if self.frozen == 1 and len(self.boxlist) >= 20:#magic
            self.frozen = 2
            #print('generated_box')
            #print(self.map.tiles)
            self.__copy__()
            
            
        if self.map.is_space(x, y) and self.frozen == 1 :
            self.map.set_tile(x, y, Tile.BOX)
            return True
        return False
    
    def get_list(self) -> None:
        self.boxlist=[]
        for x in range(self.map.scale[0]):
            for y in range(self.map.scale[1]):
                pos = (x, y)
                if self.map.is_box(x, y):
                    self.boxlist.append(pos)


class Value:
    def __init__(self, map):
        self.map = map
        self.boxlist = []
        self.goallist = []

    @property
    def reward(self, wb=5, wc=10, wn=1, k=5) -> float:
        self.get_list(self.map)
        
        Pb = self.num_block_33(self.map)
        Pc = self.Congestion_metric(self.map)
        n = len(self.boxlist)

        score = (wb * Pb + wc * Pc + wn * n) / k
        return score

    def get_list(self, map) -> None:
        for x in range(map.scale[0]):
            for y in range(map.scale[1]):
                pos = (x, y)
                if map.is_goal(x, y):
                    self.goallist.append(pos)
                elif map.is_box(x, y):
                    self.boxlist.append(pos)

    def box_num(self, map, x_1, y_1, x_2, y_2) -> int:
        if x_1 > x_2:
            x_1, x_2 = x_2, x_1
        if y_1 > y_2:
            y_1, y_2 = y_2, y_1
        num = 0
        for x in range(x_1, x_2 + 1):
            for y in range(y_1, y_2 + 1):
                if map.is_box(x, y):
                    num += 1
        return num

    def goal_num(self, map, x_1, y_1, x_2, y_2) -> int:
        if x_1 > x_2:
            x_1, x_2 = x_2, x_1
        if y_1 > y_2:
            y_1, y_2 = y_2, y_1
        num = 0
        for x in range(x_1, x_2 + 1):
            for y in range(y_1, y_2 + 1):
                if map.is_goal(x, y):
                    num += 1
        return num

    def obstacle_num(self, map, x_1, y_1, x_2, y_2) -> int:
        if x_1 > x_2:
            x_1, x_2 = x_2, x_1
        if y_1 > y_2:
            y_1, y_2 = y_2, y_1
        num = 0
        for x in range(x_1, x_2 + 1):
            for y in range(y_1, y_2 + 1):
                if map.is_wall(x, y):
                    num += 1
        return num

    def area(self, x_1, y_1, x_2, y_2) -> int:
        return (abs(x_1 - x_2) + 1) * (abs(y_1 - y_2) + 1)

    def Congestion_metric(self, map, alpha=10, beta=5, gamma=1) -> float:
        congestion = 0
        for i in range(0, len(self.boxlist)):
            x_1, y_1 = self.boxlist[i]
            x_2, y_2 = self.goallist[i]

            b = self.box_num(map, x_1, y_1, x_2, y_2)
            g = self.goal_num(map, x_1, y_1, x_2, y_2)
            o = self.obstacle_num(map, x_1, y_1, x_2, y_2)
            A = self.area(x_1, y_1, x_2, y_2)

            congestion += (alpha * b + beta * g) / (gamma * (A - o))

        return congestion

    def num_block_33(self, map) -> int:
        num = 0
        for x in range(1, self.map.scale[0] - 1):
            for y in range(1, self.map.scale[1] - 1):
                if self.is_block_33(map, x, y):
                    num += 1
        return num

    def is_block_33(self, map, x, y) -> bool:
        n = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1),
                       (1, 0), (1, 1)]:
            if map.is_wall(x + dx, y + dy):
                n += 1
            elif map.is_space(x + dx, y + dy):
                n -= 1
        return not (n == 8 or n == -8)
