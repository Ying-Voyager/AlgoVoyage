import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams['font.family'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 24
plt.rcParams['axes.titlesize'] = 28
plt.rcParams['axes.labelsize'] = 26
plt.rcParams['xtick.labelsize'] = 24
plt.rcParams['ytick.labelsize'] = 24
plt.rcParams['legend.fontsize'] = 24

BLUE   = '#4C72B0'
RED    = '#C44E52'
GREEN  = '#55A868'
PURPLE = '#8172B2'
YELLOW = '#CCB974'
CYAN   = '#64B5CD'

path ="附件.xlsx"

xls = pd.ExcelFile(path)
for n in xls.sheet_names:
    t = pd.read_excel(path, sheet_name=n)
    if len(t) > 0:
        df = t.copy()
        break
df.columns = [str(c).strip() for c in df.columns]

def pick(keys):
    for c in df.columns:
        if all(k in str(c) for k in keys):
            return c
    for c in df.columns:
        if any(k in str(c) for k in keys):
            return c
    return None

col_raw  = pick(["原始", "读段"]) or pick(["总读段"])
col_uniq = pick(["唯一", "读段"]) or pick(["唯一比对"])
col_map  = pick(["比对", "比例"])
cands = [c for c in df.columns if "GC" in str(c) or "gc" in str(c)]
col_gc = None
for c in cands:
    if not any(x in str(c) for x in ["13", "18", "21", "X", "Y"]):
        col_gc = c
        break

to_num = lambda s: pd.to_numeric(s, errors="coerce")
raw = to_num(df[col_raw])   / 1_000_000.0
uniq = to_num(df[col_uniq]) / 1_000_000.0
mrate = to_num(df[col_map])
gcrate = to_num(df[col_gc])

bins_raw  = [0, 3, 5, 7, 9, np.inf]
bins_uniq = [0, 2, 3, 4, 5, 6, np.inf]
bins_map  = [0.0, 0.75, 0.78, 0.81, 1.0]
bins_gc   = [0.0, 0.390, 0.395, 0.400, 0.405, 0.410, 1.0]

def plot_dist(ax, s, bins, xlabel, c1=BLUE, c2=RED, fmt=None):
    s = s.dropna()
    cats = pd.cut(s, bins=bins, right=False, include_lowest=True)
    cnt = cats.value_counts().sort_index()
    cnt = cnt[cnt > 0]
    x = np.arange(len(cnt))

    ax.set_facecolor('#F8F9FA')
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')

    bars = ax.bar(x, cnt.values, color=c1, alpha=0.9, edgecolor='white', linewidth=1.2)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2., h + max(cnt.values)*0.01, f'{int(h)}',
                ha='center', va='bottom', fontsize=17)

    line, = ax.plot(x, cnt.values, marker="o", color=c2, linewidth=2.8,
                    markersize=8, markerfacecolor='white', markeredgewidth=2)

    ax.set_xlabel(xlabel, labelpad=10)
    ax.set_ylabel("样本数量", labelpad=10)
    ax.set_xticks(x)

    labels = []
    for iv in cnt.index:
        if fmt is not None:
            labels.append(fmt(iv))
        else:
            labels.append(f"{iv.left:.0f}-{iv.right:.0f}" if iv.right > 1.0 else f"{iv.left:.2f}-{iv.right:.2f}")
    ax.set_xticklabels(labels, rotation=45, ha='right')

    for sp in ax.spines.values():
        sp.set_visible(False)

    ax.legend([bars, line], ['样本数', '趋势线'], loc='upper right', frameon=False)

def fmt_raw(iv):
    l, r = float(iv.left), float(iv.right)
    if l == 0 and r == 3: return "<3"
    if np.isinf(r):       return f">{l:.0f}"
    return f"{l:.0f}-{r:.0f}"

def fmt_uniq(iv):
    l, r = float(iv.left), float(iv.right)
    if l == 0 and r == 2: return "<2"
    if np.isinf(r):       return f">{l:.0f}"
    return f"{l:.0f}-{r:.0f}"

def fmt_map(iv):
    l, r = float(iv.left), float(iv.right)
    if abs(l-0.00)<1e-9 and abs(r-0.75)<1e-9: return "<0.75"
    if abs(l-0.81)<1e-9 and r >= 0.999:       return ">0.81"
    return f"{l:.2f}-{r:.2f}"

def fmt_gc(iv):
    l, r = float(iv.left), float(iv.right)
    if abs(l-0.000)<1e-9 and abs(r-0.390)<1e-9: return "<0.390"
    if abs(l-0.410)<1e-9 and r >= 0.999:        return ">0.410"
    return f"{l:.3f}-{r:.3f}"

fig, ax = plt.subplots(2, 2, figsize=(16, 12))
fig.patch.set_facecolor('white')

plot_dist(ax[0, 0], raw,  bins_raw,  "原始读段数（百万）", BLUE,   RED,    fmt_raw)
plot_dist(ax[0, 1], uniq, bins_uniq, "唯一比对读段数（百万）", GREEN,  PURPLE, fmt_uniq)
plot_dist(ax[1, 0], mrate, bins_map, "比对比例",            PURPLE, YELLOW, fmt_map)
plot_dist(ax[1, 1], gcrate, bins_gc, "GC含量",              CYAN,   RED,    fmt_gc)

plt.tight_layout()
out = Path("数学建模国赛C题代码") / "质量控制指标分布.png"
out.parent.mkdir(exist_ok=True)
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor='white')
plt.show()
