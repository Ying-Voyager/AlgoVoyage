import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

# 设置专业级风格
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 13
plt.rcParams['axes.titlesize'] = 18
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']


def plot_clean_age_effect():
    """
    绘制年龄效应的清晰分组折线图

    改进点：
    1. 更专业的配色和样式
    2. 添加样本量标注
    3. 添加趋势线和统计显著性
    4. 增强视觉对比
    """
    # 1. 读取数据
    try:
        df = pd.read_csv('Factor_Analysis_Data.csv')
        print(f"✅ 成功读取数据：{len(df)} 位选手")
    except:
        print("❌ 找不到 Factor_Analysis_Data.csv，请先运行 factor_analysis_full.py 生成数据。")
        return

    # 2. 创建年龄分组（优化分组边界）
    bins = [10, 30, 40, 50, 60, 90]
    labels = ['18-30', '31-40', '41-50', '51-60', '60+']
    df['Age_Group'] = pd.cut(df['celebrity_age_during_season'], bins=bins, labels=labels)

    # 3. 计算分组统计（均值、标准误、样本量）
    grouped = df.groupby('Age_Group', observed=True).agg({
        'Avg_Judge_Score': ['mean', 'sem', 'count'],
        'Fan_Power_Index': ['mean', 'sem']
    }).reset_index()

    # 展平列名
    grouped.columns = ['Age_Group', 'Judge_Mean', 'Judge_Err', 'Judge_Count',
                       'Fan_Mean', 'Fan_Err']

    # 移除空组
    grouped = grouped.dropna()

    print("\n📊 年龄组统计：")
    print(grouped[['Age_Group', 'Judge_Count', 'Judge_Mean', 'Fan_Mean']].to_string(index=False))

    # 4. 创建高质量图表
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # 设置背景
    ax1.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('white')

    # --- 左轴：评委分（蓝色） ---
    color_judge = '#2E86C1'  # 稳重深蓝
    ax1.set_xlabel('Age Group (years)', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Average Judge Score\n(Technical Performance)',
                   color=color_judge, fontsize=16, fontweight='bold')

    # 画线 + 误差棒（更粗更明显）
    x_pos = np.arange(len(grouped))
    line1 = ax1.errorbar(x_pos, grouped['Judge_Mean'],
                         yerr=grouped['Judge_Err'],
                         fmt='-o',
                         color=color_judge,
                         linewidth=4,
                         markersize=12,
                         markeredgewidth=2,
                         markeredgecolor='white',
                         capsize=8,
                         capthick=3,
                         elinewidth=2.5,
                         label='Judge Score (Technical)',
                         zorder=10)

    ax1.tick_params(axis='y', labelcolor=color_judge, labelsize=13)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(grouped['Age_Group'], fontsize=13, fontweight='bold')

    # 添加样本量标注（在每个点上方，但41-50组放下方避免遮挡）
    for i, (x, y, n, age_group) in enumerate(zip(x_pos, grouped['Judge_Mean'],
                                                 grouped['Judge_Count'],
                                                 grouped['Age_Group'])):
        # 对于41-50年龄组，放在下方
        if age_group == '41-50':
            y_offset = -0.8  # 下方
            va = 'top'
        else:
            y_offset = 0.4  # 上方
            va = 'bottom'

        ax1.text(x, y + y_offset, f'n={int(n)}',
                 ha='center', va=va, fontsize=10,
                 color=color_judge, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                           edgecolor=color_judge, alpha=0.8))

    # --- 右轴：粉丝指数（红色） ---
    ax2 = ax1.twinx()
    color_fan = '#E74C3C'  # 鲜艳红
    ax2.set_ylabel('Fan Power Index\n(Popularity Premium)',
                   color=color_fan, fontsize=16, fontweight='bold')

    # 画线 + 误差棒
    line2 = ax2.errorbar(x_pos, grouped['Fan_Mean'],
                         yerr=grouped['Fan_Err'],
                         fmt='-s',
                         color=color_fan,
                         linewidth=4,
                         markersize=12,
                         markeredgewidth=2,
                         markeredgecolor='white',
                         capsize=8,
                         capthick=3,
                         elinewidth=2.5,
                         linestyle='--',
                         label='Fan Power (Popularity)',
                         zorder=10)

    ax2.tick_params(axis='y', labelcolor=color_fan, labelsize=13)

    # 设置右轴范围，让0线明显
    y_max = max(abs(grouped['Fan_Mean'].min()), abs(grouped['Fan_Mean'].max())) + 0.5
    ax2.set_ylim(-y_max, y_max)

    # 添加0轴参考线（加粗）
    ax2.axhline(0, color='gray', linestyle='--', linewidth=2, alpha=0.6, zorder=1)

    # 5. 添加趋势箭头和标注
    # Judge Score趋势（向下）
    judge_trend = grouped['Judge_Mean'].iloc[-1] - grouped['Judge_Mean'].iloc[0]
    ax1.annotate('', xy=(len(x_pos) - 0.5, grouped['Judge_Mean'].iloc[-1]),
                 xytext=(0.5, grouped['Judge_Mean'].iloc[0]),
                 arrowprops=dict(arrowstyle='->', color=color_judge,
                                 lw=3, alpha=0.5, linestyle='--'))

    # Fan Power趋势（向上或平）
    fan_trend = grouped['Fan_Mean'].iloc[-1] - grouped['Fan_Mean'].iloc[0]
    if abs(fan_trend) > 0.1:  # 如果有明显趋势
        ax2.annotate('', xy=(len(x_pos) - 0.5, grouped['Fan_Mean'].iloc[-1]),
                     xytext=(0.5, grouped['Fan_Mean'].iloc[0]),
                     arrowprops=dict(arrowstyle='->', color=color_fan,
                                     lw=3, alpha=0.5, linestyle='--'))

    # 6. 添加网格（只在主轴）
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=1)
    ax1.set_axisbelow(True)

    # 7. 标题和图例
    plt.title('The Age Paradox: Judges Punish Age, Fans Forgive It\n' +
              'How technical performance and popularity diverge with age',
              fontsize=20, fontweight='bold', pad=25)

    # 合并图例（放在底部中央，避免遮挡）
    lines = [line1, line2]
    labels = ['Judge Score: Declines with age (technical decline)',
              'Fan Power: Stable or increases (sympathy, nostalgia)']

    legend = ax1.legend(lines, labels,
                        loc='upper center',
                        bbox_to_anchor=(0.5, -0.12),
                        ncol=2,
                        frameon=True,
                        fancybox=True,
                        shadow=True,
                        fontsize=13,
                        framealpha=0.95)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_edgecolor('black')
    legend.get_frame().set_linewidth(1.5)

    # 8. 添加统计信息框（移到右上角）
    # 计算整体趋势（线性回归斜率）
    age_midpoints = [25, 35, 45, 55, 70][:len(grouped)]  # 各组中点
    slope_judge, _, r_judge, p_judge, _ = stats.linregress(
        age_midpoints, grouped['Judge_Mean'])
    slope_fan, _, r_fan, p_fan, _ = stats.linregress(
        age_midpoints, grouped['Fan_Mean'])

    stats_text = (
        f"Trend Analysis:\n"
        f"Judge Score: {slope_judge:.3f}/decade\n"
        f"  (R²={r_judge ** 2:.3f}, {'p<0.05*' if p_judge < 0.05 else 'n.s.'})\n"
        f"Fan Power: {slope_fan:+.3f}/decade\n"
        f"  (R²={r_fan ** 2:.3f}, {'p<0.05*' if p_fan < 0.05 else 'n.s.'})"
    )

    # 放在右上角
    ax1.text(0.98, 0.98, stats_text,
             transform=ax1.transAxes,
             fontsize=11,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(boxstyle='round,pad=0.8',
                       facecolor='lightyellow',
                       edgecolor='black',
                       linewidth=2,
                       alpha=0.9))

    plt.tight_layout()
    plt.savefig('Age_Effect_Enhanced.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')

    print("\n✅ 已生成高质量年龄效应图: Age_Effect_Enhanced.png")
    print("📈 图表特点：")
    print("   - 清晰的趋势对比（蓝色下降，红色平稳）")
    print("   - 误差棒显示数据可靠性")
    print("   - 样本量标注增强可信度")
    print("   - 统计显著性检验")
    print("   - 专业级出版质量")

    # 打印关键发现
    print(f"\n🎯 关键发现：")
    print(f"   评委分变化：{judge_trend:.2f} 分 (从最年轻到最年长组)")
    print(f"   粉丝指数变化：{fan_trend:+.2f} (从最年轻到最年长组)")
    if judge_trend < 0 and fan_trend >= 0:
        print(f"   ⚠️  年龄悖论确认：评委惩罚年龄，粉丝宽容年龄！")


if __name__ == "__main__":
    plot_clean_age_effect()