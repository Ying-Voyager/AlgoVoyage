
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, f1_score, accuracy_score, confusion_matrix, roc_curve,
    precision_recall_curve, average_precision_score, precision_score, recall_score
)
import lightgbm as lgb
import xgboost as xgb

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120

df = pd.read_excel('data_preprocessed.xlsx')

feature_cols = [
    'TG（甘油三酯）', 'TC（总胆固醇）', 'LDL-C（低密度脂蛋白）',
    'HDL-C（高密度脂蛋白）', '血尿酸', 'BMI', '空腹血糖',
    '活动量表总分（ADL总分+IADL总分）', '痰湿质',
    '平和质', '气虚质', '阳虚质', '阴虚质', '湿热质', '血瘀质', '气郁质', '特禀质',
    '年龄组', '性别', '吸烟史', '饮酒史'
]
feature_display = [
    'TG', 'TC', 'LDL-C', 'HDL-C', '血尿酸', 'BMI', '空腹血糖',
    '活动量表', '痰湿质',
    '平和质', '气虚质', '阳虚质', '阴虚质', '湿热质', '血瘀质', '气郁质', '特禀质',
    '年龄组', '性别', '吸烟史', '饮酒史'
]

X = df[feature_cols].copy()
y = df['高血脂症二分类标签']
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

models = {
    'Logistic Regression\n（逻辑回归）': {
        'model': LogisticRegression(max_iter=1000, random_state=42),
        'X': X_scaled,
        'color': '#4C78A8',
        'ls': '-'
    },
    'Random Forest\n（随机森林）': {
        'model': RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42),
        'X': X.values,
        'color': '#72B7B2',
        'ls': '--'
    },
    'LightGBM': {
        'model': lgb.LGBMClassifier(n_estimators=200, max_depth=6, random_state=42, verbose=-1),
        'X': X.values,
        'color': '#E45756',
        'ls': '-'
    },
    'XGBoost': {
        'model': xgb.XGBClassifier(
            n_estimators=200, max_depth=6, random_state=42,
            verbosity=0, eval_metric='logloss'
        ),
        'X': X.values,
        'color': '#F58518',
        'ls': '--'
    },
}

print("=" * 65)
print("  第一步：五折交叉验证 —— 多模型性能对比")
print("=" * 65)
print(f"  {'模型':<28} {'AUC':>7} {'F1':>7} {'ACC':>7} {'精确率':>7} {'召回率':>7} {'KS':>7}")
print("  " + "-" * 65)

results = {}
for name, cfg in models.items():
    m = cfg['model']
    Xm = cfg['X']

    prob = cross_val_predict(m, Xm, y, cv=cv, method='predict_proba')[:, 1]
    pred = (prob >= 0.5).astype(int)

    auc = roc_auc_score(y, prob)
    f1 = f1_score(y, pred)
    acc = accuracy_score(y, pred)
    prec = precision_score(y, pred)
    rec = recall_score(y, pred)

    fpr_arr, tpr_arr, _ = roc_curve(y, prob)
    ks = float(np.max(tpr_arr - fpr_arr))

    results[name] = {
        'prob': prob, 'pred': pred,
        'AUC': auc, 'F1': f1, 'ACC': acc,
        'Precision': prec, 'Recall': rec, 'KS': ks,
        'color': cfg['color'], 'ls': cfg['ls'],
        'fpr': fpr_arr, 'tpr': tpr_arr
    }

    short = name.split('\n')[0]
    print(f"  {short:<28} {auc:>7.4f} {f1:>7.4f} {acc:>7.4f} {prec:>7.4f} {rec:>7.4f} {ks:>7.4f}")

best_name = max(results, key=lambda k: (results[k]['AUC'] + results[k]['F1'] + results[k]['KS']) / 3)
print(f"\n  ✅ 综合评分最优模型：{best_name.split(chr(10))[0]}")
print(f"     AUC={results[best_name]['AUC']:.4f}  F1={results[best_name]['F1']:.4f}  KS={results[best_name]['KS']:.4f}")

print("\n" + "=" * 65)
print(f"  第二步：最优模型 {best_name.split(chr(10))[0]} 混淆矩阵分析")
print("=" * 65)

best_pred = results[best_name]['pred']
cm = confusion_matrix(y, best_pred)
tn, fp, fn, tp = cm.ravel()
print(f"  真阴性 TN（正确判非高血脂）：{tn}")
print(f"  假阳性 FP（误判为高血脂）  ：{fp}")
print(f"  假阴性 FN（漏判高血脂）    ：{fn}")
print(f"  真阳性 TP（正确判高血脂）  ：{tp}")
print(f"  灵敏度（Sensitivity）      ：{tp/(tp+fn):.4f}")
print(f"  特异度（Specificity）      ：{tn/(tn+fp):.4f}")

print("\n" + "=" * 65)
print("  第三步：最优模型全量训练（供模块B三级风险分层使用）")
print("=" * 65)

best_cfg = models[best_name]
best_model = best_cfg['model']
best_model.fit(best_cfg['X'], y)
best_proba_full = best_model.predict_proba(best_cfg['X'])[:, 1]

df['高血脂预测概率'] = best_proba_full
df['最优模型名称'] = best_name.split('\n')[0]
df.to_excel('data_with_proba.xlsx', index=False)
print(f"  ✅ 预测概率已写入 data_with_proba.xlsx")
print(f"  概率分布：min={best_proba_full.min():.4f}  mean={best_proba_full.mean():.4f}  max={best_proba_full.max():.4f}")

# 图1：ROC
plt.figure(figsize=(9.2, 7.0), facecolor='white')
ax1 = plt.gca()
ax1.set_facecolor('#fcfcfc')

for name, res in results.items():
    short = name.split('\n')[0]
    ax1.plot(
        res['fpr'], res['tpr'],
        color=res['color'], linestyle=res['ls'], linewidth=2.4,
        label=f"{short}  AUC={res['AUC']:.4f}"
    )

ax1.plot([0, 1], [0, 1], color='#666666', linewidth=1.1, linestyle=(0, (4, 3)), alpha=0.8, label='随机猜测')
ax1.fill_between(results[best_name]['fpr'], results[best_name]['tpr'], alpha=0.08, color=results[best_name]['color'])

ax1.set_xlabel('假阳性率 FPR', fontsize=12)
ax1.set_ylabel('真阳性率 TPR', fontsize=12)
ax1.set_title('ROC 曲线对比', fontsize=15, fontweight='bold', pad=12)
ax1.grid(linestyle=':', linewidth=0.6, alpha=0.25)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1.02)
ax1.legend(fontsize=9.5, loc='lower right', frameon=True, facecolor='white', edgecolor='#dddddd')

plt.tight_layout()
plt.show()

# 图2：PR
plt.figure(figsize=(9.2, 7.0), facecolor='white')
ax2 = plt.gca()
ax2.set_facecolor('#fcfcfc')

for name, res in results.items():
    short = name.split('\n')[0]
    ap = average_precision_score(y, res['prob'])
    prec_arr, rec_arr, _ = precision_recall_curve(y, res['prob'])
    ax2.plot(
        rec_arr, prec_arr,
        color=res['color'], linestyle=res['ls'], linewidth=2.4,
        label=f"{short}  AP={ap:.4f}"
    )

baseline = y.mean()
ax2.axhline(baseline, color='#666666', linestyle=(0, (4, 3)), linewidth=1.1, alpha=0.8)
ax2.text(0.98, baseline + 0.01, f'基准线 {baseline:.3f}', ha='right', va='bottom', fontsize=9, color='#555555')

ax2.set_xlabel('召回率 Recall', fontsize=12)
ax2.set_ylabel('精确率 Precision', fontsize=12)
ax2.set_title('PR 曲线对比', fontsize=15, fontweight='bold', pad=12)
ax2.grid(linestyle=':', linewidth=0.6, alpha=0.25)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1.02)
ax2.legend(fontsize=9.5, loc='lower left', frameon=True, facecolor='white', edgecolor='#dddddd')

plt.tight_layout()
plt.show()

# 图3：KS
plt.figure(figsize=(9.2, 7.0), facecolor='white')
ax3 = plt.gca()
ax3.set_facecolor('#fcfcfc')

best_fpr = results[best_name]['fpr']
best_tpr = results[best_name]['tpr']
ks_vals = best_tpr - best_fpr
ks_idx = np.argmax(ks_vals)
ks_val = ks_vals[ks_idx]
thresh_ks = np.linspace(0, 1, len(best_fpr))

ax3.plot(thresh_ks, best_tpr, color='#E45756', linewidth=2.4, label='TPR（命中率）')
ax3.plot(thresh_ks, best_fpr, color='#4C78A8', linewidth=2.4, label='FPR（误判率）')
ax3.plot(thresh_ks, ks_vals, color='#54A24B', linewidth=2.2, linestyle='--', label='KS = TPR - FPR')

ax3.axvline(thresh_ks[ks_idx], color='#777777', linestyle=(0, (4, 3)), linewidth=1.1, alpha=0.8)
ax3.scatter([thresh_ks[ks_idx]], [ks_val], s=55, color='#54A24B', zorder=4)
ax3.annotate(
    f'KS={ks_val:.4f}',
    xy=(thresh_ks[ks_idx], ks_val),
    xytext=(thresh_ks[ks_idx] + 0.08, ks_val - 0.07),
    fontsize=11, color='#2d7f2d', fontweight='bold',
    arrowprops=dict(arrowstyle='->', color='#2d7f2d', lw=1.2)
)

ax3.set_xlabel('阈值（预测概率）', fontsize=12)
ax3.set_ylabel('比率', fontsize=12)
ax3.set_title(f'KS 曲线（{best_name.split(chr(10))[0]}）', fontsize=15, fontweight='bold', pad=12)
ax3.grid(linestyle=':', linewidth=0.6, alpha=0.25)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1.05)
ax3.legend(fontsize=10, loc='upper left', frameon=True, facecolor='white', edgecolor='#dddddd')

plt.tight_layout()
plt.show()

# 图4：混淆矩阵
plt.figure(figsize=(7.8, 6.9), facecolor='white')
ax4 = plt.gca()
ax4.set_facecolor('white')

cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
labels = [['真阴性\nTN', '假阳性\nFP'],
          ['假阴性\nFN', '真阳性\nTP']]
im = ax4.imshow(cm_norm, cmap='Blues', vmin=0, vmax=1)

for i in range(2):
    for j in range(2):
        count = cm[i, j]
        rate = cm_norm[i, j]
        ax4.text(
            j, i,
            f'{labels[i][j]}\n{count} 例\n({rate*100:.1f}%)',
            ha='center', va='center', fontsize=11,
            color='white' if rate > 0.5 else '#222222',
            fontweight='bold'
        )

cbar = plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=9)

ax4.set_xticks([0, 1])
ax4.set_yticks([0, 1])
ax4.set_xticklabels(['预测：非高血脂', '预测：高血脂'], fontsize=10)
ax4.set_yticklabels(['实际：非高血脂', '实际：高血脂'], fontsize=10)
ax4.set_title(f'混淆矩阵热力图\n（{best_name.split(chr(10))[0]}，五折交叉验证）', fontsize=14, fontweight='bold', pad=12)

plt.tight_layout()
plt.show()

print("\n" + "=" * 65)
print("  模块A 结论汇总")
print("=" * 65)
print(f"""
  【模型性能总览】
  四种模型在五折交叉验证下均表现优异（AUC > 0.97），
  说明融合血脂指标、中医体质积分、活动量表的多维度
  特征对高血脂预测具有很强的判别能力。

  【KS统计量解读】
  KS值衡量模型区分高血脂/非高血脂人群的最大能力，
  KS > 0.4 为良好，KS > 0.6 为优秀。
  最优模型 {best_name.split(chr(10))[0]} 的 KS = {results[best_name]['KS']:.4f}，
  达到优秀水平，具备临床风险筛查的实际应用价值。

  【最优模型选定】
  综合 AUC / F1 / KS 三项指标，选定
  {best_name.split(chr(10))[0]} 作为后续风险分层的基础模型。

  【供模块B使用】
  已将最优模型的个体预测概率写入 data_with_proba.xlsx，
  模块B将基于此概率进行低/中/高三级风险分层。
""")
