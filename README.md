# 🚀 AlgoVoyage: 个人核心算法与工程框架

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Architecture](https://img.shields.io/badge/Architecture-Modular-success.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

## 📖 项目简介

**AlgoVoyage** 是用于沉淀个人核心算法、存放顶级数学建模竞赛（如 MCM/ICM）代码以及学术科研项目仿真的综合性工程库。

本项目摒弃了传统的“面条式”脚本编写习惯，致力于打造一个**高内聚、低耦合**的算法生态。通过严格的面向对象（OOP）设计与模块化封装，实现复杂算法的高效复用、快速迭代与可重复验证，致力于在自动驾驶、具身智能与先进制造等领域探索算法工程化的最佳实践。

---

## 📂 目录结构说明

本框架采用标准的工业级项目目录规范：

* **`core/`**：**核心算法引擎**。沉淀经过验证的底层算法模块（如前沿时序预测模型、复杂动力学仿真逻辑、通用控制算法等），作为独立组件供其他模块调用。
* **`utils/`**：**通用工具箱**。包含高频使用的辅助轮子（如统一的数据 I/O 接口、跨平台路径动态解析、Matplotlib 科研级可视化与 LaTeX 渲染引擎等）。
* **`projects/`**：**学术科研与工程实践**。收录各项科研课题与工程落地的算法实现（覆盖智能装备、机构运动学仿真、数据驱动的工艺分析等方向）。
* **`competitions/`**：**竞赛存档**。历次大型学科竞赛（含美赛 MCM 等）的实战代码库，每个赛事均保持独立的虚拟环境配置与数据流管控。

---

## 🛠️ 技术栈与核心依赖

本项目致力于构建纯净、高效的计算环境：

* **编程语言**: `Python` (>= 3.8)
* **核心科学计算**: `numpy`, `scipy`, `pandas`
* **科研级可视化**: `matplotlib`, `seaborn` (默认开启 LaTeX 级学术渲染)
* **机器学习/深度学习**: *(未来将随框架扩展逐步引入对应的生态库)*

---

## ⚙️ 开发与工程规范

为保证代码库的长效可维护性，本项目严格遵循以下规范：

1. **范式标准**: 核心算法与业务逻辑均采用**面向对象 (OOP)** 进行封装，确保类的单一职责原则。
2. **环境隔离**: 坚持“代码进 Git，数据与环境留本地”的铁律，各子项目依赖独立 `.venv`，并通过 `requirements.txt` 进行版本锁定。
3. **路径鲁棒性**: 坚决杜绝硬编码的绝对路径，全面采用基于 `pathlib` 或 `os.path` 的动态相对路径，确保代码在任何操作系统的多端 Clone 均可一键运行。
4. **命名与注释**: 强制要求纯英文、下划线风格的文件与目录命名；代码内部保留详尽的中文/英文技术注释与 Docstring。

---

## 🚦 快速开始 (Quick Start)

### 1. 克隆仓库
```bash
git clone https://github.com/Ying-Voyager/AlgoVoyage.git
cd AlgoVoyage
```

### 2. 环境配置

推荐使用虚拟环境进行依赖隔离：

```bash
# 创建并激活虚拟环境
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 激活你的虚拟环境后执行：
pip install -r requirements.txt
```

### 3. 调用示例

框架成熟后，你可以直接在独立脚本中引入 `core` 或 `utils` 中的模块（以下为规划中的接口示例）：

```python
# 示例：引入学术可视化工具（utils 模块开发中）
# from utils.visualization import plot_academic_style

# 示例：引入时序预测基类（core 模块开发中）
# from core.time_series import BasePredictor

# 你的业务代码...
```

若要复现某个竞赛子项目的完整结果，进入对应子目录后直接运行目标脚本即可，例如：

```bash
cd competitions/MCM_2026
python Q4_Tanh_Saturation_Scoring.py
```

> 各子项目的详细运行说明请参阅其目录下的独立 `README.md`。

---

## 📊 项目路线图 (Roadmap)

- [x] 建立模块化工程框架（`core` / `utils` / `projects` / `competitions`）
- [x] 完成 MCM 2026 全流程建模与仿真代码


---

*"在算法的星辰大海中，保持严谨，持续远航。" —— AlgoVoyage*

---

## 📄 许可证

MIT License © 2026 AlgoVoyage