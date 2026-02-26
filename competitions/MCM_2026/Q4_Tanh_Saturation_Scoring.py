import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 全局设置
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'  # 避免中文乱码风险
plt.rcParams['font.size'] = 10


def plot_tanh_sensitivity_v2():
    print("正在生成 Tanh 参数灵敏度分析图 (多交点版)...")

    # X轴: 粉丝得票率 (0% 到 60%)
    shares = np.linspace(0, 60, 300)

    # 定义不同的 k 值进行对比 (按你的要求: 3, 5, 10)
    k_values = [3, 5, 10]

    # 颜色映射: k=3(灰), k=5(红/选中), k=10(蓝)
    colors = {3: '#7F8C8D', 5: '#C0392B', 10: '#2980B9'}
    styles = {3: '--', 5: '-', 10: '--'}
    widths = {3: 2, 5: 4, 10: 2}
    labels = {
        3: 'k=3 (Under-rewarding)',
        5: 'k=5 (Optimal/Selected)',
        10: 'k=10 (Over-saturated)'
    }

    fig, ax = plt.subplots(figsize=(12, 7))

    # 2. 绘制三条曲线
    for k in k_values:
        scores = 10 * np.tanh(k * shares / 100.0)
        ax.plot(shares, scores, label=labels[k], color=colors[k],
                linestyle=styles[k], linewidth=widths[k], alpha=0.8)

    # 3. 定义三个关键参照线 (Anchors)
    anchors = [
        {'val': 100 / 12, 'name': 'Avg (8.3%)', 'color': 'green'},  # 路人
        {'val': 20.0, 'name': 'Popular (20%)', 'color': 'orange'},  # 新增：当红
        {'val': 40.0, 'name': 'Star (40%)', 'color': 'purple'}  # 巨星
    ]

    # 4. 绘制参照线和所有交点
    for anchor in anchors:
        x_val = anchor['val']
        c_line = anchor['color']

        # 画垂直虚线
        ax.axvline(x_val, color=c_line, linestyle=':', alpha=0.6, linewidth=1.5)

        # 在顶部标记线的名字
        ax.text(x_val, 10.6, anchor['name'], color=c_line, ha='center', fontweight='bold', fontsize=10)

        # 计算并标记 3 个 k 值的交点
        for k in k_values:
            y_val = 10 * np.tanh(k * x_val / 100.0)

            # 画点
            ax.scatter([x_val], [y_val], color=colors[k], s=60, zorder=10, edgecolors='white')

            # 添加分数文字 (为了防重叠，做一些微调)
            offset_y = 0.4
            if k == 10: offset_y = 0.3  # 最上面的线，字往上标
            if k == 3:  offset_y = -0.6  # 最下面的线，字往下标
            if k == 5:  offset_y = -0.5  # 中间的线，根据情况微调

            # 特殊处理：k=10 在 40% 处已经接近重叠，微调
            if x_val == 40 and k == 10: offset_y = 0.2

            # 格式化分数
            ax.text(x_val + 0.8, y_val + offset_y, f"{y_val:.1f}",
                    color=colors[k], fontsize=9, fontweight='bold', va='center')

    # 5. 图表修饰
    ax.set_title(r"Parameter Justification: Why $k=5$? (Score vs. Vote Share)", fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel("Fan Vote Share (%)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Fan Score (0-10)", fontsize=12, fontweight='bold')

    # 设置范围
    ax.set_ylim(0, 11)  # 稍微高一点，留出顶部文字空间
    ax.set_xlim(0, 55)

    # 添加图例
    ax.legend(loc='lower right', fontsize=11, frameon=True, framealpha=0.9, facecolor='white')

    # 添加网格
    ax.grid(True, linestyle='-', alpha=0.2)

    plt.tight_layout()
    plt.savefig('Tanh_Sensitivity_Comparison.png')
    print("✅ 可视化完成: Tanh_Sensitivity_Comparison.png")


if __name__ == "__main__":
    plot_tanh_sensitivity_v2()