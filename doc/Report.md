# 基于A\*的推箱子求解与推箱子关卡生成

问题分析

推箱子作为一个游戏，既需要用图形界面和用户交互，其求解与关卡生成问题又和人工智能密切相关。Python的pygame库提供了丰富便捷的图形界面显示和用户输入处理功能；同时，Python作为一门流行于科学计算和人工智能的语言，也很适合在本次课程设计以外，在后续的探索中利用深度强化学习进行推箱子问题的求解，具有更多可能性。所以我们选用Python配合pygame库来实现推箱子。

### 问题形式化

推箱子很显然是可以通过搜索求解的问题。根据本学期课程用书《人工智能原理：现代方法》<sup>1</sup>中对搜索问题的形式化描述，推箱子是一个完全可观测的、单智能体的、在确定世界中的、已知的、序贯、静态、离散搜索问题。我们将推箱子问题写作一个类，其根据储存关卡初始化，所包含的方法全部参照书中内容。此外，推箱子问题的动作是有限的，最多为上下左右四种。推箱子问题的状态就是地图上每个位置的内容，这是一个矩阵。矩阵中的元素内容也是有限个，包含墙、空间、箱子、玩家、目标、在目标上的玩家和在目标上的箱子等。

### 推箱子求解

去除掉重复局面，每个推箱子问题的状态空间是有限的，那么在有限时间内（即使可能是超出多项式时间），用搜索算法搜索从初始状态到目标状态的路径就是可解的。问题的关键就是如何避免探索没有必要的状态，这包括达成目标的可能性很低的状态和后续已经无法达到目标的状态（称为死锁）。

由于导致死锁的动作是单向的，并且推箱子问题又是完全可观测的，所以使用离线搜索是好过在线搜索（局部搜索）的。为了避免探索重复状态，甚至造成死循环，为状态类自定义哈希方法，并在搜索中比较即可。为了避免探索没有必要的状态，我们可以人工设计启发式函数和使用A\* 算法。启发式函数需要精心设计。一个好的启发式函数可以大大减少搜索空间，提高搜索效率。启发式函数的主要要求是：

1. 一致性：启发式函数满足三角不等式，即对于任意状态$n$和其邻接状态$n'$，$h(n) \leq c(n, n') + h(n')$，其中$h(n)$为启发式函数值，$c(n, n')$为从$n$到$n'$的实际代价。
2. 可接受性：启发式函数永远不会高估从当前状态到目标状态的代价，即$h(n) \leq\hat{h}(n)$，其中$\hat{h}(n)$为从$n$到目标状态的实际最小代价。

为了避免在死锁的状态下持续探索下去，我们首先在启发式函数中加入一个十分大的死锁惩罚项。有一种方法可以判断出大部分的死锁。多次遍历每个箱子，如果这个箱子可以被推动，就让他消失；继续遍历，如果某一轮还有箱子，但遍历一次并未消去任何箱子，那么可以知道后续的遍历也不能消去这些箱子，即局面出现了死锁。

其次，在推箱子问题中，箱子需要被推到特定的目标位置上。为了更好地估计从当前状态到目标状态的代价，我们可以利用最小最优匹配来计算启发式函数。最小最优匹配其实就是找到如何将箱子分配给各个目标，使得箱子到目标的曼哈顿距离的总和最小。在求出耗费矩阵后，这个算法可以由 `scipy.optimize.linear_sum_assignment`实现。

### 地图生成

生成的推箱子地图需要保证可解性和一定的难度。可解性和难度可以通过对生成地图的直接求解来实现，但是这意味着我们需要消耗指数级的时间。为了避免这个问题，我们选用了一种一定能够保证地图有解的生成方法，并选择了地图的几个特征用于评估生成地图的难度。我们随机生成大量的推箱子问题，并选择难度评分较高的进行输出。

#### 地图难度评估

为了更好的评估地图的难度，我们选择了几个有代表性又便于求解的特征，这包括有效块数$P_b=$`num_block_33`，阻塞系数$P_c=$`Congestion_metric`和箱子的个数$n=$`box_num`。
有效块 `block_33`指的是周围3\*3范围内的八个位置不全是墙壁或空的块,  阻塞系数 ：

$$
P_c=\sum_ {i=1}^ {n}\frac {\alpha b_i+\beta g_i} {\gamma\left(A_i-w_i\right)}
$$

用于评估箱子与目标的密度。

在阻塞系数的公式中，$n$是地图中箱子的数目。按字典序排序，依次将所有的箱子与目标给予编号$i$，则$A_i,b_i,g_i,w_i$分别代表着在编号为i的箱子和目标之间包围的方框所包围的面积、箱子数，目标数，墙壁数，参数$\alpha,\beta,\gamma$选取的值分别为10，5，1。

分别选取系数$w_b,w_c,w_n,k$为15，5，1，50，最终，我们可以将难度表达为：

$$
\text{rewards}=\frac{w_bP_b+w_cP_c+w_nn}{k}
$$

#### 地图生成

为了避免繁琐的证明可解的过程，我们选择在生成时就能保证地图有解的策略。

我们首先将player的初始位置之外的所有的位置设置为障碍物。此时，我们可以进行的行动有移动 `(move)`和冻结 `(freeze)`。当选择移动时，我们会按照选择的方向在地图中进行移动，并且无视墙壁，将走过的所有位置都变成空。当选择冻结时，我们将无法再清除障碍物，并进入下一个状态。

进入第二个状态之后，我们能选择的行动有生成箱子 `generate_box`，和结束生成 `end_gene_box`。当选择生成箱子时，若选择的位置是空的，我们将在这里生成一个箱子。当选择结束生成时，我们无法再生成箱子，并进入下一个状态。

进入第三个状态之后，我们能选择的状态有移动 `move`和结束 `end_all`。当选择移动时，我们会仿照游戏的规则，在地图中进行移动，途中能够进行推箱子，也会受到障碍的影响，只是途中并没有设置目标。当选择结束后，我们除去没有移动过的所有箱子，然后在所有有箱子的地方设置目标。这使得所有目标都可达，同时防止我们生成的地图过于简单。

之后我们对生成的地图按照上面的标准进行评估，同时结束整个生成过程。若地图的得分低于预期设置的值，我们将重新生成，直到生成的地图超过我们的设置的阈值。

### 关卡文件的储存与爬取

经过调查，关卡文件的储存大都由字符表示地块类型，储存在plaintext文件中。主要有两套映射方式，一套是用 `#,$,@,.`等符号，另一套是用 `W,B,P,G`等字母，为了后续利用数据进行训练的便捷，我们储存了两套符号符号系统的转化字典和函数。

在设计要求提供的[推箱子网站](https://sokoban.cn/utility/levelset.php?set=box_it)上，储存着许多关卡，我们编写了一个脚本，根据图像排列的格式，转化为txt文件储存在 `levels/`中。

## 数据结构设计与实现

各个类型的接口详见对应类的docstring.

### 状态地图 `Map`

`Map`定义在 `game/map.py`中，由表示所有地块的 `numpy`数组 `tiles`和表示玩家位置的 `player_x,player_y`构成。为了增强代码可移植性和美观，`tiles`中的数组元素为枚举类型 `Tile`的对象，实际上相当于整数。

`Map`包含一些常用的接口，例如：

1. `set_tiles(x, y, tiles)`：设置某一位置的地块为某个类型。
2. `is_XxX(x, y)`：判断某个位置的地块是否为某个类型。
3. `locate_XxX(x, y)`：给出某个类型的地块所在的位置，类型为$n\times2$的数组，$n$为该类型地块的数量。借助 `numpy.where`这个函数，可以很方便实现。
4. `p_move(dx, dy)`：使得玩家向某个方向移动，如果成功返回 `True`，否则返回 `False`。
5. `cost_matrix()`：给出一个局面的耗费矩阵，$(i,j)$为第$i$个箱子到第$j$个目标的曼哈顿距离。借助 `numpy`的广播性质，这可以很方便实现。
6. `count_deadlock()`：利用上文提到的算法，进行并不精确的死锁判定，查全率可能不够高，但查准率是100%.

值得注意的是，由于 `Map`的状态只和 `tiles`有关，其哈希设计为 `tiles`数组转化为二进制码后的哈希值。

### 推箱子问题规则 `SokobanProblem`

`SokobanProblem`在 `game/problem.py`实现，由储存关卡的文件路径初始化的属性 `level`储存了关卡的初始局面。枚举类型 `SokobanAction`定义了上下左右四个动作。问题规则形式化之后写作以下方法：

1. `initial_state`：关卡的初始局面。
2. `actions(map)`：在某个状态下的所有可能动作。
3. `result(state, action)`：在某个状态下实施某个动作会导致的结果状态。
4. `is_goal(state)`：判断某个状态是否为目标状态。
5. `step_cost(map, action)`：由于每一步的耗费都是相等的，所以统一返回1.

此外，问题某个局面的启发值有 `heuristic(map)`方法输出。

### 搜索算法

在本学期人工智能原理的课程作业中，我们写过一个搜索算法的库 `sealgo`，意思是 `SEArch ALGOrithms`。这次在稍加完善后可以使用。`sealgo`中包含许多局部搜索（`local_search.py`）与最佳优先搜索（`best_first_search.py`）算法，便于我们实验和分析哪种更适用于推箱子问题。每个算法接受一个问题作为参数初始化 `Search(problem)`，使用 `search()`方法搜索答案并返回解的列表，每个解是一系列动作的列表。经过实验和分析，我们选择了A\*算法，所以以下主要介绍A\*算法。

```python
class AStar(BestFirstSearch):
    def __init__(self, problem:HeuristicSearchProblem, weight:float|int=1):
        super().__init__(problem)
        def eval_f(state: State) -> int|float:
            return self.g_costs[state] + \
                weight * self.problem.heuristic(state)
        self.eval_f = eval_f
```

`AStar`继承自抽象父类 `BestFirstSearch`，另外还包含一个权重参数，其对每个状态节点的评价函数 `eval_f`为：

$$
f(n):=g(n)+h(n)
$$

其中$g(n)$为累计代价，即到达该状态的路径代价的总和， $h(n)$为预估代价，即启发式函数给出的到达目标节点的近似路径代价。

```python
class BestFirstSearch(Search):
    def __init__(self, problem:SearchProblem) -> None:
        self.problem = problem
        self.frontier = PriorityQueue()
        self.g_costs = {self.problem.initial_state(): 0} # cost so far
        self.predecessors = {self.problem.initial_state(): (None, Action.STAY)}
        self.frontier.put((-1, problem.initial_state()))
        def eval_f(state: State) -> int|float:
            return 1
        self.eval_f = eval_f
        # self.eval_f must be defined in the subclass
  
    def search(self) -> List[List[Action]]:
        while not self.frontier.empty():
            state = self.frontier.get()[1]
            if self.problem.is_goal(state):
                return [self._reconstruct_path(state)]
            for action in self.problem.actions(state):
                next_state = self.problem.result(state, action)
                g_cost = self.g_costs[state] + self.problem.action_cost(state, action)
                if next_state not in self.g_costs or g_cost < self.g_costs[next_state]:
                    self.predecessors[next_state] = (state, action)
                    self.g_costs[next_state] = g_cost
                    eval = self.eval_f(next_state)
                    self.frontier.put((eval, next_state))
        return []
```

`BestFirstSearch`用优先队列储存其探索的前沿，优先队列中状态的优先级即为 `eval_f(state)`，每次都取出优先级最高的节点探索，并将可拓展的节点加入优先队列。此外，`g_costs`储存了到达每个节点的最小路径代价。`predecessors`储存了每个节点的父节点，在搜索到目标节点时，就可以通过 `_reconstruct_path(state)`重构到达目标节点的路径。

### 显示 `Display`

`Display`模块在 `ui/display.py`实现，负责图形用户界面的显示，初始化时会加载材质，材质风格在 `assets/`中储存，可以在启动时被命令行参数 `--icon-style`指定。枚举类 `State`定义了GUI的可能状态：开始菜单、游戏中、主菜单（暂停菜单）、胜利菜单、AI解决中、关卡生成中。每种菜单状态下分别由一种私有方法渲染，由方法 `run()`判断。

开始菜单 ` _start_menu()`在启动时出现，显示游戏标题，提供开始游戏、生成关卡、退出的选项；主菜单 `_main_menu()`在暂停后出现，显示关卡号，提供继续游戏、重新开始、询问AI、退出的选项；胜利菜单 `_victory_menu()`在每次通关后出现，提供下一关、退出的选项，如果所有关卡都通关，则返回主菜单；游戏中，渲染当前状态的可视化界面，每个地块的材质默认是从设计要求提供的[推箱子网站](https://sokoban.cn/utility/levelset.php?set=box_it)上下载的。

### 用户输入处理 `InputHandler`

`InputHandler`在 `ui/input_handler.py`中实现，负责所有用户输入的处理。枚举类型 `Event`定义了对游戏主逻辑造成的更新信号，例如 `ASK_AI, START, RESTART`等。当用户输入与游戏主逻辑相关时，例如点击“Start”，`InputHandler`返回对应 `Event`；当输入与推箱子问题相关时，例如按 `UP`键，`InputHandler`返回对应 `SokobanAction`。

## 算法复杂度分析

### A\*搜索算法

#### 最坏复杂度

在A\*算法中，时间复杂度主要受以下因素影响：

1. **搜索空间大小**：即状态空间的大小，设为$N$。
2. **启发式函数的质量**：启发式函数越准确，搜索空间越小，时间复杂度越低。

在最坏情况下，A\*算法的时间复杂度为$O(b^d)$，其中$b$为每个状态可能的后继状态数（分支因子），$d$为从初始状态到目标状态的最短路径长度。在推箱子问题中，分支因子小于4，因为每个箱子最多可以朝4个方向移动。所以其最坏时间复杂度为$O(b^4)$。

A\*算法的最坏空间复杂度与时间复杂度相同，也是$O(b^4)$，因为A\*算法需要在 `frontier`中储存探索前沿的节点，同时在 `f_costs`与 `predecessors`中储存已经探索过的节点。

#### 实际复杂度

在每个问题中的平均分支因子$\hat{b}$可以由：

$$
\hat{b}=\log_dn
$$

得到，其中$d$为路径长度，$n$为探索的节点数量。经过实验，如此设计启发式函数，分支因子大多位于2~3。当个别关卡超过3时，搜索可能就需要超过一分钟甚至一小时！

## 结果分析

### 推箱子求解

利用A\*算法，使用最优匹配距离、人箱最近距离和，在20个示例关卡上测试，得到结果如下：

```log
2024-07-22 00:36:32,665 - INFO - Game initialized at 2024-07-22 00:36:32.665623
2024-07-22 00:36:32,917 - INFO - Level 1: Solution found in 0.25 seconds.
2024-07-22 00:36:32,917 - INFO - Solution length: [23]
2024-07-22 00:36:33,986 - INFO - Level 2: Solution found in 1.06 seconds.
2024-07-22 00:36:33,987 - INFO - Solution length: [58]
2024-07-22 00:36:34,128 - INFO - Level 3: Solution found in 0.13 seconds.
2024-07-22 00:36:34,128 - INFO - Solution length: [43]
2024-07-22 00:36:34,317 - INFO - Level 4: Solution found in 0.18 seconds.
2024-07-22 00:36:34,317 - INFO - Solution length: [73]
2024-07-22 00:36:35,151 - INFO - Level 5: Solution found in 0.83 seconds.
2024-07-22 00:36:35,151 - INFO - Solution length: [55]
2024-07-22 00:36:37,616 - INFO - Level 6: Solution found in 2.46 seconds.
2024-07-22 00:36:37,616 - INFO - Solution length: [32]
2024-07-22 00:36:37,825 - INFO - Level 7: Solution found in 0.20 seconds.
2024-07-22 00:36:37,825 - INFO - Solution length: [52]
2024-07-22 00:36:43,365 - INFO - Level 8: Solution found in 5.53 seconds.
2024-07-22 00:36:43,366 - INFO - Solution length: [131]
2024-07-22 00:36:45,326 - INFO - Level 9: Solution found in 1.95 seconds.
2024-07-22 00:36:45,326 - INFO - Solution length: [83]
2024-07-22 00:36:55,762 - INFO - Level 10: Solution found in 10.43 seconds.
2024-07-22 00:36:55,762 - INFO - Solution length: [78]
2024-07-22 00:36:55,944 - INFO - Level 11: Solution found in 0.18 seconds.
2024-07-22 00:36:55,944 - INFO - Solution length: [104]
2024-07-22 00:36:56,500 - INFO - Level 12: Solution found in 0.55 seconds.
2024-07-22 00:36:56,501 - INFO - Solution length: [37]
2024-07-22 00:36:59,449 - INFO - Level 13: Solution found in 2.94 seconds.
2024-07-22 00:36:59,449 - INFO - Solution length: [60]
2024-07-22 00:37:01,674 - INFO - Level 14: Solution found in 2.22 seconds.
2024-07-22 00:37:01,674 - INFO - Solution length: [184]
2024-07-22 00:37:07,933 - INFO - Level 15: Solution found in 6.25 seconds.
2024-07-22 00:37:07,933 - INFO - Solution length: [121]
2024-07-22 00:41:37,750 - INFO - Level 16: Solution found in 269.81 seconds.
2024-07-22 00:41:37,750 - INFO - Solution length: [90]
2024-07-22 00:45:26,704 - INFO - Level 17: Solution found in 228.95 seconds.
2024-07-22 00:45:26,704 - INFO - Solution length: [397]
2024-07-22 00:45:37,443 - INFO - Level 18: Solution found in 10.73 seconds.
2024-07-22 00:45:37,443 - INFO - Solution length: [89]
2024-07-22 01:02:18,220 - INFO - Level 19: Solution found in 1000.78 seconds.
2024-07-22 01:02:18,221 - INFO - Solution length: [209]
2024-07-22 01:02:20,534 - INFO - Level 20: Solution found in 2.31 seconds.
2024-07-22 01:02:20,534 - INFO - Solution length: [73]
```

除了16、17和19关，该算法都能在较快的时间内找到答案。其中19关的时间尤其长。可能是启发式函数设计不恰当，导致探索了很多没有发现的死锁；也可能是阻挡过多，导致最优匹配给出的距离过于低估了箱子需要前往目标的路程，难以发现正确的路径。

### 推箱子生成

连续生成三次推箱子关卡，平均用时15s得到的结果如下图：
![1721654830615](images/Report/1721654830615.png)
![1721654842589](images/Report/1721654842589.png)![1721654846331](images/Report/1721654846331.png)

可以看到，生成的地图都是可解的，并且有一定的多样性和难度。

## 成员分工

- 林佳豪：基本要求1、2，进阶项1
- 田翔宇：进阶项2
  我们分别完成了各自负责部分的技术报告。
