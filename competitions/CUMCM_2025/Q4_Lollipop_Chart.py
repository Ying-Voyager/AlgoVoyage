import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

file = "女胎预处理后数据.xlsx"
df = pd.read_excel(file)

df["对数读段数"] = np.log1p(df["原始读段数"])
df["重复比例对数"] = np.log1p(df["重复读段的比例"])

z_cols = ["13号染色体的Z值","18号染色体的Z值","21号染色体的Z值"]
df["最大Z值"] = df[z_cols].max(axis=1)
df["平均Z值"] = df[z_cols].mean(axis=1)
df["平方和Z值"] = np.sqrt((df[z_cols]**2).sum(axis=1))

gc_cols = ["13号染色体的GC含量","18号染色体的GC含量","21号染色体的GC含量"]
df["GC平均偏差"] = df[gc_cols].sub(0.5).abs().mean(axis=1)
df["GC变异系数"] = df[gc_cols].std(axis=1) / df[gc_cols].mean(axis=1)

df["BMI平方"] = df["孕妇BMI"]**2
df["年龄平方"] = df["年龄"]**2
df["孕周平方"] = df["检测孕周"]**2
df["BMI乘孕周"] = df["孕妇BMI"] * df["检测孕周"]

TARGET_COL = "染色体的非整倍体"
def _to_bin(x):
    if pd.isna(x): return 0
    s = str(x).strip()
    if s == "" or s.lower() in {"na","nan","none","null"}: return 0
    if any(t in s for t in ("T13","T18","T21")): return 1
    try:
        return 0 if float(s) == 0.0 else 1
    except:
        return 0

y = df[TARGET_COL].map(_to_bin).astype(int)
y.name = "y"

num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if TARGET_COL in num_cols:
    num_cols.remove(TARGET_COL)

rows = []
for c in num_cols:
    pair = pd.concat([df[c], y], axis=1).dropna()
    if len(pair) < 10:
        continue
    r_p, p_p = pearsonr(pair.iloc[:,0], pair.iloc[:,1])
    r_s, p_s = spearmanr(pair.iloc[:,0], pair.iloc[:,1])
    rows.append({
        "特征": c,
        "Pearson_r": r_p,
        "Pearson_p": p_p,
        "Spearman_rho": r_s,
        "Spearman_p": p_s,
        "样本数": len(pair)
    })

res = pd.DataFrame(rows).sort_values(by="Pearson_r", key=lambda s: s.abs(), ascending=False)

out_csv = "与非整倍体相关性_单列.csv"
res.to_csv(out_csv, index=False, encoding="utf-8-sig")
print(f"已导出：{out_csv}")

TOPK = min(20, len(res))
top = res.head(TOPK)

plt.rcParams.update({
    'font.sans-serif': ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans'],
    'axes.unicode_minus': False,
    'font.size': 16,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
})

pos, neg = "#2CB67D", "#7C83FD"

fig, ax = plt.subplots(figsize=(14, 0.8*TOPK + 2))
fig.subplots_adjust(left=0.35, right=0.96, top=0.90, bottom=0.10)

ypos = np.arange(len(top))
labels = top["特征"].tolist()
rvals = top["Pearson_r"].values
cols = [pos if r >= 0 else neg for r in rvals]

for y_i, r_i, c_i in zip(ypos, rvals, cols):
    ax.hlines(y=y_i, xmin=0, xmax=r_i, color=c_i, linewidth=4.0, alpha=0.95)
ax.scatter(rvals, ypos, s=160, color=cols, zorder=3)

ax.axvline(0, color="#9aa0a6", lw=1)

xmin = min(-0.35, rvals.min()*1.25)
xmax = max(0.35,  rvals.max()*1.25)
ax.set_xlim(xmin, xmax)

ax.set_yticks(ypos)
ax.set_yticklabels(labels)
ax.invert_yaxis()

dx = 0.02 * (xmax - xmin)
for y_i, r_i in zip(ypos, rvals):
    ha = "left" if r_i >= 0 else "right"
    ax.text(r_i + (dx if r_i >= 0 else -dx), y_i, f"{r_i:.2f}", va="center", ha=ha, fontweight="bold")

ax.xaxis.grid(True, ls="--", alpha=0.25)
ax.set_axisbelow(True)
ax.set_title("与『染色体的非整倍体(0/1)』的相关性（Pearson）— 棒棒糖图")
ax.set_xlabel("相关系数 r")
ax.set_ylabel("特征")

plt.tight_layout()
plt.show()
