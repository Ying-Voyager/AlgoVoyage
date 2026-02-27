
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, classification_report


file_path = "女胎预处理后数据.xlsx"
label_col = "染色体的非整倍体"
gc_cols   = ["13号染色体的GC含量", "18号染色体的GC含量", "21号染色体的GC含量"]

TEST_SIZE    = 0.2
RANDOM_STATE = 42
SMOTE_K      = 5


M_MIN, M_MAX, M_STEPS = -0.20, -0.0002, 2000
CROSS_REWARD, CIRCLE_REWARD = 7.92, 1.0



def compute_gc_cv(df, cols):
    X = df[cols].astype(float).to_numpy()
    X = np.where(np.isfinite(X), X, np.nan)
    mu  = np.nanmean(X, axis=1)
    sig = np.nanstd(X, axis=1, ddof=0)
    cv  = sig / np.where(mu == 0, np.nan, mu)
    return pd.Series(cv, index=df.index).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def best_line_by_score(x, y, y_true, m_min, m_max, m_steps,
                       cross_reward=2.0, circle_reward=1.0):

    x = np.asarray(x); y = np.asarray(y); y_true = np.asarray(y_true).astype(int)
    n = len(x)
    tot_pos = y_true.sum()
    tot_neg = n - tot_pos
    max_possible = cross_reward*tot_pos + circle_reward*tot_neg

    m_grid = np.linspace(m_min, m_max, m_steps)
    best   = (None, None, -np.inf)

    for m in m_grid:
        r = y - m*x
        order = np.argsort(r)
        r_s, y_s = r[order], y_true[order]

        pos, neg = y_s, 1 - y_s
        cum_pos = np.concatenate(([0], np.cumsum(pos)))
        cum_neg = np.concatenate(([0], np.cumsum(neg)))

        TP = cum_pos
        TN = tot_neg - cum_neg
        score = cross_reward*TP + circle_reward*TN

        i = int(np.argmax(score))
        if i == 0:      a = r_s[0] - 1e-12
        elif i == n:    a = r_s[-1] + 1e-12
        else:           a = 0.5*(r_s[i-1] + r_s[i])

        if score[i] > best[2]:
            best = (m, a, float(score[i]))

    return best[0], best[1], best[2], max_possible


def main():

    df = pd.read_excel(file_path)
    assert label_col in df.columns
    for c in gc_cols:
        if c not in df.columns:
            raise ValueError(f"缺列：{c}")

    y_all = pd.to_numeric(df[label_col], errors="coerce").fillna(0).clip(0,1).astype(int).values
    df["GC变异系数"] = compute_gc_cv(df, gc_cols)
    yaxis_all = df["GC变异系数"].values


    X = df.select_dtypes(include=[np.number]).drop(columns=[label_col, "GC变异系数"], errors="ignore") \
         .fillna(method="ffill").fillna(method="bfill")
    X = X.fillna(X.median())


    Xtr, Xte, ytr, yte, ytr_axis, yte_axis = train_test_split(
        X.values, y_all, yaxis_all, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_all
    )
    print("训练集原始分布:", Counter(ytr))

    binc = np.bincount(ytr)
    k_eff = max(1, min(SMOTE_K, binc.min()-1))
    smote = SMOTE(random_state=RANDOM_STATE, k_neighbors=k_eff)
    Xtr_res, ytr_res = smote.fit_resample(Xtr, ytr)
    print(f"SMOTE(k={k_eff}) 后分布:", Counter(ytr_res))

    gnb = GaussianNB().fit(Xtr_res, ytr_res)
    p_tr = gnb.predict_proba(Xtr)[:,1]
    p_te = gnb.predict_proba(Xte)[:,1]


    m_tr, a_tr, sc_tr, sc_tr_max = best_line_by_score(
        p_tr, ytr_axis, ytr, M_MIN, M_MAX, M_STEPS, CROSS_REWARD, CIRCLE_REWARD
    )
    m_te, a_te, sc_te, sc_te_max = best_line_by_score(
        p_te, yte_axis, yte, M_MIN, M_MAX, M_STEPS, CROSS_REWARD, CIRCLE_REWARD
    )
    print(f"\n[Train最优线] m={m_tr:.6f}, a={a_tr:.6f}, 训练得分={sc_tr:.1f}/{sc_tr_max:.1f} ({sc_tr/sc_tr_max:.2%})")
    print(f"[Test最优线 ] m={m_te:.6f}, a={a_te:.6f}, 测试得分={sc_te:.1f}/{sc_te_max:.1f} ({sc_te/sc_te_max:.2%})")


    y_pred_testline = (yte_axis <= a_te + m_te * p_te).astype(int)
    print("\n=== 基于【测试集最优线】在测试集上的混淆矩阵 ===")
    print("混淆矩阵 [TN FP; FN TP]:\n", confusion_matrix(yte, y_pred_testline))
    print(classification_report(yte, y_pred_testline, digits=4))


    y_pred_trainline_on_test = (yte_axis <= a_tr + m_tr * p_te).astype(int)
    print("\n=== 基于【训练集最优线】在测试集上的混淆矩阵 ===")
    print("混淆矩阵 [TN FP; FN TP]:\n", confusion_matrix(yte, y_pred_trainline_on_test))
    print(classification_report(yte, y_pred_trainline_on_test, digits=4))


    plt.rcParams['font.sans-serif'] = ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 24
    plt.rcParams['axes.titlesize'] = 26
    plt.rcParams['axes.labelsize'] = 24
    plt.rcParams['xtick.labelsize'] = 22
    plt.rcParams['ytick.labelsize'] = 22
    plt.rcParams['legend.fontsize'] = 22

    fig = plt.figure(figsize=(12, 6.2))
    ax = plt.gca()

    m0 = (yte == 0); m1 = (yte == 1)
    ax.scatter(p_te[m0], yte_axis[m0], s=80, marker='o', alpha=0.85, label='真实=0（正常）')
    ax.scatter(p_te[m1], yte_axis[m1], s=100, marker='x', alpha=0.95, label='真实=1（异常）')

    ymin, ymax = np.percentile(yte_axis, [0.5, 99.5])
    pad = 0.2*max(ymax - ymin, 1e-4)
    ax.set_ylim(ymin - pad, ymax + pad)

    xL, xR = ax.get_xlim()
    xx = np.linspace(xL, xR, 400)
    yy_tr = a_tr + m_tr*xx
    yy_te = a_te + m_te*xx
    vis_tr = (yy_tr >= ax.get_ylim()[0]) & (yy_tr <= ax.get_ylim()[1])
    vis_te = (yy_te >= ax.get_ylim()[0]) & (yy_te <= ax.get_ylim()[1])
    if vis_tr.any():
        ax.plot(xx[vis_tr], yy_tr[vis_tr], linestyle='--', lw=2.2, color='#d62728',
                label=f'训练最优线')
    if vis_te.any():
        ax.plot(xx[vis_te], yy_te[vis_te], linestyle='-',  lw=2.5, color='#1f77b4',
                label=f'测试最优线')

    ax.set_xlabel("患病概率  p(异常 | X)")
    ax.set_ylabel("GC变异系数（σ/μ）")
    ax.set_title("SMOTE + 朴素贝叶斯：概率 vs GC 变异系数")
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
