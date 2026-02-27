import numpy as np
import matplotlib.pyplot as plt

models = ['XGBoost', 'LightGBM', 'SVM', 'Logistic']
r = [0.496, 0.499, 0.329, 0.273]
sigma_n = [0.595, 0.562, 0.222, 0.210]
crmse = [0.298, 0.297, 0.324, 0.329]

metrics = ['r', 'σ_norm', 'cRMSE']
vals = {'r': np.array(r, float), 'σ_norm': np.array(sigma_n, float), 'cRMSE': np.array(crmse, float)}
flip = {'r': False, 'σ_norm': False, 'cRMSE': True}

LABEL_Y = 1.10
YMAX = 1.20

plt.rcParams.update({
    'font.sans-serif': ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans'],
    'axes.unicode_minus': False,
    'font.size': 24,
    'axes.titlesize': 0,
    'legend.fontsize': 22,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
})

mtext = {'r': 'r', 'σ_norm': r'$\sigma_{\mathrm{norm}}$', 'cRMSE': 'cRMSE'}

mins = {m: vals[m].min() for m in metrics}
maxs = {m: vals[m].max() for m in metrics}

def scale(m, v):
    rng = maxs[m] - mins[m]
    y = (v - mins[m]) / (rng + 1e-12)
    return 1 - y if flip[m] else y

norm = np.column_stack([scale(m, vals[m]) for m in metrics])

fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
palette = ["#E63946", "#1D3557", "#457B9D", "#55A868", "#C44E52", "#8172B2"]
marks = ['o','s','^','D','P','X']

x = np.arange(len(metrics))
for i, name in enumerate(models):
    ax.plot(x, norm[i], lw=4, marker=marks[i % len(marks)], ms=14,
            color=palette[i % len(palette)], label=name, alpha=0.9)

for xi, m in enumerate(metrics):
    ax.vlines(xi, 0, 1, color='#bbbbbb', lw=2.5, alpha=0.7)
    ax.text(xi, LABEL_Y, mtext[m], ha='center', va='bottom', fontsize=28, fontweight='bold')
    for t in np.linspace(mins[m], maxs[m], 5):
        yt = scale(m, t)
        ax.hlines(yt, xi-0.04, xi+0.04, color='#9a9a9a', lw=1.8)
        ax.text(xi+0.06, yt, f"{t:.3f}", va='center', fontsize=20,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))

ax.set_xlim(x[0]-0.5, x[-1]+0.5)
ax.set_ylim(-0.05, YMAX)
ax.set_xticks([]); ax.set_yticks([])
ax.grid(axis='y', alpha=0.2, linestyle='-', linewidth=1.5)
ax.set_facecolor('#f8f9fa'); fig.patch.set_facecolor('white')

ax.legend(loc='center', bbox_to_anchor=(0.5, -0.1),
          ncol=len(models), frameon=True, framealpha=0.9,
          fancybox=True, shadow=False, borderpad=0.6, handlelength=2.2, columnspacing=1.6)

plt.tight_layout()
plt.show()
