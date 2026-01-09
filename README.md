# Sokoban Solver Pro (推箱子 AI 求解器)

**Sokoban Solver Pro** 是一款集成了高性能 C++ 求解引擎与现代化 Python 图形界面的自动推箱子工具。它能够针对不同的关卡，自动寻找最优或可行的解法，并以直观的动画形式进行演示。

---

## ✨ 功能特点

*   **双引擎驱动**：采用 C++17 编写核心搜索算法，确保极致的计算速度；Python Tkinter 编写图形界面，提供清爽简洁的操作体验。
*   **三种 AI 算法**：
    *   **A\* (Optimal)**：启发式搜索，通常能在最短时间内找到最优路径。
    *   **BFS (Breadth First)**：广度优先搜索，保证找到箱子推动次数最少的解。
    *   **DFS (Deep Search)**：深度优先搜索，探索极深层次的解空间。
*   **可视化控制**：支持自动播放解法动画、暂停、手动单步前进/后退、以及一键跳转起终点。
*   **简洁 UI**：清淡简洁的主题设计，支持地图自适应缩放。
*   **独立运行**：已打包为单文件 EXE（位于 `dist/` 目录），无需安装环境。

## 🚀 快速开始

1.  运行程序：双击 **`dist/SokobanSolverPro.exe`**。
2.  **选择地图**：点击 `...` 按钮选择一个地图文件（例如自带的 `automatic-sokoban-solver-master/box.txt`）。
3.  **算法配置**：选择想要使用的 AI 算法及内存限制。
4.  **开始计算**：点击 **"Calculate Solution"**。
5.  **观看演示**：计算完成后，点击下方控制栏的 **"Play"** 按钮观看自动演示。

## 🗺️ 地图文件格式 (box.txt)

你可以创建自己的 `.txt` 文件并按照以下字符编辑关卡：

| 字符 | 含义 |
| :--- | :--- |
| `#` | 墙壁 (Wall) |
| ` ` | 空地 (Floor) |
| `$` | 箱子 (Box) |
| `.` | 目标点 (Target) |
| `@` | 搬运工 (Player) |
| `*` | 在目标点上的箱子 (Box on Target) |
| `+` | 在目标点上的搬运工 (Player on Target) |

## 🧠 算法建议

*   **常规关卡**：首选 **A\***，计算效率最高。
*   **最少推动**：使用 **BFS**，寻找推动箱子次数最少的方案。
*   **内存管理**：对于超大规模地图，请适当调大界面上的 `Memory Limit`。

## 🛠️ 构建与开发

如果你想在本地进行二次开发或编译：

*   **C++ 编译**：使用 C++17 标准，例如 `g++ -std=c++17 -I include src/*.cpp -o sokoban_solver.exe`。
*   **Python 环境**：Python 3.10+，依赖项仅需 `tkinter`。
*   **打包**：使用 `pyinstaller`，参考命令：
    `pyinstaller --onefile --windowed --add-data "sokoban_solver.exe;." gui.py`

---
***Created with Dinana7mi by Gemini AI Assistant***
