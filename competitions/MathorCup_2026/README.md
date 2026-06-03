# 🏆 CMC 2026 Problem C: Multidimensional Hyperlipidemia Risk Warning and Dynamic Intervention

**—— 基于多维特征融合的中老年高血脂症精准预警及动态干预研究**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen.svg)
![Model](https://img.shields.io/badge/Model-LightGBM%20%7C%20SHAP%20%7C%20DP-orange.svg)
![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)

## 📝 项目简介

本项目包含我们团队参与数学建模比赛 C 题的完整数据预处理、统计分析、风险预警建模、特征组合挖掘与个性化干预优化代码。

本研究面向中老年人群高血脂症的风险预警与动态干预问题，融合临床生化指标、中医体质积分、活动能力量表、人口学特征与生活习惯等多维度数据，建立了一套兼具**核心指标筛选、风险等级划分、高危组合识别和个体化干预优化**的数学模型体系。

针对问题一，项目构建了融合“高血脂预警能力”与“痰湿体质表征能力”的双维度指标筛选矩阵，筛选出 TG、TC 等核心双效指标，并进一步结合 Logistic 回归、随机森林和 SHAP 方法量化九种中医体质对高血脂风险的贡献差异。

针对问题二，项目构建了多模型交叉验证体系，对 Logistic Regression、Random Forest、LightGBM 和 XGBoost 等模型进行性能对比，最终选取综合表现最优的模型作为风险预警基座。同时，利用浅层决策树提取 TG、TC 与痰湿质积分阈值，建立低、中、高三级风险分层规则，并针对痰湿体质高风险人群挖掘核心恶性特征组合。

针对问题三，项目构建了基于动态规划的 6 个月个性化干预优化模型，在预算、年龄、活动能力和中医调理费用等多重约束下，求解不同患者的最优活动干预强度与频率组合，并总结出受限型、均衡型和激进型三类患者的策略匹配规律。

---

## 💡 核心模型与创新点

本项目主要包含以下三个部分的核心工作：

### 1. 核心双效指标筛选与体质风险贡献分析

* 根据临床正常参考范围，对 TC、TG、LDL-C、HDL-C、空腹血糖、BMI、血尿酸等指标生成异常标签。
* 基于痰湿质积分三分位数，构建低度、中度、高度痰湿体质严重程度分组。
* 结合 Spearman 秩相关分析、卡方检验、t 检验和 ANOVA，分别评估各指标对高血脂风险和痰湿质严重程度的表征能力。
* 构建“双维度筛选矩阵”，将指标的高血脂预警能力与痰湿质表征能力进行联合评价。
* 引入循证医学先验权重，对 TG、TC、BMI、LDL-C、HDL-C、活动量表等指标进行综合排序。
* 采用多因素 Logistic 回归和随机森林 SHAP 解释框架，量化九种中医体质对高血脂风险的非线性贡献。

### 2. 多维度高血脂风险预警与高危组合识别

* 融合生化指标、中医体质积分、活动量表、年龄、性别、吸烟史和饮酒史等多维特征。
* 构建 Logistic Regression、Random Forest、LightGBM 和 XGBoost 多模型交叉验证体系。
* 使用 AUC、F1、Accuracy、Precision、Recall 和 KS 统计量综合评估模型性能。
* 选取综合性能最优的模型输出个体高血脂预测概率。
* 利用浅层 CART 决策树提取可解释阈值，构建低风险、中风险和高风险三级分层规则。
* 聚焦痰湿体质人群，结合 t 检验、决策树和 Apriori 关联规则，挖掘“痰湿体质 + TG 偏高”“痰湿体质 + TC 偏高”“痰湿体质 + TC 偏高 + 活动量低”等核心高危组合。

### 3. 基于动态规划的个性化干预优化模型

* 以 6 个月干预周期末的痰湿体质积分最低为目标函数。
* 将每月活动干预强度和每周训练频率作为决策变量。
* 综合考虑 2000 元预算约束、中医调理费用、活动干预费用、年龄耐受上限和活动能力耐受上限。
* 构建痰湿积分动态状态转移方程，描述每月干预强度、频率与积分下降率之间的关系。
* 使用动态规划算法全局搜索最优干预方案，避免贪心策略陷入局部最优。
* 对 1、2、3 号典型患者输出逐月最优方案，并总结三类患者匹配规律：

  * 受限型患者：强度和频率均受限，适合低强度稳定干预；
  * 均衡型患者：强度可适当提升，适合中强度高频干预；
  * 激进型患者：耐受能力较强，适合动态跃迁式高强度干预。

---

## 📂 核心文件结构

本仓库按照题目三问进行模块化拆分，推荐文件结构如下：

```text
.
├── data.xlsx
├── data_preprocessed.xlsx
├── data_with_proba.xlsx
├── data_with_risk.xlsx
├── README.md
│
├── Q1_Core_Indicator_Screening/
│   ├── data_preprocessing_feature_labeling.py
│   ├── hyperlipidemia_statistical_association.py
│   ├── phlegm_dampness_characterization.py
│   ├── dual_dimensional_indicator_screening.py
│   └── constitution_risk_contribution_analysis.py
│
├── Q2_Risk_Warning_and_Pattern_Mining/
│   ├── multimodel_hyperlipidemia_risk_prediction.py
│   ├── three_level_risk_stratification.py
│   └── phlegm_dampness_high_risk_pattern_mining.py
│
└── Q3_Dynamic_Intervention_Optimization/
    ├── intervention_optimization_model_formulation.py
    ├── dynamic_programming_intervention_planning.py
    ├── patient_intervention_strategy_visualization.py
    └── generalized_intervention_strategy_matching.py
```

---

## 📁 文件功能说明

### Q1：核心指标筛选与体质贡献分析

* `data_preprocessing_feature_labeling.py`
  数据预处理模块。读取原始数据 `data.xlsx`，生成血脂/代谢异常标签、痰湿质严重程度分组、活动能力分组和体质文字标签，并输出 `data_preprocessed.xlsx`。

* `hyperlipidemia_statistical_association.py`
  高血脂统计关联分析模块。计算各生化指标与高血脂标签之间的 Spearman 相关系数，并通过卡方检验比较正常组与异常组的发病率差异。

* `phlegm_dampness_characterization.py`
  痰湿体质表征分析模块。分析各指标与痰湿质积分、痰湿严重程度和痰湿体质标签之间的统计关系，识别能够表征痰湿质的关键指标。

* `dual_dimensional_indicator_screening.py`
  双维度指标筛选矩阵模块。综合“高血脂预警能力”和“痰湿质表征能力”，并结合先验证据权重，筛选核心双效指标。

* `constitution_risk_contribution_analysis.py`
  体质风险贡献分析模块。利用 Logistic 回归、随机森林和 SHAP 方法量化九种中医体质对高血脂风险的贡献差异。

### Q2：高血脂风险预警与高危组合挖掘

* `multimodel_hyperlipidemia_risk_prediction.py`
  多模型风险预测模块。构建 Logistic Regression、Random Forest、LightGBM 和 XGBoost 模型，进行五折交叉验证和 ROC、PR、KS、混淆矩阵评价，并输出 `data_with_proba.xlsx`。

* `three_level_risk_stratification.py`
  三级风险分层模块。基于浅层决策树提取 TG、TC 和痰湿质阈值，构建低、中、高三级风险分层规则，并输出 `data_with_risk.xlsx`。

* `phlegm_dampness_high_risk_pattern_mining.py`
  痰湿体质高危组合挖掘模块。针对痰湿体质人群，利用 t 检验、决策树和 Apriori 关联规则识别高血脂核心风险组合。

### Q3：动态干预优化与策略匹配

* `intervention_optimization_model_formulation.py`
  干预优化模型建立模块。定义决策变量、目标函数、预算约束、强度约束、频率约束和痰湿积分状态转移方程。

* `dynamic_programming_intervention_planning.py`
  动态规划求解模块。针对 1、2、3 号典型患者，在预算约束下求解 6 个月最优干预方案。

* `patient_intervention_strategy_visualization.py`
  个体化干预方案可视化模块。绘制患者积分下降趋势、月度成本构成和患者特征-方案匹配规律图。

* `generalized_intervention_strategy_matching.py`
  普遍匹配规律总结模块。遍历不同强度上限和初始调理等级组合，提炼患者特征与最优干预策略之间的普遍规律。

---

## 📦 资料下载

为了保持代码仓库的纯净与轻量，原始题目说明、数据集和完整论文 PDF 可通过网盘或比赛资料包获取。

* 🔗 百度网盘链接：`请在此处填写链接`
* 🔑 提取码：`请在此处填写提取码`

**⚠️ 数据放置指南：**

下载并解压资料包后，请将原始数据文件命名为：

```text
data.xlsx
```

并放置在本项目根目录下。部分模块运行后会自动生成以下中间文件：

```text
data_preprocessed.xlsx
data_with_proba.xlsx
data_with_risk.xlsx
```

这些中间文件具有前后依赖关系，请按照推荐顺序运行代码。

---

## 🚀 快速开始

### 1. 环境配置

建议使用 Python 3.10 及以上版本。项目主要依赖如下：

```bash
pip install pandas numpy matplotlib scipy scikit-learn lightgbm xgboost shap statsmodels mlxtend openpyxl
```

如已配置 `requirements.txt`，也可以直接运行：

```bash
pip install -r requirements.txt
```

### 2. 数据准备

请确保项目根目录下存在原始数据文件：

```text
data.xlsx
```

如果缺少该文件，后续所有模块都无法正常运行。

### 3. 推荐运行顺序

由于各模块存在数据依赖，建议按照以下顺序运行。

```bash
# 第一问：数据预处理与核心指标筛选
python Q1_Core_Indicator_Screening/data_preprocessing_feature_labeling.py
python Q1_Core_Indicator_Screening/hyperlipidemia_statistical_association.py
python Q1_Core_Indicator_Screening/phlegm_dampness_characterization.py
python Q1_Core_Indicator_Screening/dual_dimensional_indicator_screening.py
python Q1_Core_Indicator_Screening/constitution_risk_contribution_analysis.py

# 第二问：风险预警模型与高危组合识别
python Q2_Risk_Warning_and_Pattern_Mining/multimodel_hyperlipidemia_risk_prediction.py
python Q2_Risk_Warning_and_Pattern_Mining/three_level_risk_stratification.py
python Q2_Risk_Warning_and_Pattern_Mining/phlegm_dampness_high_risk_pattern_mining.py

# 第三问：动态干预优化与策略匹配
python Q3_Dynamic_Intervention_Optimization/intervention_optimization_model_formulation.py
python Q3_Dynamic_Intervention_Optimization/dynamic_programming_intervention_planning.py
python Q3_Dynamic_Intervention_Optimization/patient_intervention_strategy_visualization.py
python Q3_Dynamic_Intervention_Optimization/generalized_intervention_strategy_matching.py
```

---

## 🔗 模块依赖关系

本项目的主要数据流如下：

```text
data.xlsx
   ↓
data_preprocessing_feature_labeling.py
   ↓
data_preprocessed.xlsx
   ↓
multimodel_hyperlipidemia_risk_prediction.py
   ↓
data_with_proba.xlsx
   ↓
three_level_risk_stratification.py
   ↓
data_with_risk.xlsx
   ↓
dynamic_programming_intervention_planning.py
patient_intervention_strategy_visualization.py
generalized_intervention_strategy_matching.py
```

其中：

* `data_preprocessed.xlsx` 是第一问后续统计分析和第二问建模的基础数据；
* `data_with_proba.xlsx` 保存了最优模型输出的个体高血脂预测概率；
* `data_with_risk.xlsx` 保存了低、中、高三级风险标签，是第三问干预优化模型的输入数据。

---

## 📊 输出结果说明

运行完整项目后，可以得到以下主要结果：

1. **数据预处理结果**

   * 血脂/代谢指标异常标签；
   * 痰湿质严重程度分组；
   * 活动能力分组；
   * 体质标签文字映射。

2. **第一问结果**

   * 各指标与高血脂风险的 Spearman 相关性；
   * 各指标异常状态与高血脂发病率的卡方检验结果；
   * 痰湿质人群的指标异常特征；
   * 双维度核心指标筛选矩阵；
   * 九种体质的 Logistic 回归 OR 值和 SHAP 贡献排序。

3. **第二问结果**

   * 多模型预测性能对比；
   * ROC 曲线、PR 曲线、KS 曲线和混淆矩阵；
   * 三级风险分层阈值；
   * 低、中、高风险人群画像；
   * 痰湿体质高风险人群核心特征组合。

4. **第三问结果**

   * 6 个月干预优化模型；
   * 三位典型患者逐月最优干预策略；
   * 每月痰湿积分变化轨迹；
   * 每月成本构成；
   * 患者特征与最优干预方案匹配规律。

---

## 🧠 主要结论

本项目最终得到以下核心结论：

1. **TG 和 TC 是中老年高血脂预警与痰湿质表征的核心双效指标。**
   它们既能显著预警高血脂发病风险，又能在痰湿体质人群中表现出较强的病理关联。

2. **痰湿体质是高血脂慢病防变中的重要干预靶位。**
   通过 Logistic 回归、随机森林和 SHAP 分析可见，体质积分与生活行为特征共同参与高血脂风险形成。

3. **多维特征融合模型能够显著提升高血脂风险识别能力。**
   融合生化指标、中医体质、活动能力和人口学信息后，模型具有较强的高低风险区分能力。

4. **TG、TC 与痰湿质积分可用于构建清晰可解释的三级风险分层规则。**
   浅层决策树提取出的阈值与临床正常参考范围高度接近，具有较好的医学解释性。

5. **痰湿体质叠加 TG 偏高、TC 偏高和活动量低时，会形成高危特征组合。**
   该类人群应作为基层慢病筛查和个性化干预的重点对象。

6. **动态规划可有效解决预算约束下的个性化干预优化问题。**
   在 6 个月干预周期中，模型能够根据患者年龄、活动能力和痰湿积分水平自动匹配最优干预强度与频率。

7. **活动能力是决定干预效果上限的关键因素。**
   患者的活动量表评分同时影响活动强度上限和频率上限，是决定最终干预效果的重要约束。

---

## 👥 作者与致谢

* 💻 编程实现：应岂池
* 🧮 建模与分析：赵耀
* 📝 论文撰写：李志聪
* 🏷️ 队伍编号：MC2603921

如有问题可随时联系。禁止二次销售，版权归团队所有。

---

## 📄 许可证

本项目采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh) 协议授权。

你可以自由地分享和改编本项目内容，但须遵守以下条件：

* **署名**：必须注明原作者及出处；
* **非商业性使用**：禁止将本项目内容用于任何商业目的，包括但不限于销售、代写、卖课等行为。

© 2026 Team MC2603921
