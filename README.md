# PySokoban: The Chronicle of AI Search Algorithms (1950s - Present)
### 《推箱子里的 AI 搜索编年史：从图灵时代到现代树搜索》

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Engine](https://img.shields.io/badge/Engine-Pygame--CE%202.5+-green.svg)](https://pyga.me/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **“推箱子（Sokoban）不仅是一个经典的智力游戏，更是人工智能与组合优化历史上最纯粹、最严苛的试炼场。”**  
> 本项目以推箱子这一已被数学证明为 **PSPACE-Complete** 的复杂系统为载体，系统性复现、对比并可视化计算机科学史上从 1950 年代朴素图遍历，到启发式搜索突破、领域死锁智能、双向搜索、直至现代蒙特卡洛树搜索（MCTS）的**算法演进编年史**。

---

## 🌟 为什么选择推箱子作为 AI 搜索的试金石？

1. **组合状态爆炸（Combinatorial State Explosion）**：  
   与简单的迷宫不同，推箱子每推一次箱子都会永久性改变整个环境的拓扑结构。状态空间复杂度随着箱子数量和地图尺寸呈指数级增长（$O(b^d)$）。
2. **单向不可逆坍缩（Irreversible Deadlocks）**：  
   推箱子只能“推”不能“拉”。任何一次轻率的移动都可能将箱子推入死角（Corner Deadlock）或形成互锁方块（Freeze Deadlock），导致搜索空间陷入无穷无尽的死局。
3. **知识与搜索的世纪辩证（Search vs. Knowledge）**：  
   在推箱子中，算力的单纯堆叠（盲目搜索）在第 3 关就会面临内存溢出（OOM）。只有引入**可接受启发式（Admissible Heuristics，如匈牙利二分图最优匹配）**和**领域死锁剪枝（Rolling Stone 范式）**，才能实现数个数量级的搜索剪枝。

---

## 🏛️ AI 搜索算法编年史全景（The Algorithm Pantheon）

本项目将经典算法严格解耦并统一纳入统一的诊断评估体系（`SearchMetrics`），真实还原各时期的代表性工作：

| 历史时期 | 算法名称 | 提出者 / 标志性文献 | 算法特性 | 推箱子场景下的理论意义与实测表现 |
| :--- | :--- | :--- | :--- | :--- |
| **1950** | **DFS** (深度优先搜索) | Classical Graph Theory | 盲目 / 不保证最优 | 极度盲目，极易在无死锁检测的环路中深陷，产生奇长无比的解。 |
| **1959** | **BFS** (广度优先搜索) | E. F. Moore / E. W. Dijkstra | 盲目 / **最优解保证** | 严格按步数层级向外扩张，能够找到最短步数解；但在 3 个箱子以上立即遭遇状态爆炸。 |
| **1960** | **GBFS** (贪心最佳优先) | Early AI Heuristics | 启发式 / 不保证最优 | 仅依据 $h(n)$ 贪心逼近目标。速度极快，但容易掉入局部陷阱而死循环。 |
| **1968** | **A\* Search** (曼哈顿距离) | P. Hart, N. Nilsson, B. Raphael | 启发式 / **最优解保证** | 开创性结合已花费代价 $g(n)$ 与可接受下界 $h(n)$，搜索呈现明显的指向性。 |
| **1968** | **A\* Search** (匈牙利匹配) | H. W. Kuhn (1955) / Munkres | 启发式 / **最优解保证** | 利用二分图最小权最优匹配求解箱子与目标的全局最优对应，提供严格紧致的下界。 |
| **1970** | **Weighted A\*** ($w=1.5$) | I. Pohl | 次优启发式 ($\epsilon$-admissible) | 放宽最优解保证，以解长度微小的增长换取搜索展开节点数的大幅缩减。 |
| **1971** | **Bidirectional Search** | I. Pohl (1971) / Kaindl (1997) | 双向搜索 / **最优解保证** | 正向推箱子与逆向“拉箱子”双向对进，理论上将搜索深度减半（$b^{d/2} + b^{d/2} \ll b^d$）。 |
| **1985** | **IDS** (迭代加深搜索) | R. Korf | 盲目 / **空间线性最优** | 结合 BFS 的最优性与 DFS 的 $O(bd)$ 线性空间占用，通过牺牲时间重算换取空间可行性。 |
| **1985** | **IDA\*** (迭代加深 A\*) | R. Korf | 启发式 / **空间线性最优** | 内存受限系统的救星，通过动态抬升 $f$ 阈值替代优先队列，消除开放表（Open Set）内存爆炸。 |
| **1999** | **Deadlock-Pruned A\*** | A. Junghanns, J. Schaeffer | 领域知识增强 / **最优解保证** | **Rolling Stone 范式**：结合静态逆向拉力死区预计算与 2x2 冻结死锁检测，剪枝率达 70%~99%！ |
| **2006** | **MCTS** (蒙特卡洛树搜索) | R. Coulom / Kocsis & Szepesvári | 随机采样 / 渐近收敛 | 引入 UCB1 平衡探索与利用，无需人工显式设计启发式即可自主探索路径。 |

---

## 📊 阶梯基准评测矩阵（Benchmark Ladder Results）

运行 `pysokoban bench --levels levels/02_benchmark` 得到的真实对比数据：

```text
                     PySokoban Historical Benchmark Matrix                     
+--------------------+-------+-----------------------+------+--------+-------+----------+---------+-----------+
| Level              | Boxes | Algorithm             | Year | Solved | Steps | Expanded | PeakMem | Time (ms) |
+--------------------+-------+-----------------------+------+--------+-------+----------+---------+-----------+
| tier1_micro_1box   |     1 | BFS (广度优先)        | 1959 |  YES   |     3 |        3 |       1 |      0.04 |
| tier1_micro_1box   |     1 | A* Search             | 1968 |  YES   |     3 |        4 |       2 |      0.04 |
| tier1_micro_1box   |     1 | Deadlock-Pruned A*    | 1999 |  YES   |     3 |        4 |       2 |      0.06 |
|--------------------+-------+-----------------------+------+--------+-------+----------+---------+-----------|
| tier2_dual_2box    |     2 | BFS (广度优先)        | 1959 |  YES   |    33 |      559 |      34 |      2.21 |
| tier2_dual_2box    |     2 | A* Search             | 1968 |  YES   |    33 |      540 |      41 |      3.58 |
| tier2_dual_2box    |     2 | Deadlock-Pruned A*    | 1999 |  YES   |    33 |      152 |      13 |      2.08 |
|--------------------+-------+-----------------------+------+--------+-------+----------+---------+-----------|
| tier3_trio_3box    |     3 | BFS (广度优先)        | 1959 |  YES   |    14 |    8,121 |   3,996 |     42.10 |
| tier3_trio_3box    |     3 | A* Search             | 1968 |  YES   |    14 |    1,071 |     932 |     10.50 |
| tier3_trio_3box    |     3 | Deadlock-Pruned A*    | 1999 |  YES   |    14 |      470 |     250 |     10.10 |
|--------------------+-------+-----------------------+------+--------+-------+----------+---------+-----------|
| tier4_classic_4box |     4 | BFS (广度优先)        | 1959 |  YES   |    18 |    2,100 |     260 |      8.87 |
| tier4_classic_4box |     4 | A* (Hungarian)        | 1968 |  YES   |    18 |    1,420 |     303 |     19.20 |
| tier4_classic_4box |     4 | Deadlock-Pruned A*    | 1999 |  YES   |    18 |      819 |     154 |     16.40 |
|--------------------+-------+-----------------------+------+--------+-------+----------+---------+-----------|
| tier5_complex_5box |     5 | BFS (广度优先)        | 1959 |   NO   |     - | 100,000+ |   5,562 |   超时OOM |
| tier5_complex_5box |     5 | A* Search             | 1968 |   NO   |     - | 100,000+ |   4,997 |   超时OOM |
| tier5_complex_5box |     5 | Deadlock-Pruned A*    | 1999 |  YES   |    61 |   20,085 |     862 |    458.20 |
+--------------------+-------+-----------------------+------+--------+-------+----------+---------+-----------+
```

> **核心结论观察**：
> 1. **在 1~2 箱阶段**：BFS 与 A\* 耗时处于同级别；但 Deadlock-Pruned A\* 已将展开节点从 559 削减到 152（减少 73%）。
> 2. **在 3 箱阶段**：BFS 展开节点数暴增至 8,121 节点；A\* 凭借曼哈顿启发式压缩至 1,071 节点；而 Deadlock-Pruned A\* 仅需 470 节点（提升 17 倍效率）。
> 3. **在 5 箱阶段**：朴素 BFS 与 A\* 搜索空间彻底失控（超过 100,000 节点上限失败）；**仅有引入死锁检测的 Deadlock-Pruned A\* 成功在 20,085 节点内求解**。充分佐证了 Junghanns & Schaeffer 提出的“无死锁检测则无推箱子求解”的历史论断。

---

## 🚀 快速上手 (Quick Start)

### 1. 环境安装（现代化 PEP 621）
推荐使用轻量极速包管理工具 [`uv`](https://github.com/astral-sh/uv) 或标准 `pip`：

```bash
# 克隆仓库
git clone https://github.com/SunnyLinYY/pysokoban.git
cd pysokoban

# 使用 pip 安装可编辑包及依赖
pip install -e ".[dev]"
```

### 2. 命令行体验 (CLI Arsenal)

```bash
# 1. 打印完整的历史算法编年史
pysokoban list-algorithms

# 2. 对阶梯基准运行全套算法横向评测
pysokoban bench --levels levels/02_benchmark

# 3. 指定算法求解特定关卡并在终端 ASCII 动态回放
pysokoban solve --level levels/02_benchmark/tier3_trio_3box.txt --algo deadlock-astar --animate

# 4. 启动交互式 Pygame 可视化游戏
pysokoban play --level levels/02_benchmark/tier2_dual_2box.txt
```

---

## 🎮 交互式游戏与教学可视化功能

启动 GUI 后，系统提供开箱即用的沉浸式教学与游玩体验：

| 快捷键 | 功能说明 | 教学展示意义 |
| :--- | :--- | :--- |
| **`↑` `↓` `←` `→`** | 控制玩家移动与推箱子 | 基础手动交互与关卡体验 |
| **`Z` / `U`** | **撤销 (Undo)** | 支持无限步回退，推箱子练习核心机制 |
| **`Y`** | **重做 (Redo)** | 前进历史操作 |
| **`R`** | 重置关卡 (Reset) | 恢复至初始状态 |
| **`1` ~ `9`** | **切换 AI 算法** | 自由切换 1950 DFS、1959 BFS、1968 A\*、1999 Deadlock A\* 等 |
| **`S`** | **触发 AI 求解与回放** | 实时调用选中 AI 求解当前局面，并平滑动画播放求解路径 |
| **`F2`** | **探索热力图 (Exploration Heatmap)** | 开启后，在地图上**以半透明橙红色覆盖层高亮显示 AI 曾探索过的所有箱子位置**，直观对比盲目搜索“全图乱窜”与启发式搜索“精准制导”的视觉差异！ |
| **`Space`** | 暂停 / 继续回放 | 随时停下观察当前局势与状态 |
| **`+` / `-`** | 调整回放速度 (FPS) | 0.5x ~ 5x 速度自由缩放 |

---

## 📁 模块解耦与目录架构

项目遵循现代软件工程规范，将**纯数学领域模型**与**渲染/交互**彻底隔离：

```text
pysokoban/
├── src/pysokoban/
│   ├── core/                    # 纯 Python 领域逻辑（无 GUI 依赖，支持高并发无头测试）
│   │   ├── enums.py             # Action, Tile, Direction 定义
│   │   ├── state.py             # 具名槽位不可变哈希状态 SokobanState
│   │   ├── board.py             # 地图加载、状态转移与 ASCII 渲染 Board
│   │   └── deadlock.py          # 静态逆向拉力死区、角落死锁与 2x2 冻结死锁检测
│   ├── algorithms/              # 历史算法编年史套件
│   │   ├── base.py              # SearchAlgorithm 基类、SearchNode、SearchMetrics 诊断协议
│   │   ├── uninformed.py        # 1950s~1980s 盲目搜索 (BFS, DFS, IDS)
│   │   ├── informed.py          # 1960s~1980s 启发式搜索 (GBFS, A*, Weighted A*, IDA*)
│   │   ├── pruning.py           # 1990s 领域死锁感知 (Deadlock-Pruned A* / Rolling Stone)
│   │   ├── bidirectional.py     # 1970s~2000s 双向搜索与逆向拉箱子动力学 (BidirectionalSearch)
│   │   └── mcts.py              # 2000s 蒙特卡洛树搜索 (MonteCarloTreeSearch)
│   ├── heuristics/              # 启发式函数库 (曼哈顿距离, 匈牙利二分匹配 Kuhn-Munkres)
│   ├── visualizer/              # 现代图形界面 (SokobanGUI: 撤销重做, 调速回放, 探索热力图)
│   └── cli.py                   # 模块化命令行入口 (bench, solve, play, list-algorithms)
├── levels/
│   ├── 01_tutorial/             # 死锁与算法对比专题微关卡
│   ├── 02_benchmark/            # 1~5 箱递进梯度标准基准集 (Microban / XSokoban 精选)
│   └── *.txt                    # 内置的 20 个原有关卡
├── scripts/
│   └── fetch_benchmarks.py      # 一键拉取完整学术数据集 (Microban 155 关)
├── tests/                       # 自动化测试套件 (17 项单元与集成测试，覆盖所有算法)
├── pyproject.toml               # PEP 621 现代工程配置 (ruff + pytest + hatchling)
└── main.py                      # 统一快速启动入口
```

---

## 🧪 自动化测试与代码质量

仓库配备全面的单元与集成测试，使用 `pytest` 自动检验每一个算法在标准关卡上的完备性与正确性：

```bash
# 运行全部测试集
pytest

# 运行代码规范检查与格式化
ruff check src tests
ruff format src tests
```

---

## 📜 参考文献 (Selected References)

1. **Dijkstra, E. W.** (1959). *A note on two problems in connexion with graphs.* Numerische Mathematik, 1(1), 269–271.
2. **Hart, P. E., Nilsson, N. J., & Raphael, B.** (1968). *A formal basis for the heuristic determination of minimum cost paths.* IEEE Transactions on Systems Science and Cybernetics, 4(2), 100–107.
3. **Pohl, I.** (1970). *Heuristic search viewed as path finding in a graph.* Artificial Intelligence, 1(3-4), 193–204.
4. **Pohl, I.** (1971). *Bi-directional search.* Machine Intelligence, 6, 127–140.
5. **Korf, R. E.** (1985). *Depth-first iterative-deepening: An optimal admissible tree search.* Artificial Intelligence, 27(1), 97–109.
6. **Culberson, J.** (1997). *Sokoban is PSPACE-complete.* International Conference on Fun with Algorithms.
7. **Junghanns, A., & Schaeffer, J.** (2001). *Sokoban: Enhancing heuristic search with domain knowledge.* Artificial Intelligence, 129(1-2), 219–251.
8. **Coulom, R.** (2006). *Efficient selectivity and backup operators in Monte-Carlo tree search.* Computers and Games, 72–83.
9. **Racanière, S., Weber, T., et al.** (2017). *Imagination-augmented agents for deep reinforcement learning (Boxoban).* NeurIPS.

---

## 📄 License
本项目基于 [MIT License](LICENSE) 开源。欢迎学者、学生与开发者自由学习、二次开发与引用。
