import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_auc_score, average_precision_score
)

FILE = "女胎预处理后数据.xlsx"
YCOL = "染色体的非整倍体"
GC_COLS = ["13号染色体的GC含量", "18号染色体的GC含量", "21号染色体的GC含量"]

# 1) 读取 & GC 变异系数
df = pd.read_excel(FILE)
assert YCOL in df.columns, f"未找到目标列：{YCOL}"
for c in GC_COLS:
    if c not in df.columns:
        raise ValueError(f"未找到列：{c}")

gc = df[GC_COLS].astype(float)
gc_mean = gc.mean(axis=1).replace(0, np.nan)
gc_std = gc.std(axis=1, ddof=0)
df["GC变异系数"] = (gc_std / gc_mean).fillna(0.0)

# 2) 特征（数值列）& 缺失处理
y = df[YCOL].astype(int).values
X = df.select_dtypes(include=[np.number]).drop(columns=[YCOL], errors="ignore")
X = X.fillna(X.median())
gc_cv = df["GC变异系数"].values

# 3) 划分
X_tr, X_te, y_tr, y_te, cv_tr, cv_te = train_test_split(
    X.values, y, gc_cv, test_size=0.2, random_state=42, stratify=y
)
print("训练集原始分布:", Counter(y_tr))

# 4) 仅训练集 SMOTE
smote = SMOTE(random_state=42, k_neighbors=5)
X_tr_res, y_tr_res = smote.fit_resample(X_tr, y_tr)
print("训练集SMOTE后分布:", Counter(y_tr_res))

# 5) 训练
clf = GaussianNB()
clf.fit(X_tr_res, y_tr_res)

# 6) 测试集评估 & 概率
p_te = clf.predict_proba(X_te)[:, 1]
y_hat = (p_te >= 0.5).astype(int)

print("\n=== 测试集评估（GaussianNB, 训练集SMOTE） ===")
print("混淆矩阵 [TN FP; FN TP]:\n", confusion_matrix(y_te, y_hat))
print(classification_report(y_te, y_hat, digits=4))
try:
    print(f"ROC-AUC: {roc_auc_score(y_te, p_te):.4f}")
    print(f"PR-AUC : {average_precision_score(y_te, p_te):.4f}")
except Exception as e:
    print("AUC 计算失败：", e)

# 7) 字体（在原基础上 +6）
plt.rcParams['font.sans-serif'] = ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
_size_map = {
    'xx-small': 16, 'x-small': 18, 'small': 15, 'medium': 18,
    'large': 20, 'x-large': 22, 'xx-large': 24, 'smaller': 16, 'larger': 20
}
def _inc(key, delta=6, default=10):
    v = plt.rcParams.get(key, default)
    if isinstance(v, str):
        v = _size_map.get(v.lower(), default)
    try:
        return float(v) + delta
    except Exception:
        return default + delta

plt.rcParams['font.size']       = _inc('font.size',       6, 10)
plt.rcParams['axes.titlesize']  = _inc('axes.titlesize',  6, 12)
plt.rcParams['axes.labelsize']  = _inc('axes.labelsize',  6, 10)
plt.rcParams['xtick.labelsize'] = _inc('xtick.labelsize', 6, 9)
plt.rcParams['ytick.labelsize'] = _inc('ytick.labelsize', 6, 9)
plt.rcParams['legend.fontsize'] = _inc('legend.fontsize', 6, 9)

# 8) 可视化：x=患病概率, y=GC变异系数；0=圆圈，1=叉号
fig, ax = plt.subplots(figsize=(10.5, 6.0))
m0, m1 = (y_te == 0), (y_te == 1)

ax.scatter(p_te[m0], cv_te[m0], marker='o', s=70, alpha=0.8, label='真实=0（正常）')
ax.scatter(p_te[m1], cv_te[m1], marker='x', s=90, alpha=0.95, label='真实=1（异常）')

ax.axvline(0.5, ls='--', lw=1.2, label='阈值=0.5')
ax.set_xlabel("患病概率  p(异常 | X)")
ax.set_ylabel("GC变异系数（13/18/21）")
ax.set_title("SMOTE + GaussianNB：概率 vs GC变异系数（测试集）")
ax.grid(True, ls='--', alpha=0.3)
ax.legend()
plt.tight_layout()
plt.show()
