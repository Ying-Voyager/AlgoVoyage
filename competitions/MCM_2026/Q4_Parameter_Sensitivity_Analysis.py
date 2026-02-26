import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 1. 全局设置
sns.set_style("white")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11


# 2. 核心数学模型
def calculate_fan_score(vote_share_pct, k):
    x = vote_share_pct / 100.0
    score = 10 * np.tanh(k * x)
    return score


# 3. 单次全赛程模拟函数
def run_single_simulation(k_value):
    weeks = np.arange(1, 11)

    # --- 定义 12 位选手 (6种原型 x 2人) ---
    contestants = [
        # Group A: Traffic King
        {'name': 'Traffic King (A)', 'j': 5.0, 'f_share': 25.0},
        {'name': 'Traffic King (A2)', 'j': 5.2, 'f_share': 20.0},
        # Group B: Superstar
        {'name': 'Superstar (B)', 'j': 8.8, 'f_share': 15.0},
        {'name': 'Superstar (B2)', 'j': 8.5, 'f_share': 12.0},
        # Group C: Underrated Pro
        {'name': 'Underrated (C)', 'j': 8.0, 'f_share': 4.0},
        {'name': 'Underrated (C2)', 'j': 7.8, 'f_share': 3.0},
        # Group D: Cannon Fodder
        {'name': 'Fodder (D)', 'j': 5.0, 'f_share': 1.0},
        {'name': 'Fodder (D2)', 'j': 5.5, 'f_share': 2.0},
        # Group E: Reality Star
        {'name': 'Reality (E)', 'j': 6.0, 'f_share': 8.0},
        {'name': 'Reality (E2)', 'j': 5.8, 'f_share': 7.0},
        # Group F: Journeyman
        {'name': 'Journey (F)', 'j': 7.0, 'f_share': 2.0},
        {'name': 'Journey (F2)', 'j': 6.8, 'f_share': 1.0}
    ]

    for c in contestants:
        c['status'] = 'Active'
        c['final_score'] = 0

    eliminated_order = []

    for week in weeks:
        # 动态权重
        progress = (week - 1) / 9.0
        w_fan = 0.6 - (0.2 * progress)
        w_judge = 0.4 + (0.2 * progress)

        active = [c for c in contestants if c['status'] == 'Active']
        N = len(active)
        if N < 2: break

        round_data = []
        for c in active:
            # 简化成长
            curr_j = min(10, c['j'] + 0.1 * (week - 1))
            # 粉丝分受 k 影响
            scaling = 1.0 + (12 - N) * 0.05
            curr_f = calculate_fan_score(c['f_share'] * scaling, k_value)

            total = w_judge * curr_j + w_fan * curr_f
            gap = abs(curr_j - curr_f)

            c['final_score'] = total
            round_data.append({'name': c['name'], 'total': total, 'gap': gap, 'j': curr_j})

        round_data.sort(key=lambda x: x['total'])

        # 决赛圈 (Top 4)
        if N <= 4:
            pass
        else:
            # 淘汰逻辑
            bottom_2 = round_data[:2]
            p1, p2 = bottom_2[0], bottom_2[1]
            victim_name = None

            if N > 7:  # Phase 1
                if p1['gap'] < p2['gap']:
                    victim_name = p1['name']
                else:
                    victim_name = p2['name']
            else:  # Phase 2
                if p1['j'] < p2['j']:
                    victim_name = p1['name']
                else:
                    victim_name = p2['name']

            # 标记淘汰
            for c in contestants:
                if c['name'] == victim_name:
                    c['status'] = 'Eliminated'
                    eliminated_order.append(c)

    # 计算最终排名
    survivors = [c for c in contestants if c['status'] == 'Active']
    survivors.sort(key=lambda x: x['final_score'], reverse=True)
    eliminated_order.reverse()

    final_ranking = {}
    rank = 1
    for s in survivors:
        final_ranking[s['name']] = rank
        rank += 1
    for e in eliminated_order:
        final_ranking[e['name']] = rank
        rank += 1

    return final_ranking


# 4. 批量运行灵敏度分析 (包含 6 类人)
def run_sensitivity_analysis_full():
    print("正在运行全员灵敏度分析 (6 Archetypes)...")

    k_range = np.linspace(2, 8, 13)
    results = []

    # 目标：绘制 6 个原型的代表人物
    target_names = [
        'Superstar (B)',
        'Underrated (C)',
        'Journey (F)',
        'Reality (E)',
        'Traffic King (A)',
        'Fodder (D)'
    ]

    for k in k_range:
        rankings = run_single_simulation(k)
        row = {'k': k}
        for name in target_names:
            row[name] = rankings[name]
        results.append(row)

    df = pd.DataFrame(results)

    # 5. 绘图
    fig, ax = plt.subplots(figsize=(12, 7))

    # 颜色与样式配置
    configs = {
        'Superstar (B)': {'c': '#2E86C1', 'm': 'o', 'lw': 3, 'ls': '-'},  # 蓝实线 (冠军)
        'Underrated (C)': {'c': '#F1C40F', 'm': 's', 'lw': 2.5, 'ls': '-'},  # 黄实线 (决赛)
        'Journey (F)': {'c': '#9B59B6', 'm': '^', 'lw': 2, 'ls': '--'},  # 紫虚线 (中游)
        'Reality (E)': {'c': '#E67E22', 'm': 'D', 'lw': 2, 'ls': '--'},  # 橙虚线 (中游)
        'Traffic King (A)': {'c': '#E74C3C', 'm': 'X', 'lw': 3, 'ls': '-'},  # 红实线 (主角)
        'Fodder (D)': {'c': 'gray', 'm': 'v', 'lw': 1.5, 'ls': ':'}  # 灰点线 (炮灰)
    }

    for name in target_names:
        cfg = configs[name]
        ax.plot(df['k'], df[name], label=name, color=cfg['c'],
                marker=cfg['m'], linewidth=cfg['lw'], linestyle=cfg['ls'], markersize=8)

    # 区域背景
    ax.axhspan(0.5, 4.5, color='#FEF9E7', alpha=0.4)
    ax.text(2.1, 1.5, "FINALIST ZONE (Top 4)", color='#F39C12', fontweight='bold', fontsize=12)

    ax.axhspan(4.5, 12.5, color='#FADBD8', alpha=0.4)
    ax.text(2.1, 11.5, "ELIMINATION ZONE", color='#C0392B', fontweight='bold', fontsize=12)

    # 标注 k=5
    ax.axvline(5.0, color='green', linestyle='-', alpha=0.5, linewidth=10)  # 绿色高亮带
    ax.text(5.0, 0.2, "Selected Parameter (k=5)", color='green', fontweight='bold', ha='center', va='top')

    ax.set_title("Full-Spectrum Sensitivity Analysis: Rank Stability vs. Parameter k", fontsize=16, fontweight='bold')
    ax.set_xlabel("Tanh Saturation Parameter (k)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Final Rank (1=Winner, 12=Last)", fontsize=12, fontweight='bold')
    ax.set_yticks(range(1, 13))
    ax.invert_yaxis()

    # 调整图例位置
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, fontsize=10)

    plt.tight_layout()
    plt.savefig('Q4_Sensitivity_Full_Spectrum.png')
    print("✅ 全员灵敏度图已生成: Q4_Sensitivity_Full_Spectrum.png")


if __name__ == "__main__":
    run_sensitivity_analysis_full()