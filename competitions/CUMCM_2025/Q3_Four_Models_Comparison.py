import os
os.environ["MPLBACKEND"] = "Agg"
import matplotlib
matplotlib.use("Agg")

import warnings, json
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score,
    recall_score, f1_score, brier_score_loss
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

try:
    import xgboost as xgb
except Exception:
    xgb = None
try:
    import lightgbm as lgb
except Exception:
    lgb = None

path ="男胎预处理后数据.xlsx"
Y_TH = 0.04
TEST = 0.25
SEED = 2025

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

use = [c for c in [week_col, bmi_col, age_col, ht_col, wt_col, gc_col, reads_col, map_col] if c]
df = df0[[y_col] + use].copy()

if sex_col and df0[sex_col].notna().any():
    male = df0[sex_col].astype(str).str.contains('男|male|Male|M', case=False, regex=True)
    df = df.loc[male]

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

print(f"样本量: {len(X)}, 正例比例: {y.mean():.3f}")
print("特征:", feat)

X_tr, X_va, y_tr, y_va = train_test_split(X, y, test_size=TEST, random_state=SEED, stratify=y)

models = {}

if xgb is not None:
    models["XGBoost"] = xgb.XGBClassifier(
        objective='binary:logistic',
        max_depth=4, n_estimators=600, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.9, reg_lambda=1.0,
        n_jobs=8, random_state=SEED
    )
else:
    print("xgboost 未安装，已跳过。")

if lgb is not None:
    models["LightGBM"] = lgb.LGBMClassifier(
        objective='binary',
        max_depth=4, n_estimators=700, learning_rate=0.05,
        subsample=0.85, colsample_bytree=0.9, reg_lambda=1.0,
        random_state=SEED, n_jobs=8
    )
else:
    print("lightgbm 未安装，已跳过。")

models["SVM"] = Pipeline([
    ('scaler', StandardScaler()),
    ('svc', SVC(kernel='rbf', C=2.0, gamma='scale', probability=True, random_state=SEED))
])

models["Logistic"] = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression(solver='lbfgs', max_iter=2000, C=1.0, random_state=SEED))
])

def eval_metrics(y_true, proba, thr=0.5):
    y_pred = (proba >= thr).astype(int)
    return {
        "AUC": roc_auc_score(y_true, proba),
        "Accuracy": accuracy_score(y_true, y_pred),
        "F1": f1_score(y_true, y_pred, zero_division=0),
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "Calibration(1-Brier)": 1.0 - brier_score_loss(y_true, proba),
    }

def taylor_stats(y_true, proba):
    y = np.asarray(y_true, float)
    p = np.asarray(proba, float)
    s_ref = float(np.std(y, ddof=0))
    s_sim = float(np.std(p, ddof=0))
    if s_ref == 0 or s_sim == 0:
        r = 0.0
    else:
        r = float(np.corrcoef(p, y)[0, 1])
        r = float(np.clip(r, -1.0, 1.0))
    e2 = s_ref**2 + s_sim**2 - 2.0*s_ref*s_sim*r
    crmse = float(np.sqrt(max(e2, 0.0)))
    return s_ref, s_sim, r, crmse

res = {}
probas = {}
for name, mdl in models.items():
    mdl.fit(X_tr, y_tr)
    p = mdl.predict_proba(X_va)[:, 1]
    res[name] = eval_metrics(y_va, p)
    probas[name] = p

print("\n=== 指标 ===")
for k, v in res.items():
    print(k, {m: round(x, 4) for m, x in v.items()})

stats = {}
s_ref_global = float(np.std(y_va.astype(float), ddof=0))
for name, p in probas.items():
    s_ref, s_sim, r, _ = taylor_stats(y_va, p)
    crmse = float(np.sqrt(max(s_ref_global**2 + s_sim**2 - 2.0*s_ref_global*s_sim*r, 0.0)))
    stats[name] = (round(s_ref_global, 6), round(s_sim, 6), round(r, 6), round(crmse, 6))

print("\n=== Taylor 数据 ===")
for k, (sr, ss, r, c) in stats.items():
    print(f"{k}: (std_ref={sr}, std_sim={ss}, corr={r}, cRMSE={c})")

with open("taylor_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

stats_df = pd.DataFrame.from_dict(
    {k: {"std_ref": v[0], "std_sim": v[1], "corr": v[2], "cRMSE": v[3]} for k, v in stats.items()},
    orient="index"
)
stats_df.index.name = "Model"
stats_df.to_csv("taylor_stats.csv", encoding="utf-8-sig")

labels = ["AUC", "Accuracy", "F1", "Precision", "Recall", "Calibration(1-Brier)"]
n = len(labels)
angles = np.linspace(0, 2*np.pi, n, endpoint=False).tolist()
angles += angles[:1]

def vals(name):
    v = [res[name][lab] for lab in labels]
    return v + v[:1]

plt.figure(figsize=(7.5,7.5))
ax = plt.subplot(111, polar=True)
ax.set_theta_offset(np.pi/2)
ax.set_theta_direction(-1)
plt.xticks(angles[:-1], labels, fontsize=11)
ax.set_rlabel_position(0)
plt.yticks([0.2,0.4,0.6,0.8], ["0.2","0.4","0.6","0.8"], color="gray", size=9)
plt.ylim(0, 1.0)

colors = ["#4C72B0","#55A868","#C44E52","#8172B2"]
for i, name in enumerate(res.keys()):
    v = vals(name)
    ax.plot(angles, v, linewidth=2, label=name, color=colors[i % len(colors)])
    ax.fill(angles, v, alpha=0.15, color=colors[i % len(colors)])

plt.title("四模型综合对比（雷达图，越大越好）", y=1.08, fontsize=14)
plt.legend(loc='upper right', bbox_to_anchor=(1.28, 1.05))
plt.tight_layout()
out = "radar_comparison.png"
plt.savefig(out, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n雷达图: {os.path.abspath(out)}")
print(f"Taylor: {os.path.abspath('taylor_stats.json')} / {os.path.abspath('taylor_stats.csv')}")
