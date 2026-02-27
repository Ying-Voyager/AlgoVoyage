# 🏆 2025 CUMCM Problem C: NIPT Timing & Fetal Abnormality Detection
**—— 基于多因素建模与风险优化的无创产前检测策略研究**

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Status](https://img.shields.io/badge/Status-Completed-success.svg)
![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)

## 📝 项目简介

本项目包含我们团队参与 2025 年全国大学生数学建模竞赛 (CUMCM) C题的完整数据分析、统计建模与机器学习分类代码。

无创产前检测 (NIPT) 的准确性高度依赖于胎儿游离 DNA (染色体浓度) 的达标情况。本项目针对 NIPT 的时点选择与异常判定问题，构建了一套从**多因素非线性归因**、**风险反馈时点优化**到**多模型融合异常分类**的完整算法框架，旨在提升临床检测的准确性并降低潜在漏检风险。

---

## 💡 核心模型与创新点

本项目主要包含以下三个维度的核心工作：

1. **基于 GAMM 的非线性特征解析 (Model I)**：
   - 摒弃了传统的多元线性回归 (OLS)，采用广义加性混合模型 (GAMM) 深度解析胎儿 Y 染色体浓度与孕妇孕周、BMI 之间的复杂非线性交互效应。
   - 准确量化了孕周的主效应与 BMI 的负相关衰减，并进行了严格的显著性检验。
2. **基于 K-means 与动态规划的时点风险优化 (Model II)**：
   - 构建了融合 K-means 聚类与风险反馈机制的检测时点优化模型。
   - 通过量化测序失败、检测过早/过晚带来的临床风险，成功求解出兼顾成功率与干预窗口的最佳检测时点（集中在 12.0-12.4 周）。
3. **基于多模型融合 (Ensemble) 的女胎异常判定 (Model III)**：
   - 针对 21号、18号和13号染色体非整倍体异常，提取 Z值、GC 含量与读段数等核心特征。
   - 综合训练并对比了 LightGBM、随机森林 (Random Forest) 与高斯朴素贝叶斯 (Gaussian NB) 分类器。
   - 构建了强鲁棒性的融合模型，实现了对女胎异常结果的高精度判定。

---

## 📂 核心文件结构

本模块代码已按照业务逻辑与题目顺序进行了全英文重构与模块化拆分：

* **Q1_*.py (数据预处理与特征显著性检验)**
  * `Q1_Data_Preprocessing.py`
  * `Q1_OLS_vs_GAM_Fitting_Comparison.py`
  * `Q1_Y_Chromosome_Correlation_Matrix.py`
  * `Q1_Feature_Significance_Test.py`
  * `Q1_Sequencing_Quality_Distribution.py`
* **Q2_*.py (风险优化与最佳时点聚类)**
  * `Q2_KMeans_Clustering.py`
  * `Q2_Ensemble_Model.py`
* **Q3_*.py (进阶模型与基准对比)**
  * `Q3_LightGBM_Model.py`
  * `Q3_Parallel_Coordinates_Plot.py`
  * `Q3_Four_Models_Comparison.py`
* **Q4_*.py (多维特征分类与临床诊断可视化)**
  * `Q4_Gaussian_NB_Confusion_Matrix.py`
  * `Q4_Random_Forest_Confusion_Matrices.py`
  * `Q4_Disease_Prob_vs_GC_Variation.py`
  * `Q4_LDA_Variation_vs_Disease_Probability.py`
  * `Q4_Lollipop_Chart.py` / `Q4_Bubble_Chart.py`

---

## 📦 资料下载 (Data & Paper)

为了保持代码仓库的纯净与轻量，**原始题目说明、数十兆的临床数据集以及最终提交的成品论文**均未上传至 GitHub，请通过以下百度网盘链接获取完整资料包：

- 🔗 **百度网盘链接**: [https://pan.baidu.com/s/19rs5HwJQQKFX36t3zt_JMg?pwd=ADDD]
- 🔑 **提取码**: [提取码: ADDD]

**⚠️ 数据放置指南：**
下载并解压网盘资料后，请务必将原始数据文件（通常为 `.xlsx` 或 `.csv` 格式）直接放置在本目录（即 `competitions/CUMCM_2025/`）下。
> *注：外层的 `.gitignore` 已配置拦截规则，本地运行时的 Excel 表格和 csv 数据不会被误推送到云端。*

---

## 🚀 快速开始 (Quick Start)

### 1. 环境配置
请确保你已经激活了项目根目录下的虚拟环境，并安装了依赖：
```bash
pip install -r ../../requirements.txt
```

### 2. 运行代码

数据放置正确后，你可以直接运行任意子脚本复现论文中的图表。例如，运行第二问的集成模型仿真：

```bash
python Q2_Ensemble_Model.py
```

各模块推荐运行顺序如下（存在数据依赖关系时需按序执行）：

```bash
# 第一问：数据预处理与特征显著性检验
python Q1_Data_Preprocessing.py
python Q1_OLS_vs_GAM_Fitting_Comparison.py
python Q1_Y_Chromosome_Correlation_Matrix.py
python Q1_Feature_Significance_Test.py
python Q1_Sequencing_Quality_Distribution.py

# 第二问：风险优化与最佳检测时点聚类
python Q2_KMeans_Clustering.py
python Q2_Ensemble_Model.py

# 第三问：进阶模型与基准对比
python Q3_LightGBM_Model.py
python Q3_Four_Models_Comparison.py
python Q3_Parallel_Coordinates_Plot.py

# 第四问：多维特征分类与临床诊断可视化
python Q4_Gaussian_NB_Confusion_Matrix.py
python Q4_Random_Forest_Confusion_Matrices.py
python Q4_Disease_Prob_vs_GC_Variation.py
python Q4_LDA_Variation_vs_Disease_Probability.py
python Q4_Lollipop_Chart.py
python Q4_Bubble_Chart.py
```

> **注意**：`Q1_Data_Preprocessing.py` 会生成预处理后的数据文件，建议先运行它再进行后续步骤。

---

## 👥 作者与致谢

- 💻 **编程实现**: Ying Qichi
- 🧮 **建模与分析**: Zhao Yao
- 📝 **论文撰写**: Li Zhicong
- 🏷️ **队伍编号**: Team 2025CUMCM

如有问题可随时联系，禁止二次销售，版权归我方所有。

---

## 📄 许可证

本项目采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh) 协议授权。

你可以自由地**分享**和**改编**本项目内容，但须遵守以下条件：
- **署名**：必须注明原作者（Team 2025CUMCM）及出处
- **非商业性使用**：禁止将本项目内容用于任何商业目的，包括但不限于销售、代写、卖课等行为

© 2025 Team 2025CUMCM