import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi

# 1. 全局绘图设置
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

# ---------------------------------------------------------
# 图表 1: 六种人数字孪生雷达图 (6 Archetypes Radar)
# ---------------------------------------------------------
def plot_radar_chart_6_groups():
    print("正在生成六种人雷达图...")

    # 定义 5 个属性维度 (归一化到 0-10 分)
    categories = ['Judge Score\n(Tech)', 'Fan Strength\n(Pop)', 'Growth\n(Potential)', 'Controversy\n(Gap)', 'Base\nScore']
    N = len(categories)

    # 计算角度
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1] # 闭合回路

    # --- 定义六种原型的数据 ---
    # A: Traffic King (高粉低评)
    data_A = [5.0, 9.0, 3.0, 10.0, 6.0]
    # B: Superstar (双高)
    data_B = [9.0, 8.0, 4.0, 2.0, 9.5]
    # C: Underrated Pro (高评低粉)
    data_C = [8.0, 2.0, 5.0, 6.0, 6.5]
    # D: Cannon Fodder (双低)
    data_D = [5.0, 1.0, 1.0, 4.0, 3.5]
    # E: Reality Star (中粉低评)
    data_E = [6.0, 5.0, 2.0, 2.0, 5.5]
    # F: Journeyman (低粉中评)
    data_F = [7.0, 1.5, 2.0, 5.0, 5.0]

    # 数据闭合
    for data in [data_A, data_B, data_C, data_D, data_E, data_F]:
        data += data[:1]

    # 绘图
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

    # 绘制线条和填充
    ax.plot(angles, data_A, linewidth=2, linestyle='-', label='A: Traffic King', color='#E74C3C')
    ax.fill(angles, data_A, '#E74C3C', alpha=0.1)

    ax.plot(angles, data_B, linewidth=2, linestyle='-', label='B: Superstar', color='#2E86C1')
    ax.fill(angles, data_B, '#2E86C1', alpha=0.1)

    ax.plot(angles, data_C, linewidth=2, linestyle='-', label='C: Underrated Pro', color='#F1C40F')

    ax.plot(angles, data_D, linewidth=2, linestyle='--', label='D: Cannon Fodder', color='gray')

    ax.plot(angles, data_E, linewidth=2, linestyle='-.', label='E: Reality Star', color='#E67E22')

    ax.plot(angles, data_F, linewidth=2, linestyle=':', label='F: Journeyman', color='#9B59B6')

    # 设置刻度
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], color="grey", size=9)
    ax.set_ylim(0, 10)

    plt.title("Digital Twin Archetypes: 6-Dimensional Profiles", size=16, y=1.08, fontweight='bold')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()
    plt.savefig('Archetype_Radar_Chart_6.png')
    print("✅ 雷达图已生成: Archetype_Radar_Chart_6.png")

# ---------------------------------------------------------
# 图表 2: LDSS 决策曲面 (含 12 个点位标注)
# ---------------------------------------------------------
def plot_decision_surface_12_points():
    print("正在生成决策曲面图 (12人版)...")

    # 生成网格
    judge_scores = np.linspace(0, 10, 100)
    fan_shares = np.linspace(0, 50, 100)
    X, Y = np.meshgrid(judge_scores, fan_shares)

    # 计算曲面高度 (Z = 总分)
    w_j = 0.5
    w_f = 0.5
    k = 5.0
    Z = w_j * X + w_f * (10 * np.tanh(k * Y / 100.0))

    fig, ax = plt.subplots(figsize=(12, 9))

    # 绘制等高线
    cp = ax.contourf(X, Y, Z, levels=25, cmap='viridis')
    cbar = fig.colorbar(cp)
    cbar.set_label('Weighted Total Score (0-10)', fontsize=12, fontweight='bold')

    # --- 定义 12 位选手数据 (每组 2 人) ---
    contestants = [
        # A组: 流量王 (红)
        {'name': 'A1', 'j': 5.0, 'f': 25.0, 'c': '#E74C3C', 'm': 'X', 'l': 'Traffic King (A)'},
        {'name': 'A2', 'j': 5.2, 'f': 20.0, 'c': '#C0392B', 'm': 'X', 'l': '_nolegend_'},

        # B组: 巨星 (蓝)
        {'name': 'B1', 'j': 8.8, 'f': 15.0, 'c': '#2E86C1', 'm': 'o', 'l': 'Superstar (B)'},
        {'name': 'B2', 'j': 8.5, 'f': 12.0, 'c': '#1A5276', 'm': 'o', 'l': '_nolegend_'},

        # C组: 实力派 (黄)
        {'name': 'C1', 'j': 8.0, 'f': 4.0,  'c': '#F1C40F', 'm': 's', 'l': 'Underrated Pro (C)'},
        {'name': 'C2', 'j': 7.8, 'f': 3.0,  'c': '#D4AC0D', 'm': 's', 'l': '_nolegend_'},

        # D组: 炮灰 (灰)
        {'name': 'D1', 'j': 5.0, 'f': 1.0,  'c': 'gray',    'm': 'v', 'l': 'Cannon Fodder (D)'},
        {'name': 'D2', 'j': 5.5, 'f': 2.0,  'c': 'silver',  'm': 'v', 'l': '_nolegend_'},

        # E组: 真人秀咖 (橙)
        {'name': 'E1', 'j': 6.0, 'f': 8.0,  'c': '#E67E22', 'm': 'D', 'l': 'Reality Star (E)'},
        {'name': 'E2', 'j': 5.8, 'f': 7.0,  'c': '#D35400', 'm': 'D', 'l': '_nolegend_'},

        # F组: 中庸者 (紫)
        {'name': 'F1', 'j': 7.0, 'f': 2.0,  'c': '#9B59B6', 'm': '^', 'l': 'Journeyman (F)'},
        {'name': 'F2', 'j': 6.8, 'f': 1.0,  'c': '#8E44AD', 'm': '^', 'l': '_nolegend_'},
    ]

    # 绘制散点和标签
    for c in contestants:
        # 画点
        ax.scatter([c['j']], [c['f']], color=c['c'], marker=c['m'], s=150,
                   edgecolors='white', linewidth=1.5, label=c['l'], zorder=10)

        # 加标签 (带背景色的小框，防止看不清)
        ax.text(c['j'], c['f'] + 1.2, c['name'], color='white',
                fontweight='bold', fontsize=9, ha='center',
                bbox=dict(facecolor=c['c'], alpha=0.7, edgecolor='none', pad=1))

    # 添加参考线
    ax.axhline(20, color='white', linestyle='--', alpha=0.5)
    ax.text(0.5, 20.5, "Saturation Threshold (20%)", color='white', fontsize=10)

    # 标题和坐标轴
    ax.set_title("LDSS Decision Surface: 12 Digital Twins Distribution", fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel("Judge Score (0-10)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Fan Vote Share (%)", fontsize=12, fontweight='bold')

    # 图例放在右上角
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9, fontsize=10, title="Archetypes")

    plt.tight_layout()
    plt.savefig('LDSS_Decision_Surface_12.png')
    print("✅ 决策曲面图已生成: LDSS_Decision_Surface_12.png")

if __name__ == "__main__":
    plot_radar_chart_6_groups()
    plot_decision_surface_12_points()