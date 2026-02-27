# 🏆 2026 MCM Problem C: Beyond the Popularity Trap 
**—— 基于 LDSS 模型的《与星共舞》方差失衡与价值重构分析**

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Status](https://img.shields.io/badge/Status-Results_Pending-orange.svg)
![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)

## 📝 项目简介

本项目包含我们团队参与 2026 年美国大学生数学建模竞赛 (MCM) C题 (Data With The Stars) 的完整数据分析、数学建模与数字孪生仿真代码。

针对《与星共舞》节目中“高人气低技术”选手的晋级争议，本研究揭示了其根本原因在于**方差失衡 (Variance Imbalance)**。为此，我们通过历史数据逆向工程与机制重构，提出了一套兼顾商业娱乐性与竞技公平性的全新评分框架。

---

## 💡 核心模型与创新点

本项目主要包含以下四个维度的核心工作：

1. **基于 Zipf 定律的蒙特卡洛逆向反演 (Model I)**：
   - 针对缺失的粉丝投票数据，构建了基于 Zipf 定律的蒙特卡洛反演模型。
   - 通过 10,000 次随机仿真重构历史票数分布，证实了粉丝投票的“赢家通吃”幂律分布在数学上完全淹没了评委打分的低方差。
2. **反事实仿真与规则交换测试 (Model II)**：
   - 对“秩和法 (Rank-Sum)”与“百分比法 (Percentage)”进行了反事实仿真。
   - 证明百分比法会产生**“巨星免疫 (Superstar Immunity)”**效应，让高流量选手仅靠 25% 的选票即可建立绝对防御。
3. **双轨 OLS 回归与归因分析 (Model III)**：
   - 构建双轨回归模型以区分评委与观众的评价驱动力。
   - 发现了**年龄悖论 (Age Paradox)**（评委对生理衰退严格扣分，每 10 年降 0.09 分，而观众通过“怀旧溢价”进行补偿）。
   - 证实了**顶级舞伴效应 (Top Partner Effect)**（顶级舞伴能显著提升技术分）。
4. **全生命周期动态评分系统 (LDSS) (Model IV)**：
   - **Tanh 饱和评分**：引入双曲正切函数对粉丝选票设置“软上限”，物理隔绝人气溢出。
   - **动态权重策略与三阶段淘汰制**：前期 60/40 权重保护流量，决赛期 40/60 权重回归专业。
   - 采用 12 个原型代理进行**数字孪生 (Digital Twin)** 仿真，成功验证了新赛制在保护早期商业参与度的同时，能有效在四强前淘汰技术薄弱的“流量王”。

---

## 📂 核心文件结构

本仓库严格遵循大厂工程化规范，核心代码按照题目 (Q1-Q4) 进行了模块化拆分：

* **Q1_*.py (逆向工程与分布重建)**
  * `Q1_Early_Season_Analysis.py` / `Q1_Longitudinal_Analysis_S3_S27.py`
  * `Q1_Season_28_Analysis.py` / `Q1_Sensitivity_Analysis.py`
* **Q2_*.py (投票机制反事实仿真)**
  * `Q2_Comprehensive_Trajectory_Analysis.py` / `Q2_Counterfactual_Analysis.py`
  * `Q2_Fan_Power_Leverage_Analysis.py` / `Q2_Judges_Save_Impact_Analysis.py`
* **Q3_*.py (双轨归因与可视化)**
  * `Q3_Dual_Track_Factor_Analysis.py` / `Q3_Age_Paradox_Visualization.py`
* **Q4_*.py (LDSS 模型与数字孪生)**
  * `Q4_Tanh_Saturation_Scoring.py` / `Q4_Digital_Twin_Simulation.py`
  * `Q4_LDSS_Season_Simulation.py` / `Q4_Parameter_Sensitivity_Analysis.py`

---

## 📦 资料下载 (Data & Paper)

为了保持代码仓库的纯净与轻量，**原始题目说明、比赛数据集以及最终提交的完整 PDF 论文**均未上传至 GitHub，请通过以下百度网盘链接获取完整资料包：

- 🔗 **百度网盘链接**: [https://pan.baidu.com/s/1Gq6gMwxJ3_eD_1IG_S90Lw?pwd=ADDD]
- 🔑 **提取码**: [提取码: ADDD]

**⚠️ 数据放置指南 (非常重要)：**
下载并解压网盘资料后，请务必将原始数据文件（如 `2026_MCM_Problem_C_Data.csv`）直接放置在本项目的当前目录下（即 `competitions/MCM_2026/` 文件夹内）。
> *注：外层的 `.gitignore` 已配置拦截规则，本地运行时的 `.csv` 数据不会被误推送到云端。*

---

## 🚀 快速开始 (Quick Start)

### 1. 环境配置
请确保你已经安装了 Python 3.12+ 环境，并在终端中运行以下命令，一键安装项目根目录下的依赖清单：
```bash
pip install -r ../../requirements.txt
```

### 2. 运行代码

数据放置正确后，你可以直接运行任意子脚本复现论文中的图表。例如，运行第四问的 Tanh 饱和评分仿真：

```bash
python Q4_Tanh_Saturation_Scoring.py
```

各模块推荐运行顺序如下（存在数据依赖关系时需按序执行）：

```bash
# 第一问：逆向工程粉丝投票分布
python Q1_Early_Season_Analysis.py
python Q1_Longitudinal_Analysis_S3_S27.py
python Q1_Season_28_Analysis.py
python Q1_Sensitivity_Analysis.py

# 第二问：投票机制反事实仿真
python Q2_Voting_Methods_Comparison.py
python Q2_Counterfactual_Analysis.py
python Q2_Comprehensive_Trajectory_Analysis.py
python Q2_Judges_Save_Impact_Analysis.py
python Q2_Sensitivity_Analysis.py

# 第三问：双轨归因分析（需先运行 Factor Analysis 生成中间数据）
python Q3_Dual_Track_Factor_Analysis.py
python Q3_Age_Paradox_Visualization.py
python Q3_Factor_Data_Inspection.py

# 第四问：LDSS 模型与数字孪生仿真
python Q4_Tanh_Saturation_Scoring.py
python Q4_Digital_Twin_Simulation.py
python Q4_LDSS_Season_Simulation.py
python Q4_Parameter_Sensitivity_Analysis.py
```

> **注意**：`Q3_Age_Paradox_Visualization.py` 依赖 `Q3_Dual_Track_Factor_Analysis.py` 生成的 `Factor_Analysis_Data.csv`，请务必先运行后者。

---

## 👥 作者与致谢

- 💻 **编程实现**: Ying Qichi
- 🧮 **建模与分析**: Zhao Yao
- 📝 **论文撰写**: Li Zhicong
- 🏷️ **队伍编号**: Team 2602906

如有问题可随时联系，禁止二次销售，版权归我方所有。

---

## 📄 许可证

本项目采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh) 协议授权。

你可以自由地**分享**和**改编**本项目内容，但须遵守以下条件：
- **署名**：必须注明原作者（Team 2602906）及出处
- **非商业性使用**：禁止将本项目内容用于任何商业目的，包括但不限于销售、代写、卖课等行为

© 2026 Team 2602906