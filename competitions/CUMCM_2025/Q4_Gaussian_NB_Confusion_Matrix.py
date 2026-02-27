import numpy as np
import matplotlib.pyplot as plt

# 数据
cm_test_opt = np.array([[86, 17],
                        [ 1, 12]])

cm_train_opt_on_test = np.array([[65, 38],
                                 [ 2, 11]])

title_left  = ""
title_right = ""

# 字体
plt.rcParams.update({
    'font.sans-serif': ['SimHei','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','DejaVu Sans'],
    'axes.unicode_minus': False,
    'font.size': 24,
    'xtick.labelsize': 22,
    'ytick.labelsize': 22,
    'axes.labelsize': 26,
    'axes.titlesize': 26,
})

def draw_cm(ax, cm, title, cmap, vmax):
    im = ax.imshow(cm, cmap=cmap, vmin=0, vmax=vmax)
    ax.set(title=title, xlabel="预测值", ylabel="真实值")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["正常(0)", "异常(1)"])
    ax.set_yticklabels(["正常(0)", "异常(1)"])
    ax.set_xticks(np.arange(-.5, 2, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 2, 1), minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for i in range(2):
        for j in range(2):
            v = cm[i, j]
            ax.text(j, i, f"{v}", ha="center", va="center",
                    color=("white" if v > vmax * 0.55 else "black"), fontsize=24)
    return im

vmax = max(cm_test_opt.max(), cm_train_opt_on_test.max())

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
draw_cm(axes[0], cm_test_opt, title_left, "Blues", vmax)
draw_cm(axes[1], cm_train_opt_on_test, title_right, "Oranges", vmax)

plt.tight_layout()
plt.show()
