import os, re, json, warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.calibration import calibration_curve
import lightgbm as lgb

# 参数
path = "男胎预处理后数据.xlsx"
Y_TH = 0.04
WEEK_GRID = np.arange(10, 25.5, 0.5)
K = 5
PI_STAR = 0.90
SEED = 2025

plt.rcParams['font.sans-serif'] = ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读数据 & 列匹配
df0 = pd.read_excel(path)

def pick(df, keys):
    for k in keys:
        for c in df.columns:
            if str(k) in str(c):
                return c
    return None

y_col    = pick(df0, ['Y浓度','Y染色体浓度','浓度','Y concentration','Y_ratio'])
bmi_col  = pick(df0, ['BMI','孕妇BMI','maternal BMI'])
week_col = pick(df0, ['孕周','检测孕周','孕周数','Week','Gestational'])
sex_col  = pick(df0, ['胎儿性别','性别','Fetal Sex','Sex'])
age_col  = pick(df0, ['年龄','Age'])
ht_col   = pick(df0, ['身高','Height','Stature'])
wt_col   = pick(df0, ['体重','Weight','Mass'])
gc_col   = pick(df0, ['GC','GC含量'])
reads_col= pick(df0, ['读段','reads','read count','原始读段数'])
map_col  = pick(df0, ['比对率','MapRate','mapping'])

assert y_col and bmi_col and week_col, "缺少 Y浓度/BMI/孕周"

use = [c for c in [week_col,bmi_col,age_col,ht_col,wt_col,gc_col,reads_col,map_col] if c]
df = df0[[y_col] + use].copy()

if sex_col and df0[sex_col].notna().any():
    male = df0[sex_col].astype(str).str.contains('男|male|Male|M', case=False, regex=True)
    df = df.loc[male, :]

df = df.dropna().copy()
if (df[y_col] > 1).mean() > 0.5:
    df[y_col] = df[y_col] / 100.0

y = (df[y_col] >= Y_TH).astype(int)

ren = {
    week_col:'Week',
    bmi_col:'BMI',
    age_col:'Age' if age_col else None,
    ht_col:'Height' if ht_col else None,
    wt_col:'Weight' if wt_col else None,
    gc_col:'GC' if gc_col else None,
    reads_col:'Reads' if reads_col else None,
    map_col:'MapRate' if map_col else None
}
ren = {k:v for k,v in ren.items() if v is not None}
df = df.rename(columns=ren)

feat = [c for c in ['Week','BMI','Age','Height','Weight','GC','Reads','MapRate'] if c in df.columns]
X = df[feat].astype(float)

print(f"样本量: {len(X)}, 达标比例: {y.mean():.3f}")
print("特征:", feat)

# 训练/验证
X_tr, X_va, y_tr, y_va = train_test_split(X, y, test_size=0.25, random_state=SEED, stratify=y)

model = lgb.LGBMClassifier(
    objective='binary', max_depth=4, n_estimators=700, learning_rate=0.05,
    subsample=0.85, colsample_bytree=0.9, reg_lambda=1.0, random_state=SEED, n_jobs=8
)
model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], eval_metric='auc')

p_va = model.predict_proba(X_va)[:,1]
auc = roc_auc_score(y_va, p_va)
print(f"AUC(valid) = {auc:.4f}")

# ROC
fpr, tpr, _ = roc_curve(y_va, p_va)
plt.figure(figsize=(6,5))
plt.plot(fpr, tpr, lw=2, label=f"AUC={auc:.3f}")
plt.plot([0,1],[0,1],'--',lw=1)
plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate")
plt.title("ROC（验证集, LightGBM）")
plt.legend(); plt.tight_layout(); plt.show()

# 特征重要性
imp = model.feature_importances_
order = np.argsort(imp)[::-1]
plt.figure(figsize=(7,5))
plt.barh(np.array(feat)[order][::-1], imp[order][::-1])
plt.title("LightGBM 特征重要性")
plt.tight_layout(); plt.show()

# BMI 自动切点
def bmi_cuts(mdl, names):
    info = mdl.booster_.dump_model()
    cuts = []
    def dfs(node):
        if 'split_feature' not in node:
            return
        idx = node['split_feature']
        name = names[idx] if isinstance(idx, int) else idx
        thr = node.get('threshold', None)
        if name == 'BMI' and thr is not None:
            try:
                cuts.append(float(thr))
            except:
                try:
                    cuts.append(float(str(thr).strip()))
                except:
                    pass
        if 'left_child' in node: dfs(node['left_child'])
        if 'right_child' in node: dfs(node['right_child'])
    for ti in info.get('tree_info', []):
        if 'tree_structure' in ti:
            dfs(ti['tree_structure'])
    return cuts

cuts_raw = bmi_cuts(model, feat)
if len(cuts_raw) == 0:
    qs = np.linspace(0,1,K+1)[1:-1]
    cuts = list(np.unique(np.quantile(X['BMI'], qs)))
else:
    cnt = Counter(np.round(cuts_raw, 1))
    cuts = [k for k,_ in cnt.most_common(K-1)]
cuts = sorted(set(cuts))
bins = [-np.inf] + cuts + [np.inf]
print(f"BMI 切点:", cuts)

plt.figure(figsize=(7,4))
plt.hist(X['BMI'], bins=30, alpha=0.75, edgecolor='k')
for c in cuts:
    plt.axvline(c, color='r', ls='--', lw=1.2)
plt.xlabel('BMI'); plt.ylabel('样本数'); plt.title('BMI 分布（含自动切点）')
plt.tight_layout(); plt.show()

# 组内达标曲线 & 推荐周
bmi_grp = pd.cut(X['BMI'], bins=bins, include_lowest=True)
df_g = df.copy(); df_g['BMI_group'] = bmi_grp

def curve(gdf, grid):
    if len(gdf)==0: return np.zeros_like(grid, float)
    feats = gdf[feat].copy()
    out = []
    for w in grid:
        t = feats.copy(); t['Week'] = w
        out.append(model.predict_proba(t)[:,1].mean())
    return np.array(out)

curves = {}; best = {}
for g, gdf in df_g.groupby('BMI_group'):
    m = curve(gdf, WEEK_GRID)
    curves[g] = m
    idx = np.where(m >= PI_STAR)[0]
    best[g] = float(WEEK_GRID[idx[0]]) if len(idx)>0 else float(WEEK_GRID[np.argmax(m)])

plt.figure(figsize=(8.5,5.5))
for g, m in curves.items():
    plt.plot(WEEK_GRID, m, lw=2, label=str(g))
    bw = best[g]; pm = np.interp(bw, WEEK_GRID, m)
    plt.scatter([bw],[pm], s=55, zorder=3)
plt.axhline(PI_STAR, color='gray', ls='--', lw=1.2, label=f"达标线 {PI_STAR:.0%}")
plt.xlabel("孕周 (Week)"); plt.ylabel("组均达标概率  P(Y≥4%)")
plt.title("不同 BMI 组：孕周-达标概率 与 推荐检测周")
plt.legend(fontsize=9, ncol=2); plt.grid(alpha=0.25)
plt.tight_layout(); plt.show()

rows = []
for g in curves.keys():
    rows.append({
        "BMI组": str(g),
        "样本量": int((df_g['BMI_group']==g).sum()),
        "推荐孕周": best[g],
        "该周组均达标概率": float(np.interp(best[g], WEEK_GRID, curves[g]))
    })
rec = pd.DataFrame(rows).sort_values("BMI组")
print("\n=== 推荐检测周（LightGBM） ===")
print(rec.to_string(index=False))

# 校准
p_val = model.predict_proba(X_va)[:,1]
frac, meanp = calibration_curve(y_va, p_val, n_bins=10, strategy='quantile')
plt.figure(figsize=(6,5))
plt.plot(meanp, frac, marker='o')
plt.plot([0,1],[0,1],'--',lw=1)
plt.xlabel("平均预测概率"); plt.ylabel("实际达标频率")
plt.title("校准曲线（验证集, LightGBM）")
plt.tight_layout(); plt.show()

# SHAP
try:
    import shap
    exp = shap.TreeExplainer(model)
    sv = exp.shap_values(X_va)
    if isinstance(sv, list):
        sv = sv[1] if len(sv)>1 else sv[0]
    plt.figure(figsize=(7,4))
    shap.summary_plot(sv, X_va, show=False)
    plt.title("SHAP（验证集, LightGBM）")
    plt.tight_layout(); plt.show()
except Exception as e:
    print("SHAP 跳过：", e)

# 置信带（组内 bootstrap）
MC = 500
rng = np.random.default_rng(SEED)
curves_runs = {}

for g, gdf in df_g.groupby('BMI_group'):
    if len(gdf) == 0:
        continue
    feats_all = gdf[feat].copy().reset_index(drop=True)
    n = len(feats_all)
    c_runs = []
    for _ in range(MC):
        idx = rng.integers(0, n, size=n)
        fb = feats_all.iloc[idx].copy()
        out = []
        for w in WEEK_GRID:
            t = fb.copy(); t['Week'] = w
            out.append(model.predict_proba(t)[:,1].mean())
        c_runs.append(np.array(out, float))
    curves_runs[g] = c_runs

plt.figure(figsize=(9.5, 6.5))
for g, runs in curves_runs.items():
    mat = np.vstack(runs)
    mean = mat.mean(0)
    se = mat.std(0, ddof=1)/np.sqrt(len(runs))
    lo, hi = mean - 1.96*se, mean + 1.96*se
    plt.plot(WEEK_GRID, mean, lw=2, label=f"{g}")
    plt.fill_between(WEEK_GRID, lo, hi, alpha=0.2)
    bw = best[g]; pm = np.interp(bw, WEEK_GRID, mean)
    plt.scatter([bw],[pm], s=45, zorder=3)

plt.axhline(PI_STAR, color='gray', ls='--', lw=1.3)
plt.xlabel("孕周 (Week)"); plt.ylabel("组均达标概率  P(Y≥4%)")
plt.title("孕周-达标概率：均值 ± 95% 置信带（固定模型）")
plt.legend(ncol=2, fontsize=9, frameon=True)
plt.grid(alpha=0.25); plt.tight_layout(); plt.show()
