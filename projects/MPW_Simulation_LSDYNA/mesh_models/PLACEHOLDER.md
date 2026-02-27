# mesh_models / 网格模型目录

> **⚠ 此目录下的核心网格文件 `mesh.k` 未随仓库分发。**
> 本文档说明缺席原因及替代方案。

---

## 为何 `mesh.k` 不在此处？

`mesh.k` 是本仿真项目的核心几何与离散化资产，由 HyperMesh 2022 生成，文件体积约 **48 MB**，包含以下内容：

- 线圈、集磁器（Field Shaper）与铝飞管的完整三维**六面体结构化网格拓扑**
- 焊接作用区采用 **1 mm 精细网格**、非关键区域采用 **2 mm 粗化网格**的局部自适应加密策略
- 为满足 `*EM_MAT_001` 电磁耦合要求而精心设计的**零件 ID 分配**与**节点集定义**（NSID=4 用于边界约束，SIDVIN/SIDVOUT 用于电路激励）
- 经过反复迭代验证的集磁器斜壁几何参数化方案，直接支撑了论文关于内外径比对涡流分布影响的核心结论

出于以下两点考量，我们选择暂不开放完整网格文件：

**1. 知识产权保护（IP Protection）**
上述网格拓扑与加密策略是本研究方法论的重要组成部分，凝结了大量工程调试与学术验证工作。在论文正式发表并完成相关知识产权登记之前，核心数据资产不予公开分发。

**2. 仓库轻量化（Repository Hygiene）**
48 MB 的二进制文件不适合纳入 Git 版本控制。为保持仓库的可克隆性与长期可维护性，大体积二进制资产统一采用独立渠道管理。

---

## 替代方案

### 📖 查阅 README 中的网格截图

根目录 [`README.md`](../README.md) 的「研究背景」章节附有仿真模型的高清截图，展示了网格拓扑、分区策略与整体几何布局，可作为复现参考。

### 🔬 研究求解器核心逻辑

[`solver_core/`](../solver_core/) 目录下完整开放了两个关键文件：

| 文件 | 内容摘要 |
|------|----------|
| `i.k` | 主关键字文件：零件定义、全局参数（含几何尺寸约束）、材料属性、边界条件及文件包含逻辑 |
| `em.k` | 电磁-结构强耦合求解器配置：FEM-BEM 耦合策略、RLC 放电电路、电磁材料定义及收敛容差 |

两个文件中的 `*PARAMETER` 块完整记录了网格构建所需的关键几何约束（管件外径、壁厚、间隙、集磁器内外径比等），足以支撑独立网格的重建工作。

### 📬 学术合作请求

如您有合理的学术研究需求，欢迎通过以下方式联系：

> 请在本仓库提交一个 **GitHub Issue**，注明研究机构、用途说明及预期使用场景。
> 我们将视情况以非商业学术协议的形式提供网格文件的访问权限。

---

*本目录仅作占位与说明用途。如上述信息发生变更，将以本文件为准同步更新。*

---
---

# mesh_models / Mesh Model Directory

> **⚠ The core mesh file `mesh.k` is not distributed with this repository.**
> This document explains the rationale and provides alternatives.

---

## Why Is `mesh.k` Not Here?

`mesh.k` is the core geometric and discretization asset of this simulation project, generated with HyperMesh 2022 The file is approximately **48 MB** in size and contains the following:

- Complete 3D **structured hexahedral mesh topology** for the coil, field shaper, and aluminum flyer tube
- A locally adaptive refinement strategy: **1 mm fine mesh** in the welding zone and **2 mm coarse mesh** in non-critical regions
- Carefully designed **part ID assignments** and **node set definitions** required for `*EM_MAT_001` electromagnetic coupling (NSID=4 for boundary constraints; SIDVIN/SIDVOUT for circuit excitation)
- Parameterized field shaper slanted-wall geometry, iteratively validated against experiments, which directly underpins the paper's core findings on how the inner-to-outer diameter ratio governs eddy current distribution

We have chosen not to release the complete mesh file for two reasons:

**1. Intellectual Property Protection**
The mesh topology and refinement strategy constitute a methodological contribution of this work, embodying substantial engineering effort and academic validation. The core data assets will not be publicly distributed until the paper is formally published and relevant IP registrations are completed.

**2. Repository Hygiene**
A 48 MB binary file is unsuitable for Git version control. To preserve the clonability and long-term maintainability of this repository, large binary assets are managed through a separate channel.

---

## Alternatives

### 📖 Refer to the Mesh Screenshots in README

The "Background" section of the root [`README.md`](../README.md) includes high-resolution screenshots of the simulation model, showing the mesh topology, partitioning strategy, and overall geometric layout — sufficient for reference reconstruction.

### 🔬 Study the Solver Core Logic

The [`solver_core/`](../solver_core/) directory provides full access to two key files:

| File | Summary |
|------|---------|
| `i.k` | Master keyword file: part definitions, global parameters (including geometric constraints), material properties, boundary conditions, and file include logic |
| `em.k` | Electromagnetic–structural coupling solver configuration: FEM-BEM coupling strategy, RLC discharge circuit, EM material definitions, and convergence tolerances |

The `*PARAMETER` blocks in both files document all key geometric constraints required for mesh construction (tube outer diameter, wall thickness, gap, field shaper inner-to-outer diameter ratio, etc.), providing sufficient information to reconstruct a compatible independent mesh.

### 📬 Academic Collaboration Requests

If you have a legitimate academic research need, please reach out via the following channel:

> Submit a **GitHub Issue** in this repository, including your institution, intended use case, and expected application scope.
> We will evaluate requests on a case-by-case basis and may provide access to the mesh file under a non-commercial academic agreement.

---

*This directory serves as a placeholder and documentation file. Any updates to the above will be reflected here.*
