# 推箱子游戏

## 概述

这个项目是使用Python和Pygame库实现的推箱子游戏、求解以及关卡生成。游戏包含多个关卡，可自定义图标样式，并包含一个日志系统来跟踪游戏活动。

## 功能

- **可自定义关卡**：玩家可以通过指定命令行参数来从任意关卡开始游戏。
- **图标样式**：可以选择不同的图标样式来显示游戏元素。
- **测试模式**：游戏可以在测试模式下运行，便于调试和开发。
- **日志记录**：将游戏活动记录到指定的日志文件中。

## 安装

1. **克隆仓库**

    ```sh
    git clone https://github.com/SunnyLinYY/pysokoban.git
    cd pysokoban
    ```

2. **安装依赖**

    安装默认python>=12的conda，然后运行：

    ```sh
    conda create -n pysokoban
    conda activate pysokoban
    pip install pygame scipy numpy
    ```

    如果还想进行结果数据处理和分析等操作还需要运行：

    ```sh
    pip install pandas tabulate matplotlib
    ```

3. **运行游戏**

    ```sh
    python main.py
    ```

    可以根据需要指定其他参数：

    ```sh
    python main.py --level 5 --icon-style image_v2 --log-file mylog.log
    ```

## 命令行参数

- `--test`: 在测试模式下运行游戏。
- `--level`: 指定起始关卡（默认为1）。
- `--log-file`: 指定日志文件名称（默认为`sokoban.log`）。
- `--icon-style`: 指定游戏元素的图标样式（默认为`images_v1`）。

## 游戏文件

### main.py

这是游戏的主要入口，处理命令行参数、日志设置和游戏初始化。

### ui

#### input_handler.py

这个模块处理用户输入。它定义了一个 `InputHandler` 类，用于处理键盘和鼠标事件，并将这些事件映射到相应的游戏动作。支持的事件包括开始游戏、重新开始、暂停、退出等。

- 处理键盘输入并映射到相应的游戏事件。
- 处理鼠标点击事件，并在点击特定按钮时触发相应事件。
- 记录用户的输入行为到日志。

#### display.py

这个模块负责游戏的显示和渲染。它定义了一个 `Display` 类，用于在不同的游戏状态下渲染游戏界面和菜单。包括开始菜单、主菜单、胜利菜单和游戏中的显示。

- 加载和显示游戏图标。
- 根据游戏状态渲染不同的界面。
- 显示游戏地图和元素。
- 处理不同菜单下的按钮点击事件。

### game

#### game.py

此文件包含游戏的主要逻辑和流程控制。它管理游戏的状态、处理用户输入、渲染游戏地图，并与AI模块进行交互。

#### problem.py

此文件定义了推箱子问题的抽象表示，包括初始状态、可能的动作、结果状态、目标测试和启发式函数。`SokobanProblem`类继承自 `HeuristicSearchProblem`，实现了特定于推箱子问题的方法。

#### map.py

此文件定义了游戏地图的表示和操作，包括地图加载、玩家和箱子的位置、瓦片类型的判断、箱子的移动和死锁检测。

### sealgo

这里面包含了一些传统的搜索算法，以及定义搜索问题的抽象类。`SokobanProblem`就继承于其中的`HeuristicSearchProblem`。

### assets

该目录包含游戏资源文件，文件夹的名字可作为`--icon-style`的参数。

### utils

#### utils/scrawler.py

这个脚本从指定的URL抓取推箱子关卡并保存为文本文件。它将HTML内容中的图片转换为游戏关卡中使用的字符。

#### utils/data_analysis.py

这里是结果分析的时候用到的一些函数。

### levels

这是存放关卡文件的默认文件夹，名称为`level{lvl_num}.txt`

### logs

这是存放日志的默认文件夹。

## 许可证

该项目使用MIT许可证 - 请参见LICENSE文件以获取详细信息。

---

如有任何问题或需要进一步的帮助，请随时联系。