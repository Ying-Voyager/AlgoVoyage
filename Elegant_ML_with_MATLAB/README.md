# 优雅地使用 MATLAB 进行机器学习 — 课程作业合集

> **作者：** Ying Qichi
> **版本：** v1.0
> **日期：** 2024-06-10
> **工具：** MATLAB R2021b+
>
> 本仓库收录了课程《优雅地使用 MATLAB 进行机器学习》的全部课后作业与期中项目代码。
> 课程覆盖从 MATLAB 基础语法到机器学习核心算法的完整学习路径，每份作业均经过代码优化与规范注释。
> 开源目的是希望能为后来的学弟学妹们提供参考，缩短踩坑时间。

---

## 目录

1. [课程结构](#1-课程结构)
2. [作业列表与知识点](#2-作业列表与知识点)
3. [各作业详细说明](#3-各作业详细说明)
4. [期末项目：miRNA–疾病关联预测](#4-期末项目mirna疾病关联预测)
5. [代码规范与优化说明](#5-代码规范与优化说明)
6. [运行指南](#6-运行指南)
7. [依赖环境](#7-依赖环境)
8. [版权声明](#8-版权声明)

---

## 1. 课程结构

本课程分为两个阶段：

| 阶段 | 内容 | 对应作业 |
|------|------|----------|
| **基础阶段** | MATLAB 语法、流程控制、数据可视化 | HW01 ~ HW04 |
| **机器学习阶段** | 回归分析、正则化、分类与模型评估 | HW05 ~ HW07 + Final |

学习路径建议按照 HW01 → HW07 → Final 顺序逐步推进，每个阶段都建立在前一阶段的基础之上。

---

## 2. 作业列表与知识点

| 文件名 | 主题 | 核心知识点 |
|--------|------|-----------|
| `HW01_MATLAB_Scripting_Basics.m` | MATLAB 脚本基础 | 变量、运算、`input`/`disp`/`fprintf`、海伦公式、一元二次方程 |
| `HW02_Branching_Logic.m` | 分支逻辑控制 | `if/elseif/else`、`switch/case`、字符 ASCII 操作、成绩分级、商场折扣 |
| `HW03_Loop_Control_Structures.m` | 循环与控制结构 | `for`/`while` 循环、`break`、自定义函数、递归、百钱买百鸡、哥德巴赫猜想 |
| `HW04_Data_Visualization.m` | 数据可视化 | `plot`/`scatter`/`subplot`/`polarplot`/`fill`/`yyaxis`、`fzero` 求根 |
| `HW05_Regression_Analysis.m` | 回归分析 | 多项式拟合、`regress` 多元线性回归、设计矩阵构建 |
| `HW06_Regularized_Regression.m` | 正则化回归 | L2 岭回归 `ridge`、波士顿房价数据集、`randperm` 随机划分、MSE 评估 |
| `HW07_Classification_Model_Evaluation.m` | 分类与模型评估 | SVM（`fitcsvm`）、鸢尾花数据集、ROC 曲线绘制、AUC 计算（梯形法则） |
| `Final_Project_Machine_Learning.m` | 期末项目 | Katz 链路预测、异构网络、miRNA–疾病关联、ROC/AUC 综合评估 |

---

## 3. 各作业详细说明

### HW01 — MATLAB 脚本基础

**内容：** 5 道交互式计算题，覆盖 MATLAB 最基础的输入输出与数学运算。

| 题目 | 实现要点 |
|------|----------|
| 长方形周长与面积 | `input` 输入，基础四则运算 |
| 三角形周长与面积 | 三角不等式验证 + 海伦公式 $S = \sqrt{p(p-a)(p-b)(p-c)}$ |
| 一元二次方程求根 | 判别式 $\Delta = b^2-4ac$ 分三种情况讨论 |
| 球的体积与表面积 | $V = \frac{4}{3}\pi r^3$，$S = 4\pi r^2$ |
| 三数从小到大排列 | `sort` 函数一行求解 |

---

### HW02 — 分支逻辑控制

**内容：** 5 道 `if/switch` 分支题，训练条件判断与程序流的精准控制。

| 题目 | 实现要点 |
|------|----------|
| 四位数各位之和是否被 3 整除 | `while` + `mod` 逐位提取 |
| 字符后继输出（含 Z→A 循环处理） | `double(char)` ↔ ASCII 转换，边界特判 |
| 整数位数 + 逆序输出 | `num2str` + `fliplr` + `str2double` 字符串翻转法 |
| 百分制成绩等级判定 | 5 级 `if/elseif` 梯度判断（E/D/C/B/A） |
| 商场阶梯折扣计算 | 6 挡折扣 `if/elseif` + 精确金额 `%.2f` 格式化输出 |

---

### HW03 — 循环与控制结构

**内容：** 5 道循环题，包含经典数学问题和自定义函数，引入递归思想。

| 题目 | 实现要点 |
|------|----------|
| 四则运算答题系统（10 题） | `switch/case` 计算 + 内置答案对比统计正确数 |
| 百钱买百鸡 | 双重 `for` 循环枚举（公鸡≤20，母鸡≤33） |
| 哥德巴赫猜想验证 | 自定义 `issushu` 函数（优化：只判断到 $\sqrt{n}$） |
| 十进制转二进制 | `dec2bin` 内置函数一行实现 |
| 斐波那契数列前 30 项 | 自定义递归函数 `fibo(n)`，`fibo(n) = fibo(n-1) + fibo(n-2)` |

---

### HW04 — 数据可视化

**内容：** 4 道绘图题，系统覆盖 MATLAB 常用图形类型，注重图表规范与美观性。

| 题目 | 图形类型 | 实现要点 |
|------|----------|----------|
| 正弦曲线与直线的交点图 | `plot` + `scatter` | `fzero` 数值求交点，`text` 标注，`legend` 图例 |
| 四子图综合展示 | `subplot` 2×2 | 极坐标 `polarplot`、填充 `fill`、双 Y 轴 `yyaxis`、相图 |
| 快慢衰减双 Y 轴图 | `yyaxis` 双轴 | $y_1 = 20e^{-0.5x}\cos(\pi x)$，$y_2 = 0.2e^{-0.5x}\cos(8\pi x)$ |
| 采样精度对比四子图 | `subplot` 2×2 | 粗/密采样 × 点/线 线型的 4 种对比 |

---

### HW05 — 回归分析

**内容：** 2 道回归分析题，从一元多项式到多元线性回归，掌握 `regress` 函数的标准用法。

**题1：金属块温度三次多项式拟合**

设计矩阵为：

$$\mathbf{T} = \begin{bmatrix} 1 & t_1 & t_1^2 & t_1^3 \\ \vdots & \vdots & \vdots & \vdots \\ 1 & t_n & t_n^2 & t_n^3 \end{bmatrix}$$

调用 `regress(temp', T_mat)` 得到系数向量 $\mathbf{b}$，外推预测 9 小时温度。

**题2：体育三项成绩多元线性回归**

综合得分模型：

$$\hat{y} = b_0 + b_1 \cdot x_{\text{跳远}} + b_2 \cdot x_{\text{1000m}} + b_3 \cdot x_{\text{跳绳}}$$

对 15 名同学的数据进行拟合，绘制三项原始指标与综合打分的对比折线图。


---

### HW06 — 正则化回归

**内容：** 波士顿房价数据集的 L2 正则化（岭回归）预测，理解正则化对过拟合的抑制作用。

**核心流程：**

```
读取 housing.data → randperm 随机8:2划分 → ridge 岭回归拟合
→ 测试集预测 → 计算 MSE → 绘制真实值 vs 预测值对比图
```

**岭回归目标函数：**

$$\hat{\mathbf{b}} = \arg\min_{\mathbf{b}} \left\{ \|\mathbf{y} - \mathbf{X}\mathbf{b}\|_2^2 + \lambda \|\mathbf{b}\|_2^2 \right\}$$

本作业取 $\lambda = 0.1$ 作为演示，可通过修改脚本开头的 `k` 变量调整惩罚强度。

> ⚠️ **数据依赖：** 运行前请将 `housing.data` 文件放置在 MATLAB 当前工作路径下。

---

### HW07 — 分类与模型评估

**内容：** 基于鸢尾花数据集（Fisher Iris），使用 SVM 进行二分类，并通过 ROC 曲线和 AUC 值完整评估模型性能。

**核心流程：**

```
load fisheriris → 取前100样本前2特征 → randperm 随机8:2划分
→ fitcsvm 训练 → predict 获取得分 → 自定义 plot_roc 绘制曲线 → trapz 计算 AUC
```

**ROC 曲线绘制原理：**

自定义 `plot_roc` 函数按预测得分升序遍历样本：预测为正类则 TPR 下降一步，预测为负类则 FPR 下降一步，最终用梯形法则 `trapz` 计算曲线下面积 AUC：

$$\text{AUC} = -\int_1^0 \text{TPR} \, d(\text{FPR}) = \int_0^1 \text{TPR} \, d(\text{FPR})$$

---

## 4. 期末项目：miRNA–疾病关联预测

### 4.1 问题背景

miRNA（微小核糖核酸）与多种人类疾病存在已知关联。期末项目基于已知的 miRNA–疾病关联网络，利用 **Katz 链路预测算法**挖掘潜在的未知关联，并通过 AUC 评分量化预测效果。

### 4.2 数据文件说明

| 文件名 | 内容 |
|--------|------|
| `disease_name.xlsx` | 疾病名称列表 |
| `miRNA_name.xlsx` | miRNA 名称列表 |
| `diseasesim.txt` | 疾病相似度矩阵（n × n） |
| `mirsim.txt` | miRNA 相似度矩阵（m × m） |
| `Known miRNA-disease association number.txt` | 已知关联的 [miRNA_id, disease_id] 索引对 |

> ⚠️ **数据依赖：** 上述 5 个数据文件需自行准备并放置于脚本同一目录下，本仓库不分发原始数据集。

### 4.3 算法流程

**第一步：构建已知关联矩阵 $M_0$（m × n）**

$$M_0[i,j] = \begin{cases} 1 & \text{已知 miRNA}_i \text{ 与疾病}_j \text{ 存在关联} \\ 0 & \text{否则} \end{cases}$$

**第二步：构建转移概率矩阵 $R_D$**

对 $M_0$ 按列归一化，得到从疾病节点到 miRNA 节点的随机游走转移概率：

$$R_D[:,j] = \frac{M_0[:,j]}{\sum_i M_0[i,j]}$$

**第三步：组装异构网络大矩阵 $A$**

$$A = \begin{bmatrix} S_{\text{miRNA}} & R_D \\ R_D^\top & S_{\text{disease}} \end{bmatrix}$$

其中 $S_{\text{miRNA}}$ 为 miRNA 相似度矩阵，$S_{\text{disease}}$ 为疾病相似度矩阵。

**第四步：计算 Katz 指标**

$$\text{Katz}(A) = \sum_{l=1}^{4} \beta^l A^l = \beta A + \beta^2 A^2 + \beta^3 A^3 + \beta^4 A^4$$

取 $\beta = 0.01$，截取大矩阵右上角的 m × n 子块作为 miRNA–疾病关联预测得分矩阵。

**第五步：ROC/AUC 评估**

将预测得分矩阵展开为向量，与 $M_0$ 的标签向量对比，绘制 ROC 曲线并输出 AUC 值。

### 4.4 预期评估效果

| 指标 | 含义 | 理论参考值 |
|------|------|-----------|
| AUC | ROC 曲线下面积，越接近 1 越好 | ≥ 0.85 可认为模型有效 |
| 实验得分 | AUC × 100（脚本自动输出） | 取决于数据集与 β 参数 |

---

## 5. 代码规范与优化说明

相较于课堂示例代码，本仓库中的作业进行了若干工程化规范处理：

| 优化点 | 原写法 | 本仓库写法 |
|--------|--------|-----------|
| 数据集随机划分 | 繁琐 `for` 循环手动筛选 | `randperm` 2 行代码搞定 |
| SVM 训练 | 已淘汰的 `svmtrain` | 现代 `fitcsvm` + `predict` |
| 双 Y 轴绘图 | 已淘汰的 `plotyy` | 现代 `yyaxis left/right` |
| 文件读取 | 旧版 `textread` | 推荐 `readmatrix` |
| 数值转换 | `str2num` | 更健壮的 `str2double` |
| 交点求解 | 字符串传参 `fzero('...')` | 匿名函数 `fzero(@(x)...)` |
| 数值格式化 | `%d` 格式化浮点数 | `%.2f` 保留两位小数 |
| 代码防御 | 无错误处理 | `try/catch` 包裹文件读取 |

---

## 6. 运行指南

### 6.1 基础作业（HW01 ~ HW04）

直接在 MATLAB 中打开对应 `.m` 文件，按 **F5** 或点击「运行」即可。HW01 ~ HW03 为交互式作业，运行后需在命令行按提示输入数据。

### 6.2 回归作业（HW05）

```matlab
% 直接运行，数据已硬编码在脚本中
% 运行 HW05_Regression_Analysis.m
```

### 6.3 波士顿房价（HW06）

```matlab
% ① 将 housing.data 文件复制到当前工作路径
% ② 直接运行 HW06_Regularized_Regression.m
% 可在脚本开头修改岭参数：
k = 0.1;   % 尝试 0.01 / 0.1 / 1.0 / 10 观察效果变化
```

### 6.4 SVM 分类（HW07）

```matlab
% 鸢尾花数据集已内置于 MATLAB，无需额外下载
% 直接运行 HW07_Classification_Model_Evaluation.m
```

### 6.5 期末项目（Final）

```matlab
% ① 将以下 5 个文件放置到脚本同一目录：
%    disease_name.xlsx, miRNA_name.xlsx,
%    diseasesim.txt, mirsim.txt,
%    Known miRNA-disease association number.txt
% ② 直接运行 Final_Project_Machine_Learning.m
% ③ 命令行将输出 AUC 值与预计实验得分
```

---

## 7. 依赖环境

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| MATLAB | R2018b 或更高 | `xline`/`yline` 需 R2018b+；`yyaxis` 需 R2016a+ |
| Statistics and Machine Learning Toolbox | 任意版本 | HW06 的 `ridge`、HW07 的 `fitcsvm` 均依赖此工具箱 |
| Optimization Toolbox | 不需要 | 本课程作业未使用 `fmincon` |

> **工具箱检查：** 在 MATLAB 命令行运行 `ver` 可查看当前已安装的工具箱列表。若缺少 Statistics and Machine Learning Toolbox，HW06 和 HW07 将无法运行。

---

## 8. 版权声明

Copyright © 2025 Ying Qichi. All rights reserved.

本仓库中的全部 MATLAB 脚本（`.m` 文件）以**学术共享**精神开源，供后续同学学习参考，具体条款如下：

- ✅ 在注明来源的前提下，可免费用于个人学习、课程参考与非商业教学，允许修改和再分发。
- ✅ 在引用本项目的前提下，允许基于此代码进行衍生作业或研究。
- ❌ 未经作者明确书面授权，禁止将本代码或其衍生版本用于任何商业用途。
- ❌ 严禁直接将本代码作为个人原创作业提交，请在充分理解后独立完成。

> 本仓库代码均为课程作业的参考实现，不附带任何关于正确性的学术担保。
> 部分题目存在多种等价解法，鼓励在理解思路的基础上探索更优雅的实现方式。
>
> MATLAB® 为 MathWorks, Inc. 的注册商标，本项目与 MathWorks 无任何隶属关系或背书。

---

*如发现代码 bug 或有更优雅的写法，欢迎提交 Issue 或 PR，一起让这份参考资料更完善。*
