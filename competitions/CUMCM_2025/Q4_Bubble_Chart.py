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

USE_MU_SIGMA_IN_MODEL = False
B_PR = (-3.0, 3.0, 81)
C_PR = (-3.0, 3.0, 81)

R_CROSS = 8.0
R_CIRC  = 1.0

TEST_SIZE = 0.2
SEED = 42
SMOTE_K = 5


def gc_mu_sigma(df: pd.DataFrame, cols):
    X = df[cols].astype(float).to_numpy()
    X = np.where(np.isfinite(X), X, np.nan)
    mu = np.nanmean(X, axis=1)
    sg = np.nanstd(X, axis=1, ddof=0)
    return (pd.Series(mu, index=df.index).fillna(0.0),
            pd.Series(sg, index=df.index).fillna(0.0))


def best_thresh(r_sorted, y_sorted, cross_reward=8.0, circle_reward=1.0):
    n = len(r_sorted)
    y = y_sorted.astype(int)
    cum_pos = np.concatenate(([0], np.cumsum(y)))
    cum_neg = np.concatenate(([0], np.cumsum(1 - y)))
    TP = int(y.sum()) - cum_pos
    TN = cum_neg
    score = cross_reward * TP + circle_reward * TN
    i = int(np.argmax(score))
    if n == 0:
        return 0.0, 0.0
    if i == 0:
        a_p = r_sorted[0] - 1e-12
    elif i == n:
        a_p = r_sorted[-1] + 1e-12
    else:
        a_p = 0.5 * (r_sorted[i - 1] + r_sorted[i])
    return a_p, float(score[i])


def search_plane(mu_tr, sg_tr, z_tr, y_tr, b_range, c_range, cross_reward=8.0, circle_reward=1.0):
    mu_tr = np.asarray(mu_tr); sg_tr = np.asarray(sg_tr)
    z_tr = np.asarray(z_tr);   y_tr = np.asarray(y_tr).astype(int)

    mx, sx = mu_tr.mean(), mu_tr.std(ddof=0)
    my, sy = sg_tr.mean(), sg_tr.std(ddof=0)
    sx = sx if sx > 0 else 1.0
    sy = sy if sy > 0 else 1.0
    mu_z = (mu_tr - mx) / sx
    sg_z = (sg_tr - my) / sy

    bmin, bmax, bsteps = b_range
    cmin, cmax, csteps = c_range
    b_grid = np.linspace(bmin, bmax, int(bsteps))
    c_grid = np.linspace(cmin, cmax, int(csteps))

    best = dict(score=-np.inf)
    for b_p in b_grid:
        base = z_tr - b_p * mu_z
        for c_p in c_grid:
            r = base - c_p * sg_z
            idx = np.argsort(r)
            a_p, sc = best_thresh(r[idx], y_tr[idx], cross_reward, circle_reward)
            if sc > best.get("score", -np.inf):
                b = b_p / sx
                c = c_p / sy
                a = a_p - b_p * (mx / sx) - c_p * (my / sy)
                best.update(dict(a=a, b=b, c=c, a_p=a_p, b_p=b_p, c_p=c_p,
                                 score=sc, mx=mx, sx=sx, my=my, sy=sy))
    return best


def predict_plane(mu, sg, z, p):
    return (z >= (p["a"] + p["b"] * mu + p["c"] * sg)).astype(int)


def score_weighted(y_true, y_pred, cross_reward=8.0, circle_reward=1.0):
    y_true = y_true.astype(int); y_pred = y_pred.astype(int)
    TP = int(((y_true == 1) & (y_pred == 1)).sum())
    TN = int(((y_true == 0) & (y_pred == 0)).sum())
    return cross_reward * TP + circle_reward * TN, TP, TN


def main():
    df = pd.read_excel(FILE)
    assert YCOL in df.columns, f"未找到目标列：{YCOL}"
    for c in GC_COLS:
        if c not in df.columns:
            raise ValueError(f"未找到列：{c}")

    y_all = pd.to_numeric(df[YCOL], errors="coerce").fillna(0).clip(0, 1).astype(int).values

    mu_all, sg_all = gc_mu_sigma(df, GC_COLS)
    df["GC均值_作图"] = mu_all
    df["GC标准差_作图"] = sg_all

    Xn = df.select_dtypes(include=[np.number]).copy()
    drop = [YCOL]
    if not USE_MU_SIGMA_IN_MODEL:
        drop += ["GC均值_作图", "GC标准差_作图"]
    Xn = Xn.drop(columns=drop, errors="ignore").fillna(Xn.median())

    X_tr, X_te, y_tr, y_te, mu_tr, mu_te, sg_tr, sg_te = train_test_split(
        Xn.values, y_all, mu_all.values, sg_all.values,
        test_size=TEST_SIZE, random_state=SEED, stratify=y_all
    )
    print("训练集原始分布:", Counter(y_tr))

    binc = np.bincount(y_tr)
    k_eff = max(1, min(SMOTE_K, binc.min() - 1))
    sm = SMOTE(random_state=SEED, k_neighbors=k_eff)
    X_tr_res, y_tr_res = sm.fit_resample(X_tr, y_tr)
    print(f"SMOTE(k={k_eff}) 后分布:", Counter(y_tr_res))

    clf = GaussianNB()
    clf.fit(X_tr_res, y_tr_res)

    z_tr = clf.predict_proba(X_tr)[:, 1]
    z_te = clf.predict_proba(X_te)[:, 1]

    best = search_plane(
        mu_tr, sg_tr, z_tr, y_tr,
        B_PR, C_PR, cross_reward=R_CROSS, circle_reward=R_CIRC
    )
    a, b, c = best["a"], best["b"], best["c"]
    print("\n=== 训练得到的最优判别条件（最大化 8*TP + 1*TN） ===")
    print(f"  预测1(异常) 当 z >= a + b*mu + c*sigma")
    print(f"  a={a:.6g}, b={b:.6g}, c={c:.6g}")

    y_hat_tr = predict_plane(mu_tr, sg_tr, z_tr, best)
    y_hat_te = predict_plane(mu_te, sg_te, z_te, best)

    tr_score, TP_tr, TN_tr = score_weighted(y_tr, y_hat_tr, R_CROSS, R_CIRC)
    te_score, TP_te, TN_te = score_weighted(y_te, y_hat_te, R_CROSS, R_CIRC)

    tr_max = R_CROSS * int(y_tr.sum()) + R_CIRC * int((y_tr == 0).sum())
    te_max = R_CROSS * int(y_te.sum()) + R_CIRC * int((y_te == 0).sum())

    print(f"\n训练集：得分 = {tr_score:.1f} / {tr_max:.1f}  (TP={TP_tr}, TN={TN_tr})")
    print("训练集混淆矩阵 [TN FP; FN TP]:\n", confusion_matrix(y_tr, y_hat_tr))
    print(classification_report(y_tr, y_hat_tr, digits=4))

    print(f"\n测试集：得分 = {te_score:.1f} / {te_max:.1f}  (TP={TP_te}, TN={TN_te})")
    print("测试集混淆矩阵 [TN FP; FN TP]:\n", confusion_matrix(y_te, y_hat_te))
    print(classification_report(y_te, y_hat_te, digits=4))

    print(f"(参考) ROC-AUC={roc_auc_score(y_te, z_te):.4f}, PR-AUC={average_precision_score(y_te, z_te):.4f}")

    plt.rcParams.update({
        'font.sans-serif': ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'WenQuanYi Micro Hei', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.size': 22,
        'axes.titlesize': 24,
        'axes.labelsize': 22,
        'xtick.labelsize': 20,
        'ytick.labelsize': 20,
        'legend.fontsize': 20,
    })

    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    zc = np.clip(z_te, 0, 1)
    sizes = (zc ** 2) * 3000 + 50
    c0, c1 = '#4C72B0', '#C44E52'
    m0, m1 = (y_te == 0), (y_te == 1)

    ax.scatter(mu_te[m0], sg_te[m0], s=sizes[m0], c=c0, alpha=0.75, marker='o',
               edgecolors='k', linewidths=0.6, label='真实=0（正常）')
    ax.scatter(mu_te[m1], sg_te[m1], s=sizes[m1], c=c1, alpha=0.85, marker='o',
               edgecolors='k', linewidths=0.6, label='真实=1（异常）')

    ax.set_xlabel("GC均值 μ（13/18/21）")
    ax.set_ylabel("GC标准差 σ（ddof=0）")
    ax.set_title("2D 概率气泡图：颜色=真实标签，气泡大小=患病概率")
    ax.legend(loc='best', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.35)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
