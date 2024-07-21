# 基于A*的推箱子求解与基于蒙特卡洛的关卡生成

## 问题分析

推箱子作为一个游戏，既需要用图形界面和用户交互，其求解与关卡生成问题又和人工智能密切相关。Python的pygame库提供了丰富便捷的图形界面显示和用户输入处理功能；同时，Python作为一门流行于科学计算和人工智能的语言，也很适合在本次课程设计以外，在后续的探索中利用深度强化学习进行推箱子问题的求解。

### 问题形式化

推箱子很显然是可以通过搜索求解的问题。根据本学期课程用书《人工智能原理：现代方法》<sup>1</sup>中对搜索问题的形式化描述，推箱子是一个完全可观测的、单智能体的、在确定世界中的、已知的、序贯、静态、离散搜索问题。我们将推箱子问题写作一个类，其根据储存关卡初始化，所包含的方法全部参照书中内容。此外，推箱子问题的动作是有限的，最多为上下左右四种。推箱子问题的状态就是地图上每个位置的内容，这

他根据储存关卡初始化，并且含有如下方法：

### 推箱子求解

去除掉重复局面，每个推箱子问题的状态空间是有限的，那么在有限时间内（即使可能是超出多项式时间），用搜索算法搜索从初始状态到目标状态的路径就是可解的。问题的关键就是如何避免探索没有必要的状态，这包括达成目标的可能性很低的状态和后续已经无法达到目标的状态（称为死锁）。
由于导致死锁的动作是单向的，

### 地图生成

推箱子的地图生成

## 数据结构设计与实现

### 状态——地图`Map`

`Map`由表示所有地块的`numpy`数组`tiles`和表示玩家位置的`player_x,player_y`构成，并包含一些常用的接口，例如：

1. `set_tiles(x, y, tiles)`

### 规则——推箱子问题`SokobanProblem`

1. `initial_state`：关卡的初始局面
2. `actions(map)`：在某个状态下的所有可能动作
3. `result(state, action)`：在某个状态下实施某个动作会导致的结果状态
4. `is_goal`：

```python
class SokobanProblem(HeuristicSearchProblem):
    """
    Represents a Sokoban problem.

    Attributes:
    - State: The state of the problem, represented by a Map object.
    - Action: The possible actions that can be taken, represented by an enumeration.
    - level: The level of the problem, represented by a Map object.

    Methods:
    - __init__(self, level_path: path): Initializes the SokobanProblem object with a level path.
    - initial_state(self): Returns the initial state of the problem.
    - actions(self, map: State): Returns the possible actions for a given state.
    - result(self, map: State, action: Action) -> State: Returns the resulting state after taking an action.
    - is_goal(self, map: State): Checks if the given state is a goal state.
    - step_cost(self, map: State, action: Action): Returns the cost of taking an action in a given state.
    """
```

### 显示`Displayer`

### 用户输入处理`InputHandler`

### 游戏状态表示

### 搜索算法

### 

## 算法复杂度分析

### A\*搜索算法

## 结果分析
```log
2024-07-21 01:37:58,682 - INFO - Game initialized at 2024-07-21 01:37:58.682896
2024-07-21 01:37:58,929 - INFO - Level 1: Solution found in 0.24 seconds.
2024-07-21 01:37:58,929 - INFO - Solution length: [29]
2024-07-21 01:38:00,434 - INFO - Level 2: Solution found in 1.51 seconds.
2024-07-21 01:38:00,435 - INFO - Solution length: [50]
2024-07-21 01:38:00,578 - INFO - Level 3: Solution found in 0.14 seconds.
2024-07-21 01:38:00,578 - INFO - Solution length: [39]
2024-07-21 01:38:00,681 - INFO - Level 4: Solution found in 0.09 seconds.
2024-07-21 01:38:00,681 - INFO - Solution length: [73]
2024-07-21 01:38:08,129 - INFO - Level 5: Solution found in 7.45 seconds.
2024-07-21 01:38:08,129 - INFO - Solution length: [49]
2024-07-21 01:38:10,647 - INFO - Level 6: Solution found in 2.52 seconds.
2024-07-21 01:38:10,647 - INFO - Solution length: [30]
2024-07-21 01:38:10,950 - INFO - Level 7: Solution found in 0.30 seconds.
2024-07-21 01:38:10,950 - INFO - Solution length: [52]
2024-07-21 01:38:13,880 - INFO - Level 8: Solution found in 2.93 seconds.
2024-07-21 01:38:13,880 - INFO - Solution length: [115]
2024-07-21 01:38:15,633 - INFO - Level 9: Solution found in 1.76 seconds.
2024-07-21 01:38:15,633 - INFO - Solution length: [107]
2024-07-21 01:38:21,771 - INFO - Level 10: Solution found in 6.13 seconds.
2024-07-21 01:38:21,771 - INFO - Solution length: [74]
2024-07-21 01:38:22,126 - INFO - Level 11: Solution found in 0.36 seconds.
2024-07-21 01:38:22,126 - INFO - Solution length: [80]
2024-07-21 01:38:22,200 - INFO - Level 12: Solution found in 0.07 seconds.
2024-07-21 01:38:22,200 - INFO - Solution length: [37]
2024-07-21 01:38:26,803 - INFO - Level 13: Solution found in 4.61 seconds.
2024-07-21 01:38:26,803 - INFO - Solution length: [56]
2024-07-21 01:38:27,826 - INFO - Level 14: Solution found in 1.02 seconds.
2024-07-21 01:38:27,826 - INFO - Solution length: [198]
2024-07-21 01:38:34,690 - INFO - Level 15: Solution found in 6.86 seconds.
2024-07-21 01:38:34,690 - INFO - Solution length: [138]
2024-07-21 01:40:25,292 - INFO - Level 16: Solution found in 110.60 seconds.
2024-07-21 01:40:25,292 - INFO - Solution length: [76]
2024-07-21 01:45:39,087 - INFO - Level 17: Solution found in 313.79 seconds.
2024-07-21 01:45:39,087 - INFO - Solution length: [337]
2024-07-21 01:45:56,350 - INFO - Level 18: Solution found in 17.25 seconds.
2024-07-21 01:45:56,351 - INFO - Solution length: [75]
2024-07-21 02:39:47,615 - INFO - Level 19: Solution found in 3231.26 seconds.
2024-07-21 02:39:47,615 - INFO - Solution length: [206]
2024-07-21 02:39:50,507 - INFO - Level 20: Solution found in 2.89 seconds.
2024-07-21 02:39:50,507 - INFO - Solution length: [73]
```
## 成员分工
