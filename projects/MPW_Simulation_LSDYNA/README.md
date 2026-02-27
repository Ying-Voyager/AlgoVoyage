# LS-DYNA 磁脉冲焊接仿真代码 — 场形器焊接直径极限研究

> **作者：** Ying Qichi
> **版本：** v1.0
> **日期：** 2026-02-28
> **求解器：** LS-DYNA MPP R8.0+（双精度）· LS-PrePost v4.10.8
>
> 本仓库包含以下论文的仿真输入文件：
>
> **《磁脉冲焊接中场形器焊接直径极限的探究》**
> *Ying Qichi 等，2025*

---

## 目录

1. [研究背景](#1-研究背景)
2. [仓库结构](#2-仓库结构)
3. [仿真概览](#3-仿真概览)
4. [文件说明：`i.k` — 主输入与参数](#4-文件说明ik--主输入与参数)
5. [文件说明：`em.k` — 电磁与结构求解器设置](#5-文件说明emk--电磁与结构求解器设置)
6. [网格文件：`mesh.k`（不开源）](#6-网格文件meshk不开源)
7. [仿真复现的核心结果](#7-仿真复现的核心结果)
8. [运行指南](#8-运行指南)
9. [依赖环境](#9-依赖环境)
10. [引用](#10-引用)
11. [版权声明](#11-版权声明)

---

## 1. 研究背景

磁脉冲焊接（MPW）是一种固态高速碰撞焊接工艺，用于连接异种金属管件。脉冲电容器组通过线圈放电，产生瞬态磁场，在**场形器**中感应出涡流，由此产生的洛伦兹力将外管（飞管）高速推向内管（靶管），在无整体熔化的条件下实现焊接。

MPW 工程化放大中一个核心的未解问题是：**对于给定的场形器，可焊管件的直径极限是多少？** 随着场形器内径的增大，两种相互竞争的效应同时出现：

- **内环电流**减弱，导致作用于管件的磁压降低；
- 更大的管件半径在相同磁压下，几何上会**放大环向应力**。

两者的非单调竞争关系决定了最优可焊直径窗口。此外，当场形器内外径比超过约 0.7 时，内外环电流路径发生**干涉**，导致驱动电流急剧非线性下降。

本仿真直接支撑了论文中的理论模型、数值验证和实验验证。采用 LS-DYNA 三维电磁-力学耦合 FEM-BEM 仿真，研究了 **70 mm** 和 **80 mm** 外径的 AA6061-T6 铝管。

<p align="center">
  <img src="https://github.com/user-attachments/assets/f358e0eb-61ef-4592-9382-608f462b2e2d" width="49%" />
  <img src="https://github.com/user-attachments/assets/fc4b8df8-5972-415f-a28f-d91dcf32e365" width="49%" />
</p>

---

## 2. 仓库结构

```
MPW_Simulation_LSDYNA/
├── README.md               ← 本文件
├── solver_core/
│   ├── i.k                 ← 主关键字文件：零件定义、参数、材料、
│   │                          边界条件、文件包含
│   └── em.k                ← 电磁求解器设置、结构控制、材料电磁属性、
│                              电路定义、输出请求
└── mesh_models/
    └── mesh.k              ← （不开源）由 CAD 几何生成的有限元网格
                               如需网格文件，请通过 Issues 联系作者。
```

> **关于 `mesh.k`：** 网格文件包含线圈、场形器和飞管的完整三维六面体有限元离散，由 LS-PrePost 生成，目前不开源。缺少此文件求解器将无法运行。请参阅[第 6 节](#6-网格文件meshk不开源)获取足以重建兼容网格的几何与网格划分信息。

---

## 3. 仿真概览

| 项目 | 详情 |
|------|------|
| **求解器** | LS-DYNA MPP R8.0+（必须使用双精度） |
| **耦合方法** | FEM–BEM 电磁-力学耦合 |
| **仿真时长** | 80 µs（`ENDTIM = 8.0e-5 s`） |
| **初始时间步** | 100 ns（`DTINIT = 1.0e-7 s`） |
| **时间步安全系数** | 0.1（`TSSFAC`） |
| **输出间隔** | 1 µs（D3PLOT、GLSTAT、MATSUM） |
| **激励源** | 实验提取的放电电流第一半周波形 |
| **峰值放电电压** | ≈ 9.0 × 10⁹ V·s 等效（电路：`V0 = 8.999999e9`） |
| **电路参数** | R = 5.96 mΩ，L = 0.203 mH，C = 0.2 µF |
| **管件材料** | AA6061-T6（简化 Johnson–Cook 模型） |
| **线圈 / 场形器** | 刚体（铜 / 铜合金） |
| **网格密度** | 焊接区 1 mm / 其余区域 2 mm |
| **场形器与管件间隙** | 0.5 mm |
| **管件壁厚** | 2 mm |

### 求解物理场

仿真在每个时间步内耦合三个物理域：

```
┌──────────────────────────────────────────────────┐
│  1. EM BEM 求解器  →  自由空间中的磁场           │
│         ↕ (FEM-BEM 耦合)                         │
│  2. EM FEM 求解器  →  涡流与焦耳热               │
│         ↕ (洛伦兹体力 → 力学载荷)               │
│  3. 结构 FEM      →  大变形运动学                │
│                       （管件加速与碰撞）          │
└──────────────────────────────────────────────────┘
```

---

## 4. 文件说明：`i.k` — 主输入与参数

`i.k` 是提交给 LS-DYNA 的顶层关键字文件，定义所有**参数化变量**、**零件定义**，并包含两个支撑文件。

### 4.1 全局参数（`*PARAMETER`）

所有物理和数值参数均集中为命名变量，无需修改底层 card 数据即可方便地进行几何或材料参数扫描。

| 参数名 | 符号 | 数值 | 单位 | 说明 |
|--------|------|------|------|------|
| `T_end` | *t*_end | 1.0 × 10⁻⁴ | s | 仿真结束时间 |
| `dt_plot` | Δ*t*_plot | 2.0 × 10⁻⁶ | s | D3PLOT 输出间隔 |
| `em_dt` | Δ*t*_EM | 1.0 × 10⁻⁶ | s | 电磁求解器基础时间步 |
| `em_bemmtx` | — | 25 | — | BEM 矩阵更新频率 |
| `em_femmtx` | — | 25 | — | FEM 矩阵更新频率 |
| `em_cond1` | σ_coil | 58 MS/m | MS/m | 线圈电导率（铜） |
| `em_cond2` | σ_FS | 30 MS/m | MS/m | 场形器电导率 |
| `em_res` | R | 5.96 mΩ | mΩ | 电路电阻 |
| `em_cap` | C | 2.0 × 10⁻⁷ | F | 电容 |
| `em_ind` | L | 230 µH | µH | 电路电感 |
| `em_v0` | V₀ | 7.0 × 10⁹ | — | 初始放电电压（归一化） |
| `struc_dt` | Δ*t*_struct | 2.0 × 10⁻⁶ | s | 结构输出时间步 |
| `struc_ro1` | ρ_FS | 18.940 × 10⁻³ | g/mm³ | 场形器材料密度 |
| `struc_ro2` | ρ_tube | 2.7 × 10⁻³ | g/mm³ | 铝管密度（AA6061） |
| `struc_E` | E | 68.9 GPa | GPa | 铝的杨氏模量 |
| `struc_nu` | ν | 0.33 | — | 泊松比 |
| `struc_sig` | σ_y | 210 MPa | MPa | 初始屈服应力（J-C 模型参数 A） |
| `therm_ti` | T₀ | 25 °C | °C | 初始温度 |

> 若研究不同场形器几何，修改 `em_cond2`（电导率）并相应重建或参数化 `mesh.k`。电路参数（`em_res`、`em_cap`、`em_ind`、`em_v0`）可按不同电容器组配置进行调整。

### 4.2 零件定义（`*PART`）

| 零件 ID | 名称 | 材料类型 | 作用 |
|---------|------|----------|------|
| 1 | `coil` | MAT_RIGID | 铜线圈 — 刚体，EM 激励源 |
| 2 | `FS2` | MAT_RIGID | 场形器本体 2 — 刚体，EM 被动导体 |
| 3 | `FS1` | MAT_RIGID | 场形器本体 1 — 刚体，EM 被动导体 |
| 4 | `tubeAl` | MAT_SIMPLIFIED_JOHNSON_COOK | AA6061-T6 飞管 — 可变形体 |

所有零件均使用 `SECTION_SOLID`（单元公式 1 — 常应力实体单元）。

### 4.3 文件包含

```
*INCLUDE em.k      ← 电磁求解器配置、电路、材料电磁属性
*INCLUDE mesh.k    ← 网格几何（不开源）
```

---

## 5. 文件说明：`em.k` — 电磁与结构求解器设置

`em.k` 包含所有求解器控制卡、材料定义、放电电路和输出配置，从 `i.k` 中分离出来，以将求解器物理与几何参数化隔离。

### 5.1 结构控制

| 控制卡 | 参数 | 数值 | 说明 |
|--------|------|------|------|
| `*CONTROL_SOLUTION` | `SOLN = 0` | 结构 + EM | 耦合结构–电磁分析 |
| `*CONTROL_TERMINATION` | `ENDTIM` | 8.0 × 10⁻⁵ s | 结束时间（第一半周期 ≈ 30 µs 即可完成变形，延伸至 80 µs） |
| `*CONTROL_TIMESTEP` | `DTINIT` | 1.0 × 10⁻⁷ s | 初始力学时间步 |
| | `TSSFAC` | 0.1 | 时间步缩放系数（EM 耦合稳定性要求保守取值） |

**结束时间较短的原因：** MPW 的物理变形几乎全部发生在放电电流**第一半周期**（≈ 15–30 µs）内。运行至 80 µs 可完整捕捉电流衰减过程，同时控制计算成本。

### 5.2 输出配置

| 控制卡 | 间隔 | 格式 | 内容 |
|--------|------|------|------|
| `*DATABASE_BINARY_D3PLOT` | 1 µs | 二进制 | 全场数据（位移、应力、速度、电磁场） |
| `*DATABASE_GLSTAT` | 1 µs | 二进制 | 全局能量平衡 |
| `*DATABASE_MATSUM` | 1 µs | 二进制 | 各材料能量 |
| `*EM_DATABASE_CIRCUIT` | 每步 | ASCII | 电路电流、电压、能量（用于提取论文图 4 中的放电波形） |

### 5.3 边界条件

```
*BOUNDARY_SPC_SET  NSID=4，约束全部自由度
```
节点集 4（在 `mesh.k` 中定义）对应线圈外表面，约束所有平动和转动自由度。场形器和管件可自由响应电磁载荷。

### 5.4 材料定义

#### 线圈 — `*MAT_RIGID`（MID=1）

| 属性 | 数值 |
|------|------|
| 密度 ρ | 9.9 × 10⁻³ g/mm³（铜） |
| 杨氏模量 E | 9.7 × 10¹⁰ Pa |
| 泊松比 ν | 0.30 |
| 约束 | 全自由度固定（CON1=7，CON2=7） |

#### 铝飞管 — `*MAT_SIMPLIFIED_JOHNSON_COOK`（MID=2，AA6061-T6）

飞管采用简化 Johnson–Cook 塑性模型，捕捉应变硬化和应变率敏感性，不含热软化项：

$$\sigma = (A + B\varepsilon^n)(1 + C\ln\dot{\varepsilon}^*)$$

| 参数 | 符号 | 数值 | 单位 |
|------|------|------|------|
| 初始屈服应力 | A | 3.24 × 10⁸ | Pa |
| 硬化常数 | B | 1.141 × 10⁸ | Pa |
| 硬化指数 | n | 0.42 | — |
| 应变率系数 | C | 0.002 | — |
| 密度 | ρ | 2.7 × 10⁻³ | g/mm³ |
| 杨氏模量 | E | 6.9 × 10¹⁰ | Pa |
| 泊松比 | ν | 0.33 | — |
| 参考应变率 | ε₀ | 1.0 | s⁻¹ |

上述参数取自 Lesuer 等（2001），与高应变率铝合金表征结果一致。

#### 场形器 — `*MAT_RIGID`（MID=3）

与线圈相同的刚体公式，全自由度固定。

### 5.5 放电电流激励（`*DEFINE_CURVE`，LCID=1）

激励为**电流–时间列表曲线**，缩放系数 `SFA = 1.5 × 10⁻⁶`，`SFO = 1 × 10⁶`，直接从实验 Rogowski 线圈测量数据提取。曲线捕捉 RLC 放电第一半周期（0–30 µs），峰值电流出现在 t ≈ 15 µs，幅值约 229 kA。

```
时间 (µs)    电流 (kA，归一化)
0            4.2
5            89.5
10           185.3
15           228.9   ← 峰值
20           202.0
25           113.0
30           6.2     ← 第一半周期结束
```

使用实验测量波形（而非理想 RLC 解析解）直接提升了仿真保真度——在所有测试放电能量（20–35 kJ）下，径向收缩量的仿真误差为 **2–4%**。

### 5.6 电磁求解器配置

LS-DYNA 电磁模块采用混合 **FEM-BEM** 方法：FEM 求解导体内部涡流；BEM 处理周围空气/真空域，无需对自由空间进行网格划分。

#### 电磁控制（`*EM_CONTROL`）

| 参数 | 数值 | 说明 |
|------|------|------|
| `EMSOL` | 1 | EM–结构耦合求解 |
| `NPERIO` | 2 | 每宏时间步的 EM 周期数 |
| `NCYLFEM` | 1 | FEM 矩阵重建频率 |
| `NCYLBEM` | 1 | BEM 矩阵重建频率 |

#### 电磁时间步（`*EM_CONTROL_TIMESTEP`）

| 参数 | 数值 | 说明 |
|------|------|------|
| `TSTYPE` | 1 | 恒定 EM 时间步 |
| `DTCONS` | 1.0 × 10⁻⁷ s | EM 时间步（与结构一致） |
| `RLCSF` | 25 | RLC 子循环系数 |

#### 求解器收敛容差

| 求解器 | 控制卡 | 容差 | 最大迭代次数 |
|--------|--------|------|-------------|
| BEM（外部磁场） | `*EM_SOLVER_BEM` | 1 × 10⁻⁶ | 1000 |
| FEM（内部涡流） | `*EM_SOLVER_FEM` | 1 × 10⁻³ | 200 |
| FEM-BEM 耦合 | `*EM_SOLVER_FEMBEM` | 1 × 10⁻⁴ | 200 |

BEM 收紧容差（`1e-6`）是准确求解场形器内表面薄趋肤深度电流分布的必要条件，而这正是本研究的核心关注量。

### 5.7 电磁材料属性（`*EM_MAT_001`）

| 零件 | MID | EM 类型 | σ (MS/m) | 说明 |
|------|-----|---------|----------|------|
| 线圈 | 1 | 2（导体，EM 激励源） | 58 | 铜线圈 |
| 飞管 | 2 | 4（导体，被动） | 23 | AA6061-T6 铝 |
| 场形器 | 3 | 4（导体，被动） | 23 | 铜合金场形器 |

`MTYPE=2`：承载规定电流的零件（线圈）。`MTYPE=4`：被感应涡流的被动导体。

### 5.8 RLC 放电电路（`*EM_CIRCUIT`）

```
*EM_CIRCUIT
  CIRCID=1  CIRCTYP=1（规定电压的 RLC 电路）
  LCID=1    （列表电流波形）
  R = 5.96 mΩ
  L = 0.203 mH
  C = 0.2 µF
  V0 = 8.999999e9（初始电容电荷，模型单位）
  SIDVIN=1，SIDVOUT=2（线圈上的电流入射/出射面段集）
```

该电路代表**单回路 RLC 电容器组**。Rogowski 线圈测量（`*EM_CIRCUIT_ROGO`，ROGOID=1，SETID=1）记录仿真电流，用于与实验数据（论文图 4）对比。

---

## 6. 网格文件：`mesh.k`（不开源）

网格文件未包含在本仓库中。以下信息可帮助重建兼容网格。

### 几何摘要

| 组件 | 几何形态 | 关键尺寸 |
|------|----------|----------|
| 铝飞管 | 薄壁圆柱 | 外径 70 mm 或 80 mm；壁厚 2 mm |
| 场形器 | 斜壁聚能环 | 内半径 *r*_a（可变）；外半径 *r*_b 固定 |
| 线圈 | 多匝螺线管（简化为实体导体） | 与标准 MPW 线圈几何一致 |

### 网格划分策略

| 区域 | 单元尺寸 | 原因 |
|------|----------|------|
| 焊接区（管件 ± 场形器内环区域） | 1 mm | 解析趋肤深度（铝在 30 kHz 时 δ ≈ 1–3 mm）并捕捉陡峭场梯度 |
| 其余区域（线圈体、场形器外壁） | 2 mm | 在保持精度的同时降低总自由度数 |
| 单元类型 | 8 节点六面体（ELFORM=1） | `*EM_MAT_001` 电磁耦合所必需 |

网格由 **LS-PrePost v4.10.8** 生成。任何标准六面体网格划分工具（如 HyperMesh、ANSA、LS-PrePost）均可生成兼容的 `mesh.k`，前提是零件 ID（1–4）、节点集 ID（NSID=4，用于 SPC）和面段集 ID（SIDVIN=1、SIDVOUT=2，用于电路）与 `i.k` 和 `em.k` 中的定义一致。

---

## 7. 仿真复现的核心结果

仿真在 20、23、26、29、32、35 kJ 放电能量下（每组重复 3 次）与 70 mm 和 80 mm 外径 AA6061-T6 铝管实验进行了对比验证。

### 7.1 径向收缩量 vs. 放电能量

- 仿真与实验均显示，两种管径下径向收缩量随放电能量**单调增加**。
- 相同放电能量下，80 mm 管的**绝对收缩量更大**（因其周长更大）。
- 仿真精度：最大误差 **3–4%**，平均误差 **2–3%**（覆盖全部工况）。

### 7.2 工程应变对比

- 尽管 70 mm 管绝对收缩量较小，但其**工程应变高于** 80 mm 管。
- 这与解析预测一致：70 mm 管的内外径比更接近最优窗口（0.15–0.50 × *r*_b），在单位磁压下产生更高的环向应力。

### 7.3 内环电流 vs. 场形器内径

| *r*_a / *r*_b | 归一化内环电流 | 区间特征 |
|:---:|:---:|:---|
| < 0.5 | > 0.85 | 最优窗口；电流强，环向应力高 |
| 0.5 – 0.7 | 0.6 – 0.85 | 缓慢衰减；仍可焊接 |
| ≈ 0.7 | 干涉起始 | 电流路径开始重叠 |
| > 0.8 | **急剧下降** | 强干涉；内环电流崩塌 |

仿真复现了 *r*_a/*r*_b > 0.8 时**急剧非线性电流衰减**现象，单纯电阻模型无法捕捉此效应。论文引入**指数趋肤深度修正因子**以协调理论与仿真结果。

### 7.4 磁压分布

磁压 *P*_M ∝ *I*_i²（内环电流平方）。仿真验证了理论预测：*P*_M 随内径增大单调下降，遵循内环电流的平方规律。

### 7.5 环向应力 — 非单调最优窗口

管件内壁环向应力（采用 Lamé 解对受外压厚壁圆筒求解）对内径呈**非单调依赖**：

- 先**增大**（几何放大效应主导）
- 在 *r*_a/*r*_b ≈ 0.15–0.50 附近达到最大值
- 后**减小**（磁压衰减主导）

归一化环向应力在 *r*_a ≈ 0.15–0.50 × *r*_b 范围内保持 **0.9 以上**，定义了**最优可焊直径窗口**。

---

## 8. 运行指南

### 8.1 前提条件

- LS-DYNA MPP R8.0.0 或更高版本，**双精度**构建
- MPI 环境（OpenMPI 或 IntelMPI），用于并行计算
- `mesh.k` 与 `i.k`、`em.k` 位于同一目录（或更新 `*INCLUDE mesh.k` 路径）

### 8.2 文件准备

确保以下文件位于同一工作目录：

```
your_run_dir/
├── i.k          ← 主输入文件（提交此文件）
├── em.k         ← 由 i.k 自动包含
└── mesh.k       ← 由 i.k 自动包含（需另行获取）
```

### 8.3 执行命令

**单节点运行（MPI，N 核）：**

```bash
mpirun -np <N> ls-dyna-mpp i=i.k memory=300m ncpu=<N>
```

**典型资源需求：**

| 网格规模 | 核数 | 预估耗时 |
|----------|------|----------|
| ~50 万单元 | 8 | ~4–6 小时 |
| ~50 万单元 | 32 | ~1–2 小时 |

> EM 耦合仿真内存消耗较大。每核至少分配 **300 MB**（`memory=300m`）。BEM 矩阵存储随导体表面单元数以 O(N²) 增长。

### 8.4 修改几何参数

若研究不同场形器内半径：

1. 更新 `mesh.k` 几何（或从 CAD 重新生成）。
2. 若电路参数随放电能量变化，在 `i.k` 中编辑：

```
R   em_v0   <新电压>
R   em_res  <新电阻>
R   em_cap  <新电容>
R   em_ind  <新电感>
```

3. 重新运行。除非需要调整求解器容差或输出间隔，否则无需修改 `em.k`。

### 8.5 后处理

在 **LS-PrePost** 中打开结果文件：

| 输出文件 | 内容 | 建议分析 |
|----------|------|----------|
| `d3plot` | 全场历史 | 管件变形、速度场、电流密度分布、磁压云图 |
| `glstat` | 全局能量 | 动能 vs. 时间——验证电磁到力学的能量传递 |
| `matsum` | 各零件能量 | 确认管件动能在 ~15 µs 时达到峰值 |
| `EM_DATABASE_CIRCUIT` | 电路 I/V/E | 提取仿真电流波形，与实验 Rogowski 数据对比 |

提取**径向收缩量**：从 `d3plot` 文件中，在管件变形区中截面（场形器槽轴向中心）沿径向方向量取节点位移。

---

## 9. 依赖环境

| 组件 | 版本 | 备注 |
|------|------|------|
| LS-DYNA | MPP R8.0+ | **必须使用双精度**；EM 模块需 R7.1+ |
| LS-PrePost | v4.10.8+ | 用于网格生成和后处理 |
| MPI | OpenMPI 4.x / IntelMPI 2019+ | MPP 并行运行所必需 |
| 操作系统 | Linux（在 CentOS 7 / Ubuntu 20.04 上测试） | 也支持 Windows HPC |

> ⚠️ `*EM_CIRCUIT`、`*EM_SOLVER_BEM` 和 `*EM_MAT_001` 关键字需要 LS-DYNA **R7.1 或更高版本**。使用 R6.x 或更早版本将导致关键字解析错误。

---

## 10. 引用

如您在研究中使用了本仿真文件，请引用配套论文：

```bibtex
@article{yingqichi2025mpw,
  title   = {Exploration of the welding diameter limit of field shaper
             in Magnetic Pulse Welding},
  author  = {Ying Qichi et al.},
  journal = {-},
  year    = {2025},
  note    = {仿真文件见：https://github.com/YingQichi/AlgoVoyage}
}
```

---

## 11. 版权声明

Copyright © 2025 Ying Qichi. All rights reserved.

本仓库中的仿真输入文件（`i.k`、`em.k`）仅供**学术及非商业研究使用**，具体条款如下：

- ✅ 在注明来源的前提下，可免费用于非商业研究、修改和再分发。
- ✅ 在引用原始论文的前提下，允许基于此进行衍生工作。
- ❌ 未经作者明确书面授权，禁止用于商业用途。
- ❌ 禁止在未明确标注修改内容的情况下分发修改后的文件。

> 网格文件（`mesh.k`）不开源。如有合作研究需求，欢迎通过 GitHub Issues 提出申请。
>
> LS-DYNA® 是 Ansys, Inc. 的注册商标。本仓库与 Ansys 或 DYNAmore GmbH 无任何隶属关系或背书。

---

*如对仿真设置、电磁求解器参数或解析模型实现有任何疑问，欢迎在 GitHub 提交 Issue。*

---
---

# LS-DYNA Simulation Code for Magnetic Pulse Welding — Field Shaper Diameter Limit Study

> **Author:** Ying Qichi
> **Version:** v1.0
> **Date:** 2026-02-28
> **Solver:** LS-DYNA MPP R8.0+ (double precision) · LS-PrePost v4.10.8
>
> This repository contains the simulation input files accompanying the publication:
>
> **"Exploration of the welding diameter limit of field shaper in Magnetic Pulse Welding"**
> *Ying Qichi et al., 2025*

---

## Table of Contents

1. [Background](#1-background)
2. [Repository Structure](#2-repository-structure)
3. [Simulation Overview](#3-simulation-overview)
4. [File Reference: `i.k` — Master Input & Parameters](#4-file-reference-ik--master-input--parameters)
5. [File Reference: `em.k` — EM & Structural Solver Settings](#5-file-reference-emk--em--structural-solver-settings)
6. [Mesh File: `mesh.k` (Not Distributed)](#6-mesh-file-meshk-not-distributed)
7. [Key Results Reproduced by This Simulation](#7-key-results-reproduced-by-this-simulation)
8. [How to Run](#8-how-to-run)
9. [Dependencies & Environment](#9-dependencies--environment)
10. [Citation](#10-citation)
11. [License](#11-license)

---

## 1. Background

Magnetic Pulse Welding (MPW) is a solid-state, high-velocity impact welding process for joining dissimilar metal tubes. A pulsed capacitor bank discharges through a coil, generating a transient magnetic field that induces eddy currents in the **field shaper**. The resulting Lorentz force accelerates the outer (flyer) tube toward the inner (target) tube, forming a weld without bulk melting.

A central unresolved question in MPW upscaling is: **what is the weldable tube diameter limit for a given field shaper?** As the inner diameter of the field shaper increases, two competing effects emerge:

- The **inner-loop current** weakens, reducing magnetic pressure on the tube.
- The larger tube radius geometrically **amplifies hoop stress** for a given pressure.

The non-monotonic interplay of these effects defines an optimal weldable diameter window. Additionally, when the inner-to-outer diameter ratio of the field shaper exceeds ≈ 0.7, current path **interference** between inner and outer loops causes a sharp, non-linear drop in driving current.

This simulation set directly supports the theoretical model, numerical verification, and experimental validation presented in the paper. Tube diameters of **70 mm** and **80 mm** (AA6061-T6 aluminum) are investigated using a 3D electromagnetic–mechanical coupled FEM-BEM simulation in LS-DYNA.

<p align="center">
  <img src="https://github.com/user-attachments/assets/f358e0eb-61ef-4592-9382-608f462b2e2d" width="49%" />
  <img src="https://github.com/user-attachments/assets/fc4b8df8-5972-415f-a28f-d91dcf32e365" width="49%" />
</p>

---

## 2. Repository Structure

```
MPW_Simulation_LSDYNA/
├── README.md               ← This file
├── solver_core/
│   ├── i.k                 ← Master keyword file: parts, parameters, material,
│   │                          boundary conditions, includes
│   └── em.k                ← EM solver settings, structural control, material
│                              EM properties, circuit definition, output requests
└── mesh_models/
    └── mesh.k              ← (NOT distributed) FE mesh generated from CAD geometry
                               Contact the authors for access to the mesh.
```

> **Note on `mesh.k`:** The mesh file contains the complete 3D hexahedral finite element discretization of the coil, field shaper, and flyer tube, generated in LS-PrePost. It is not open-sourced at this time. The solver will not run without it. Please refer to [Section 6](#6-mesh-file-meshk-not-distributed) for geometry and meshing details sufficient to reconstruct a compatible mesh.

---

## 3. Simulation Overview

| Item | Details |
|------|---------|
| **Solver** | LS-DYNA MPP R8.0+ (double precision required) |
| **Coupling method** | Coupled FEM–BEM electromagnetic–mechanical |
| **Simulation duration** | 80 µs (`ENDTIM = 8.0e-5 s`) |
| **Initial timestep** | 100 ns (`DTINIT = 1.0e-7 s`) |
| **Timestep safety factor** | 0.1 (`TSSFAC`) |
| **Output interval** | 1 µs (D3PLOT, GLSTAT, MATSUM) |
| **Excitation** | First half-cycle discharge current waveform (experimentally extracted) |
| **Peak discharge voltage** | ≈ 9.0 × 10⁹ V·s equivalent (circuit: `V0 = 8.999999e9`) |
| **Circuit parameters** | R = 5.96 mΩ, L = 0.203 mH, C = 0.2 µF |
| **Tube material** | AA6061-T6 (Simplified Johnson–Cook) |
| **Coil / Field shaper** | Rigid body (copper / Cu alloy) |
| **Mesh density** | 1 mm (welding zone) / 2 mm (elsewhere) |
| **Gap (field shaper ↔ tube)** | 0.5 mm |
| **Tube wall thickness** | 2 mm |

### Physics solved

The simulation couples three physical domains in each timestep:

```
┌─────────────────────────────────────────────────────┐
│  1. EM BEM solver  →  Magnetic field in free space  │
│         ↕ (FEM-BEM coupling)                        │
│  2. EM FEM solver  →  Eddy currents & Joule heat    │
│         ↕ (Lorentz body force → mechanical load)    │
│  3. Structural FEM →  Large-deformation kinematics  │
│                        (tube acceleration & impact) │
└─────────────────────────────────────────────────────┘
```

---

## 4. File Reference: `i.k` — Master Input & Parameters

`i.k` is the top-level keyword file submitted to LS-DYNA. It defines all **parametric variables**, **part definitions**, and includes the two supporting files.

### 4.1 Global Parameters (`*PARAMETER`)

All physical and numerical parameters are centralized as named variables, making it straightforward to sweep geometries or materials without editing low-level card data.

| Parameter | Symbol | Value | Unit | Description |
|-----------|--------|-------|------|-------------|
| `T_end` | *t*_end | 1.0 × 10⁻⁴ | s | Simulation end time |
| `dt_plot` | Δ*t*_plot | 2.0 × 10⁻⁶ | s | D3PLOT output interval |
| `em_dt` | Δ*t*_EM | 1.0 × 10⁻⁶ | s | EM solver base timestep |
| `em_bemmtx` | — | 25 | — | BEM matrix update frequency |
| `em_femmtx` | — | 25 | — | FEM matrix update frequency |
| `em_cond1` | σ_coil | 58 MS/m | MS/m | Electrical conductivity of coil (copper) |
| `em_cond2` | σ_FS | 30 MS/m | MS/m | Electrical conductivity of field shaper |
| `em_res` | R | 5.96 mΩ | mΩ | Circuit resistance |
| `em_cap` | C | 2.0 × 10⁻⁷ | F | Capacitance |
| `em_ind` | L | 230 µH | µH | Circuit inductance |
| `em_v0` | V₀ | 7.0 × 10⁹ | — | Initial discharge voltage (normalized) |
| `struc_dt` | Δ*t*_struct | 2.0 × 10⁻⁶ | s | Structural output timestep |
| `struc_ro1` | ρ_FS | 18.940 × 10⁻³ | g/mm³ | Density of field shaper material |
| `struc_ro2` | ρ_tube | 2.7 × 10⁻³ | g/mm³ | Density of aluminum tube (AA6061) |
| `struc_E` | E | 68.9 GPa | GPa | Young's modulus of aluminum |
| `struc_nu` | ν | 0.33 | — | Poisson's ratio |
| `struc_sig` | σ_y | 210 MPa | MPa | Initial yield stress (J-C model, parameter A) |
| `therm_ti` | T₀ | 25 °C | °C | Initial temperature |

> To study different field shaper geometries, modify `em_cond2` (conductivity) and regenerate or parametrize `mesh.k` accordingly. Circuit parameters (`em_res`, `em_cap`, `em_ind`, `em_v0`) can be adjusted to match different capacitor bank configurations.

### 4.2 Part Definitions (`*PART`)

| Part ID | Name | Material Type | Role |
|---------|------|---------------|------|
| 1 | `coil` | MAT_RIGID | Copper coil — rigid, EM active |
| 2 | `FS2` | MAT_RIGID | Field shaper body 2 — rigid, EM active |
| 3 | `FS1` | MAT_RIGID | Field shaper body 1 — rigid, EM active |
| 4 | `tubeAl` | MAT_SIMPLIFIED_JOHNSON_COOK | AA6061-T6 flyer tube — deformable |

All parts use `SECTION_SOLID` (element formulation 1 — constant stress solid).

### 4.3 File Includes

```
*INCLUDE em.k      ← EM solver configuration, circuit, material EM properties
*INCLUDE mesh.k    ← Mesh geometry (not distributed)
```

---

## 5. File Reference: `em.k` — EM & Structural Solver Settings

`em.k` contains all solver control cards, material definitions, the discharge circuit, and output configuration. It is separated from `i.k` to isolate solver physics from geometry and parameterization.

### 5.1 Structural Control

| Card | Parameter | Value | Description |
|------|-----------|-------|-------------|
| `*CONTROL_SOLUTION` | `SOLN = 0` | Structural + EM | Coupled structural–EM analysis |
| `*CONTROL_TERMINATION` | `ENDTIM` | 8.0 × 10⁻⁵ s | End time (first half-cycle ≈ 30 µs sufficient for deformation; padded to 80 µs) |
| `*CONTROL_TIMESTEP` | `DTINIT` | 1.0 × 10⁻⁷ s | Initial mechanical timestep |
| | `TSSFAC` | 0.1 | Timestep scale factor (conservative for EM coupling stability) |

**Rationale for short end time:** Physical deformation in MPW occurs almost entirely during the **first half-cycle** of the discharge current (≈ 15–30 µs). Running beyond 80 µs captures the full current decay while keeping computational cost manageable.

### 5.2 Output Configuration

| Card | Interval | Format | Contents |
|------|----------|--------|----------|
| `*DATABASE_BINARY_D3PLOT` | 1 µs | Binary | Full field data (displacement, stress, velocity, EM fields) |
| `*DATABASE_GLSTAT` | 1 µs | Binary | Global energy balance |
| `*DATABASE_MATSUM` | 1 µs | Binary | Per-material energy |
| `*EM_DATABASE_CIRCUIT` | Every step | ASCII | Circuit current, voltage, energy (used to extract discharge waveform for Fig. 4 in the paper) |

### 5.3 Boundary Conditions

```
*BOUNDARY_SPC_SET  NSID=4, all DOFs constrained
```
Node set 4 (defined in `mesh.k`) corresponds to the outer surface of the coil, fixing it in all translational and rotational degrees of freedom. The field shaper and tube are free to respond to electromagnetic loading.

### 5.4 Material Definitions

#### Coil — `*MAT_RIGID` (MID=1)

| Property | Value |
|----------|-------|
| Density ρ | 9.9 × 10⁻³ g/mm³ (copper) |
| Young's modulus E | 9.7 × 10¹⁰ Pa |
| Poisson's ratio ν | 0.30 |
| Constraint | All DOFs fixed (CON1=7, CON2=7) |

#### Aluminum Flyer Tube — `*MAT_SIMPLIFIED_JOHNSON_COOK` (MID=2, AA6061-T6)

The tube uses the Simplified Johnson–Cook plasticity model, capturing strain hardening and strain-rate sensitivity without thermal softening:

$$\sigma = (A + B\varepsilon^n)(1 + C\ln\dot{\varepsilon}^*)$$

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| Initial yield stress | A | 3.24 × 10⁸ | Pa |
| Hardening constant | B | 1.141 × 10⁸ | Pa |
| Hardening exponent | n | 0.42 | — |
| Strain rate coefficient | C | 0.002 | — |
| Density | ρ | 2.7 × 10⁻³ | g/mm³ |
| Young's modulus | E | 6.9 × 10¹⁰ | Pa |
| Poisson's ratio | ν | 0.33 | — |
| Reference strain rate | ε₀ | 1.0 | s⁻¹ |

These parameters are taken from Lesuer et al. (2001) and are consistent with high-strain-rate aluminum characterization.

#### Field Shaper — `*MAT_RIGID` (MID=3)

Same rigid formulation as the coil; all DOFs fixed.

### 5.5 Discharge Current Excitation (`*DEFINE_CURVE`, LCID=1)

The excitation is a **tabulated current-versus-time curve** scaled by `SFA = 1.5 × 10⁻⁶` and `SFO = 1 × 10⁶`, directly extracted from experimental Rogowski coil measurements. The curve captures the first half-cycle of the RLC discharge (0–30 µs), with peak current at t ≈ 15 µs and amplitude ≈ 229 kA.

```
Time (µs)    Current (kA, normalized)
0            4.2
5            89.5
10           185.3
15           228.9   ← Peak
20           202.0
25           113.0
30           6.2     ← End of first half-cycle
```

Using the experimentally measured waveform (rather than an ideal RLC analytical solution) directly improves simulation fidelity — simulation-to-experiment error for radial shrinkage is **2–4%** across all tested discharge energies (20–35 kJ).

### 5.6 Electromagnetic Solver Configuration

The EM module in LS-DYNA uses a hybrid **FEM-BEM** approach: FEM solves eddy currents inside conductors; BEM handles the air/vacuum domain surrounding them, eliminating the need to mesh free space.

#### EM Control (`*EM_CONTROL`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `EMSOL` | 1 | Coupled EM–structural solution |
| `NPERIO` | 2 | Number of EM periods per macro timestep |
| `NCYLFEM` | 1 | FEM matrix rebuild frequency |
| `NCYLBEM` | 1 | BEM matrix rebuild frequency |

#### EM Timestep (`*EM_CONTROL_TIMESTEP`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `TSTYPE` | 1 | Constant EM timestep |
| `DTCONS` | 1.0 × 10⁻⁷ s | EM timestep (matches structural) |
| `RLCSF` | 25 | RLC subcycle factor |

#### Solver Tolerances

| Solver | Card | Tolerance | Max Iterations |
|--------|------|-----------|----------------|
| BEM (exterior field) | `*EM_SOLVER_BEM` | 1 × 10⁻⁶ | 1000 |
| FEM (interior eddy) | `*EM_SOLVER_FEM` | 1 × 10⁻³ | 200 |
| FEM-BEM coupling | `*EM_SOLVER_FEMBEM` | 1 × 10⁻⁴ | 200 |

Tight BEM tolerance (`1e-6`) is required to accurately resolve the thin skin-depth current distribution on the field shaper inner surface, which is the key quantity of interest in this study.

### 5.7 Electromagnetic Material Properties (`*EM_MAT_001`)

| Part | MID | EM Type | σ (MS/m) | Description |
|------|-----|---------|----------|-------------|
| Coil | 1 | 2 (conductor, EM source) | 58 | Copper coil |
| Flyer tube | 2 | 4 (conductor, passive) | 23 | AA6061-T6 aluminum |
| Field shaper | 3 | 4 (conductor, passive) | 23 | Cu alloy field shaper |

`MTYPE=2`: part carrying the prescribed current (coil). `MTYPE=4`: passive conductor where eddy currents are induced.

### 5.8 RLC Discharge Circuit (`*EM_CIRCUIT`)

```
*EM_CIRCUIT
  CIRCID=1  CIRCTYP=1 (RLC with prescribed voltage)
  LCID=1    (tabulated current waveform)
  R = 5.96 mΩ
  L = 0.203 mH
  C = 0.2 µF
  V0 = 8.999999e9 (initial capacitor charge, model units)
  SIDVIN=1, SIDVOUT=2  (current entry/exit segment sets on coil)
```

The circuit represents a **single-mesh RLC capacitor bank**. The Rogowski coil measurement (`*EM_CIRCUIT_ROGO`, ROGOID=1, SETID=1) records the simulated current for comparison with experimental data (Fig. 4 in the paper).

---

## 6. Mesh File: `mesh.k` (Not Distributed)

The mesh file is not included in this repository. The following information is provided to facilitate reproduction of a compatible mesh.

### Geometry Summary

| Component | Geometry | Key Dimensions |
|-----------|----------|----------------|
| Aluminum flyer tube | Thin-walled cylinder | OD = 70 mm or 80 mm; wall = 2 mm |
| Field shaper | Slanted-wall concentrator ring | Inner radius *r*_a (variable); outer radius *r*_b fixed |
| Coil | Multi-turn solenoid (simplified as solid conductor) | Matches standard MPW coil geometry |

### Meshing Strategy

| Region | Element Size | Rationale |
|--------|-------------|-----------|
| Welding zone (tube ± field shaper inner region) | 1 mm | Resolves skin depth (δ ≈ 1–3 mm at 30 kHz for aluminum) and captures steep field gradients |
| Elsewhere (coil body, FS outer wall) | 2 mm | Reduces total DOF count while maintaining accuracy |
| Element type | 8-node hexahedral (ELFORM=1) | Required for `*EM_MAT_001` EM coupling |

Mesh generation was performed in **LS-PrePost v4.10.8**. Any standard hexahedral mesher (e.g., HyperMesh, ANSA, LS-PrePost) can be used to generate a compatible `mesh.k`, provided the part IDs (1–4), node set ID (NSID=4 for SPC), and segment set IDs (SIDVIN=1, SIDVOUT=2 for circuit) match those defined in `i.k` and `em.k`.

---

## 7. Key Results Reproduced by This Simulation

The simulation was validated against experiments using AA6061-T6 tubes of 70 mm and 80 mm outer diameter at discharge energies of 20, 23, 26, 29, 32, and 35 kJ (three repetitions each).

### 7.1 Radial Shrinkage vs. Discharge Energy

- Both simulation and experiment show that radial shrinkage **increases monotonically** with discharge energy for both tube sizes.
- The 80 mm tube exhibits **larger absolute shrinkage** than the 70 mm tube at identical discharge energy, due to its greater circumference.
- Simulation-to-experiment agreement: maximum error **3–4%**, average error **2–3%** across all conditions.

### 7.2 Engineering Strain Comparison

- The **70 mm tube exhibits higher engineering strain** than the 80 mm tube, despite its smaller absolute shrinkage.
- This is consistent with the analytical prediction: the 70 mm tube has a more favorable inner-to-outer diameter ratio (closer to the optimal window of 0.15–0.50 × *r*_b), resulting in higher hoop stress per unit magnetic pressure.

### 7.3 Inner Current vs. Field Shaper Inner Diameter

| *r*_a / *r*_b | Normalized inner current | Regime |
|:---:|:---:|:---|
| < 0.5 | > 0.85 | Optimal window; high current, high hoop stress |
| 0.5 – 0.7 | 0.6 – 0.85 | Gradual decay; still weldable |
| ≈ 0.7 | onset of interference | Current path overlap begins |
| > 0.8 | **sharp drop** | Strong interference; inner current collapses |

The simulation reproduces the **sharp non-linear current attenuation** at *r*_a/*r*_b > 0.8, which cannot be captured by the basic resistance model alone. An **exponential skin-depth correction factor** was introduced to reconcile theory and simulation at large diameters.

### 7.4 Magnetic Pressure Distribution

Magnetic pressure *P*_M ∝ *I*_i² (inner current squared). The simulation confirms the theoretical prediction: *P*_M decreases monotonically with inner diameter, following the square of the inner current.

### 7.5 Hoop Stress — Non-Monotonic Optimal Window

The hoop stress at the tube inner wall (evaluated via Lamé's solution for thick-walled cylinders under external pressure) exhibits a **non-monotonic dependence** on inner diameter:

- First **increases** (geometric amplification dominates)
- Reaches a maximum near *r*_a/*r*_b ≈ 0.15–0.50
- Then **decreases** (magnetic pressure decay dominates)

Normalized hoop stress remains above **0.9** within the range *r*_a ≈ 0.15–0.50 × *r*_b, defining the **optimal weldable diameter window**.

---

## 8. How to Run

### 8.1 Prerequisites

- LS-DYNA MPP R8.0.0 or higher, **double precision** build
- MPI environment (OpenMPI or IntelMPI) for parallel execution
- `mesh.k` in the same directory as `i.k` and `em.k` (or update the `*INCLUDE mesh.k` path)

### 8.2 File Preparation

Ensure the following files are in the same working directory:

```
your_run_dir/
├── i.k          ← Main input (submit this file)
├── em.k         ← Included automatically by i.k
└── mesh.k       ← Included automatically by i.k (provide separately)
```

### 8.3 Execution

**Single-node run (MPI, N cores):**

```bash
mpirun -np <N> ls-dyna-mpp i=i.k memory=300m ncpu=<N>
```

**Typical resource requirement:**

| Mesh size | Cores | Wall time (est.) |
|-----------|-------|-----------------|
| ~500k elements | 8 | ~4–6 h |
| ~500k elements | 32 | ~1–2 h |

> EM-coupled simulations are memory-intensive. Allocate at least **300 MB** per core (`memory=300m`). BEM matrix storage scales as O(N²) with the number of conductor surface elements.

### 8.4 Modifying Geometry Parameters

To study a different field shaper inner radius:

1. Update the `mesh.k` geometry (or regenerate from CAD).
2. If circuit parameters change (different energy level), edit the following in `i.k`:

```
R   em_v0   <new_voltage>
R   em_res  <new_resistance>
R   em_cap  <new_capacitance>
R   em_ind  <new_inductance>
```

3. Re-run. No changes to `em.k` are required unless solver tolerances or output intervals need adjustment.

### 8.5 Post-Processing

Open result files in **LS-PrePost**:

| Output file | Contents | Suggested plots |
|-------------|----------|-----------------|
| `d3plot` | Full field history | Tube deformation, velocity field, current density distribution, magnetic pressure map |
| `glstat` | Global energy | Kinetic energy vs. time — confirms energy transfer from EM to mechanical |
| `matsum` | Per-part energy | Check that tube kinetic energy peaks at ~15 µs |
| `EM_DATABASE_CIRCUIT` | Circuit I/V/E | Extract simulated current waveform; compare with experimental Rogowski data |

To extract **radial shrinkage**, measure nodal displacement in the radial direction at the mid-plane of the tube deformation zone (axial center of the field shaper slot) from the `d3plot` file.

---

## 9. Dependencies & Environment

| Component | Version | Notes |
|-----------|---------|-------|
| LS-DYNA | MPP R8.0+ | **Double precision mandatory**; EM module requires R7.1+ |
| LS-PrePost | v4.10.8+ | Used for mesh generation and post-processing |
| MPI | OpenMPI 4.x / IntelMPI 2019+ | Required for MPP execution |
| OS | Linux (tested on CentOS 7 / Ubuntu 20.04) | Windows HPC also supported |

> ⚠️ The `*EM_CIRCUIT`, `*EM_SOLVER_BEM`, and `*EM_MAT_001` keywords require LS-DYNA **R7.1 or later**. Using R6.x or earlier will cause keyword parsing errors.

---

## 10. Citation

If you use these simulation files in your research, please cite the accompanying paper:

```bibtex
@article{yingqichi2025mpw,
  title   = {Exploration of the welding diameter limit of field shaper
             in Magnetic Pulse Welding},
  author  = {Ying Qichi et al.},
  journal = {-},
  year    = {2025},
  note    = {Simulation files available at: https://github.com/YingQichi/AlgoVoyage}
}
```

---

## 11. License

Copyright © 2025 Ying Qichi. All rights reserved.

The simulation input files (`i.k`, `em.k`) in this repository are released for **academic and non-commercial research use only**, under the following terms:

- ✅ Free to use, modify, and redistribute for non-commercial research, with attribution.
- ✅ Derivative works permitted with citation of the original paper.
- ❌ Commercial use prohibited without explicit written permission from the author.
- ❌ Redistribution of modified files without clearly marking the changes is not permitted.

> The mesh file (`mesh.k`) is not distributed. Requests for access for collaborative research purposes may be submitted via GitHub Issues.
>
> LS-DYNA® is a registered trademark of Ansys, Inc. This repository is not affiliated with or endorsed by Ansys or DYNAmore GmbH.

---

*For questions regarding the simulation setup, EM solver parameters, or analytical model implementation, please open a GitHub Issue.*
