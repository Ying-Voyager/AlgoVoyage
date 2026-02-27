import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import pdist

rcParams["font.family"] = "SimHei"
rcParams["axes.unicode_minus"] = False

def bump(p, d=8, base=12):
    v = rcParams.get(p, base)
    try:
        rcParams[p] = float(v) + d
    except:
        rcParams[p] = base + d

for k in ["font.size","axes.titlesize","axes.labelsize","xtick.labelsize","ytick.labelsize","legend.fontsize"]:
    bump(k, 8)

path ="男胎预处理后数据.xlsx"
df = pd.read_excel(path)

def pick(df, keys):
    for c in df.columns:
        s = str(c)
        if any(k in s for k in keys):
            return c
    return None

y_c   = pick(df, ["Y染色体浓度","Y浓度","Y","浓度"])
bmi_c = pick(df, ["孕妇BMI","BMI","bmi"])
wk_c  = pick(df, ["检测孕周","孕周","孕周数","week"])
if not all([y_c, bmi_c, wk_c]):
    raise ValueError("列名不匹配")

tmp = df[[y_c, bmi_c, wk_c]].dropna().astype(float)
tmp.columns = ["Y","BMI","Week"]
tmp["BMI2"] = tmp["BMI"]**2
tmp["Week2"] = tmp["Week"]**2
tmp["BMIxWeek"] = tmp["BMI"]*tmp["Week"]
corr = tmp.corr(method="pearson")

row_lk = linkage(pdist(corr), method="average")
col_lk = linkage(pdist(corr.T), method="average")

sns.set_theme(context="talk")
base = rcParams.get("font.size", 12)
try:
    ann = float(base) + 8
except:
    ann = 20

g = sns.clustermap(
    corr,
    row_linkage=row_lk,
    col_linkage=col_lk,
    annot=True,
    annot_kws={"fontsize": ann},
    fmt=".2f",
    cmap="coolwarm",
    linewidths=0.5,
    cbar_kws={"shrink": 0.7},
    figsize=(9, 8),
    dendrogram_ratio=(0.15, 0.15)
)

for lbl in g.ax_heatmap.get_xticklabels():
    lbl.set_fontsize(rcParams["xtick.labelsize"])
for lbl in g.ax_heatmap.get_yticklabels():
    lbl.set_fontsize(rcParams["ytick.labelsize"])

if g.cax is not None:
    g.cax.tick_params(labelsize=rcParams["ytick.labelsize"])

for ax in [g.ax_row_dendrogram, g.ax_col_dendrogram]:
    for ln in ax.collections:
        ln.set_linewidth(2.5)

g.ax_heatmap.set_title("")
plt.tight_layout()
plt.show()
