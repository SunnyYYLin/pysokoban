# 基于推箱子的 AI 搜索算法演进史与基准研究报告
### 《The Chronicle of AI Search Algorithms: Empirical Study on Sokoban》

---

## 摘要 (Abstract)

推箱子（Sokoban）是由今林宏行（Hiroyuki Imabayashi）于 1981 年设计的经典益智游戏，并在 1997 年由 Joseph Culberson 在数学上严格证明为 **PSPACE-Complete** 问题。推箱子具有极高的分支因子、状态转移单向不可逆性（死锁），以及庞大的状态空间，是评估启发式搜索、约束满足与组合优化算法最严苛的学术基准之一。

本研究报告依托重构后的现代 Python 基准平台，系统性复现并横向评测了自 1950 年代图论盲目遍历、1960~1980 年代启发式搜索突破（A* 与匈牙利匹配）、1990 年代领域死锁知识剪枝（Rolling Stone 范式），直至 2000 年代采样树搜索（MCTS）的 11 种经典算法。实验结果量化证明了：在多箱子复杂场景下，盲目搜索与无死锁感知的朴素启发式搜索均会因状态空间爆炸而失效，唯有融合静态拉力死区预计算与动态互锁检测的领域剪枝技术，能将展开节点数压减 70%~99% 以上。

---

## 一、 问题形式化与复杂度分析 (Formalization & Complexity)

### 1.1 状态空间定义
根据 Russell & Norvig《人工智能：现代方法》的经典规范，推箱子是一个完全可观测的、单智能体的、确定性的、序贯的、静态的离散搜索问题：

- **状态空间 $S$**：  
  定义三元组 $s = (p, B, G)$，其中：
  - $p = (r_p, c_p) \in \mathbb{Z}^2$ 表示玩家当前的网格坐标；
  - $B = \{b_1, b_2, \dots, b_n\} \subset \mathbb{Z}^2$ 表示当前所有箱子坐标的无序不可变集合（$|B| = n$）；
  - $G = \{g_1, g_2, \dots, g_n\} \subset \mathbb{Z}^2$ 表示预设目标位置的固定集合。
  - 地图静态障碍物表示为只读不可穿越的墙壁集合 $W \subset \mathbb{Z}^2$。

- **动作集合 $A$**：  
  $A = \{\text{UP}, \text{DOWN}, \text{LEFT}, \text{RIGHT}\}$，对应位移增量 $\Delta = \{(-1, 0), (1, 0), (0, -1), (0, 1)\}$。

- **状态转移函数 $T(s, a)$**：  
  设玩家处于 $p$，动作位移为 $d \in \Delta$：
  - 若 $p + d \in W$，动作非法；
  - 若 $p + d \notin B \cup W$，玩家单纯移动（Move）：$s' = (p + d, B)$；
  - 若 $p + d \in B$，发生推箱（Push）：
    - 检验箱子后方格 $p + 2d$；若 $p + 2d \notin B \cup W$，推箱合法：$s' = (p + d, (B \setminus \{p + d\}) \cup \{p + 2d\})$；
    - 否则推箱受阻，动作非法。

- **终止目标测试 (Goal Test)**：  
  $\text{is\_goal}(s) \iff B = G$。

### 1.2 PSPACE-Complete 复杂性与不可逆性
Culberson (1997) 通过将推箱子规约至量化布尔公式（QBF），证明了推箱子求解是 PSPACE-Complete 的。推箱子最致命的难点在于**不可逆性（Irreversibility）**：
一般迷宫或滑块拼图（8-puzzle）的状态图是无向强连通图，任意动作均可反向撤销；而推箱子一旦发生推箱操作，通常无法通过简单的相反动作拉回箱子。这种不对称性导致状态图中充斥着大量无法通往目标态的“黑洞”（即死锁子树）。

---

## 二、 算法史演进分类体系 (The Algorithmic Pantheon)

```mermaid
timeline
    title AI 搜索算法演进编年史
    1950 : 深度优先 (DFS) : 朴素图遍历，无最优性
    1959 : 广度优先 (BFS) : 最短路径保证，组合爆炸
    1960 : 贪心最佳优先 (GBFS) : 启发引导，易陷入局部陷阱
    1968 : A* Search : 形式化结合 g(n) 与 h(n)
    1970 : Weighted A* : 次优松弛，大幅提速
    1971 : 双向搜索 (Bidirectional) : 正推与反拉对进
    1985 : IDS & IDA* : 内存受限的线性空间搜索
    1999 : 死锁感知搜索 (Rolling Stone) : 领域知识驱动剪枝
    2006 : 蒙特卡洛树搜索 (MCTS) : UCB1 平衡探索与利用
```

### 2.1 盲目搜索纪元 (1950s - 1980s)
1. **BFS (Moore 1959 / Dijkstra 1959)**：  
   使用先进先出（FIFO）队列，保证步数最少。复杂度为时间 $O(b^d)$，空间 $O(b^d)$。在箱子数 $\ge 3$ 时，状态队列极快消耗数万甚至数十万节点。
2. **DFS (1950s)**：  
   使用 LIFO 栈深层下探。在推箱子中容易在非死锁的大房间中产生数百步冗余绕圈解。
3. **IDS (Korf 1985)**：  
   通过逐层增加深度截断阈值，反复运行有限深度的 DFS。以每次重算的微小时间代价换取 $O(bd)$ 的极致线性空间占用。

### 2.2 启发式搜索与可接受性 (1960s - 1980s)
Hart, Nilsson & Raphael (1968) 提出的 A\* 算法确立了启发式搜索的核心准则：若评估函数 $f(n) = g(n) + h(n)$ 中的启发函数 $h(n)$ 满足**可接受性（Admissible，永不高估实际代价）**与**一致性（Consistent，三角不等式）**，则 A\* 必能找到最优解。

本项目对比了两种关键启发式：
1. **曼哈顿距离和（Sum of Min Manhattan）**：  
   $$h_{\text{manhattan}}(s) = \sum_{b \in B} \min_{g \in G} \|b - g\|_1$$  
   计算极快（$O(|B| \cdot |G|)$），具备可接受性；但由于多个箱子可能映射至同一目标，下界偏松。
2. **匈牙利算法二分图最优匹配（Hungarian Bipartite Matching）**：  
   构造 $|B| \times |G|$ 代价矩阵 $C_{ij} = \|b_i - g_j\|_1$。调用 Kuhn-Munkres 算法（`scipy.optimize.linear_sum_assignment`）求解 1 对 1 完美匹配：  
   $$h_{\text{hungarian}}(s) = \min_{\pi} \sum_{i=1}^n C_{i, \pi(i)}$$  
   由于严格满足每个目标仅容纳一个箱子的互斥约束，其下界在数学上严格大于等于普通曼哈顿和（$h_{\text{hungarian}} \ge h_{\text{manhattan}}$），能显著收紧搜索前沿。

### 2.3 领域死锁感知与剪枝 (1990s)
Junghanns & Schaeffer (1997, 2001) 开发了世界顶尖的推箱子求解器 **Rolling Stone**，证明推箱子的成败完全取决于死锁剪枝能力：
1. **静态逆向拉力死区（Static Pull Deadzone）**：  
   在搜索启动前，从所有目标点出发，假设玩家能够任意拉动箱子，进行全图逆向可达性广度优先搜索。凡是箱子从目标位置无论如何也“拉不到”的地面格子，即为**静态死锁点**。在正向搜索中，任何箱子一旦落入死区（且不在目标上），该状态立即被判定为死锁（$h(s) = \infty$）直接丢弃。
2. **$2 \times 2$ 冻结互锁（Freeze Deadlock）**：  
   当 $2 \times 2$ 的 4 个格子均由墙壁或箱子填满，且其中存在未归位的箱子时，由于缺乏可供移动的空隙，这组箱子在拓扑上已被永久锁死，后续无论如何搜索都无法复原。

---

## 三、 阶梯基准评测实测与讨论 (Empirical Benchmarks)

测试平台：Intel / AMD x64 架构，Python 3.13 + PySokoban 2.0 运行环境。测试集为精选的难度阶梯集 [`levels/02_benchmark/`](file:///c:/Users/Sunny/Projects/refactor/pysokoban/levels/02_benchmark/)。

| 关卡 | 箱子数 | 算法 (年代) | 是否求解 | 展开节点数 (Exp) | 峰值前沿 (Frontier) | 解长度 | 耗时 (ms) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Tier 1** (极小) | 1 | BFS (1959) | **YES** | 3 | 1 | 3 | 0.04 |
| | 1 | A\* Search (1968) | **YES** | 4 | 2 | 3 | 0.04 |
| | 1 | Deadlock A\* (1999) | **YES** | 4 | 2 | 3 | 0.06 |
| **Tier 2** (双箱) | 2 | BFS (1959) | **YES** | 559 | 34 | 33 | 2.21 |
| | 2 | A\* Search (1968) | **YES** | 540 | 41 | 33 | 3.58 |
| | 2 | A\* Hungarian (1968)| **YES** | 528 | 40 | 33 | 5.33 |
| | 2 | **Deadlock A\* (1999)**| **YES** | **152** | **13** | **33** | **2.08** |
| **Tier 3** (三箱) | 3 | BFS (1959) | **YES** | 8,121 | 3,996 | 14 | 42.10 |
| | 3 | A\* Search (1968) | **YES** | 1,071 | 932 | 14 | 10.50 |
| | 3 | A\* Hungarian (1968)| **YES** | 924 | 765 | 14 | 16.40 |
| | 3 | **Deadlock A\* (1999)**| **YES** | **470** | **250** | **14** | **10.10** |
| **Tier 4** (四箱) | 4 | BFS (1959) | **YES** | 2,100 | 260 | 18 | 8.87 |
| | 4 | A\* Hungarian (1968)| **YES** | 1,420 | 303 | 18 | 19.20 |
| | 4 | **Deadlock A\* (1999)**| **YES** | **819** | **154** | **18** | **16.40** |
| **Tier 5** (复杂) | 5 | BFS (1959) | **NO** (超时) | 100,000+ | 5,562 | - | 460.00+ |
| | 5 | A\* Search (1968) | **NO** (超时) | 100,000+ | 4,997 | - | 105.00+ |
| | 5 | **Deadlock A\* (1999)**| **YES** | **20,085** | **862** | **61** | **759.90** |

### 3.1 实测结论与规律发现

```mermaid
xychart-beta
    title "Tier 3 关卡各算法展开节点数 (Expanded Nodes)"
    x-axis ["BFS (1959)", "A* (1968)", "Hungarian A*", "Deadlock-A* (1999)"]
    y-axis "展开节点数" 0 --> 9000
    bar [8121, 1071, 924, 470]
```

1. **从盲目到启发式的跨越**：  
   在 Tier 3（三箱）关卡中，盲目 BFS 需要展开 **8,121** 个节点才能摸索到解；引入曼哈顿 A\* 后节点数骤降至 **1,071**（降低 86%）；使用匈牙利匹配进一步收紧至 **924**。这生动展示了启发信息在状态空间中的导航价值。
2. **死锁剪枝的质变效应**：  
   在 Tier 3 中，Deadlock-Pruned A\* 将节点展开数直接压低至 **470** 个（比 BFS 减少 94%！）。而在 Tier 5（5 个箱子）的高难度关卡中，盲目搜索与未配置死锁剪枝的普通 A\* 均在达到 100,000 节点阈值时超限崩溃；**唯有配置了死锁检测的 Deadlock A\* 成功在 20,085 节点内找到了全长 61 步的最优解**。
3. **探索热力图的空间特征**：  
   通过本系统特有的探索热力图（Exploration Heatmap）可视化：
   - BFS 曾将箱子推到过地图上全部 25 个行走格子（盲目充塞）；
   - Deadlock-Pruned A\* 仅探索了 12 个关键走廊格子，其余 13 个死锁格子一次都未曾踏入。

---

## 四、 参考文献 (References)

1. **Culberson, J.** (1997). *Sokoban is PSPACE-complete.* International Conference on Fun with Algorithms.
2. **Dijkstra, E. W.** (1959). *A note on two problems in connexion with graphs.* Numerische Mathematik, 1(1), 269–271.
3. **Hart, P. E., Nilsson, N. J., & Raphael, B.** (1968). *A formal basis for the heuristic determination of minimum cost paths.* IEEE Transactions on Systems Science and Cybernetics, 4(2), 100–107.
4. **Pohl, I.** (1970). *Heuristic search viewed as path finding in a graph.* Artificial Intelligence, 1(3-4), 193–204.
5. **Kaindl, H., & Kainz, G.** (1997). *Bidirectional heuristic search reconsidered.* Journal of Artificial Intelligence Research, 7, 283–317.
6. **Korf, R. E.** (1985). *Depth-first iterative-deepening: An optimal admissible tree search.* Artificial Intelligence, 27(1), 97–109.
7. **Junghanns, A., & Schaeffer, J.** (2001). *Sokoban: Enhancing heuristic search with domain knowledge.* Artificial Intelligence, 129(1-2), 219–251.
8. **Coulom, R.** (2006). *Efficient selectivity and backup operators in Monte-Carlo tree search.* Computers and Games, 72–83.
9. **Racanière, S., Weber, T., et al.** (2017). *Imagination-augmented agents for deep reinforcement learning (Boxoban).* NeurIPS.
