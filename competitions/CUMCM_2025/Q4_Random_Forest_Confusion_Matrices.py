import pandas as pd
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, average_precision_score
)


file_path ="女胎预处理后数据.xlsx"
df = pd.read_excel(file_path)
y = df["染色体的非整倍体"]
X = df.drop(columns=["染色体的非整倍体"])


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("训练集原始分布:", Counter(y_train))
print("测试集原始分布:", Counter(y_test))


def plot_confusion_matrix(cm, labels, tick_labels, title, save_path):
    plt.rcParams['font.sans-serif'] = ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 24
    plt.rcParams['xtick.labelsize'] = 22
    plt.rcParams['ytick.labelsize'] = 22
    plt.rcParams['axes.labelsize'] = 26
    plt.rcParams['axes.titlesize'] = 26

    fig, ax = plt.subplots(figsize=(7, 7))
    im = ax.imshow(cm, interpolation='nearest', cmap='Blues')

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=16)

    ax.set(
        xticks=np.arange(len(labels)),
        yticks=np.arange(len(labels)),
        xticklabels=tick_labels,
        yticklabels=tick_labels,
        xlabel='预测 (Predicted)',
        ylabel='真实 (Actual)',
        title=title
    )
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

    row_sums = cm.sum(axis=1, keepdims=True)
    th = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            pct = (cm[i, j] / row_sums[i, 0] * 100) if row_sums[i, 0] > 0 else 0.0
            ax.text(j, i, f"{cm[i, j]}\n({pct:.1f}%)",
                    ha="center", va="center", fontweight='bold', fontsize=20,
                    color="white" if cm[i, j] > th else "black")

    ax.set_xticks(np.arange(-.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.show()
    print("已保存：", save_path)



print("\n=== 方案A：SMOTE + RF ===")
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
print("训练集SMOTE后分布:", Counter(y_train_res))

modelA = RandomForestClassifier(random_state=42)
modelA.fit(X_train_res, y_train_res)

y_predA = modelA.predict(X_test)
print("\n=== 在原始测试集上的评估结果（SMOTE训练） ===")
print(confusion_matrix(y_test, y_predA))
print(classification_report(y_test, y_predA))

if hasattr(modelA, "predict_proba"):
    y_probA = modelA.predict_proba(X_test)[:, 1]
    print(f"ROC-AUC: {roc_auc_score(y_test, y_probA):.4f}")
    print(f"PR-AUC : {average_precision_score(y_test, y_probA):.4f}")

cmA = confusion_matrix(y_test, y_predA, labels=[0,1])
plot_confusion_matrix(cmA, [0,1], ["0(阴性)","1(阳性)"], "混淆矩阵（SMOTE训练）", "confusion_matrix_smote.png")



print("\n=== 方案B：原始训练集 + RF ===")
modelB = RandomForestClassifier(random_state=42)
modelB.fit(X_train, y_train)

y_predB = modelB.predict(X_test)
print("\n=== 在原始测试集上的评估结果（无SMOTE） ===")
print(confusion_matrix(y_test, y_predB))
print(classification_report(y_test, y_predB))

if hasattr(modelB, "predict_proba"):
    y_probB = modelB.predict_proba(X_test)[:, 1]
    print(f"ROC-AUC: {roc_auc_score(y_test, y_probB):.4f}")
    print(f"PR-AUC : {average_precision_score(y_test, y_probB):.4f}")

cmB = confusion_matrix(y_test, y_predB, labels=[0,1])
plot_confusion_matrix(cmB, [0,1], ["0(阴性)","1(阳性)"], "混淆矩阵（无SMOTE）", "confusion_matrix_raw.png")
