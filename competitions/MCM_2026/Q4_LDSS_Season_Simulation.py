import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.lines import Line2D

# 1. 全局设置
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11


# 2. 核心数学模型
def calculate_fan_score(vote_share_pct, k=5.0):
    x = vote_share_pct / 100.0
    score = 10 * np.tanh(k * x)
    return score


# 3. 模拟主程序
def run_simulation():
    print("启动数字孪生模拟: 12位选手 -> 决赛Top 4 (LDSS v2.0)...")
    weeks = np.arange(1, 11)

    # 初始化 12 位选手
    contestants = [
        {'name': 'Traffic King A1', 'group': 'A', 'j': 5.0, 'f_share': 25.0, 'color': '#E74C3C'},
        {'name': 'Traffic King A2', 'group': 'A', 'j': 5.2, 'f_share': 20.0, 'color': '#C0392B'},
        {'name': 'Superstar B1', 'group': 'B', 'j': 8.8, 'f_share': 15.0, 'color': '#2E86C1'},
        {'name': 'Superstar B2', 'group': 'B', 'j': 8.5, 'f_share': 12.0, 'color': '#1A5276'},
        {'name': 'Pro Dancer C1', 'group': 'C', 'j': 8.0, 'f_share': 4.0, 'color': '#F1C40F'},
        {'name': 'Pro Dancer C2', 'group': 'C', 'j': 7.8, 'f_share': 3.0, 'color': '#D4AC0D'},
        {'name': 'Fodder D1', 'group': 'D', 'j': 5.0, 'f_share': 1.0, 'color': 'gray'},
        {'name': 'Fodder D2', 'group': 'D', 'j': 5.5, 'f_share': 2.0, 'color': 'silver'},
        {'name': 'Reality E1', 'group': 'E', 'j': 6.0, 'f_share': 8.0, 'color': '#E67E22'},
        {'name': 'Reality E2', 'group': 'E', 'j': 5.8, 'f_share': 7.0, 'color': '#D35400'},
        {'name': 'Journey F1', 'group': 'F', 'j': 7.0, 'f_share': 2.0, 'color': '#9B59B6'},
        {'name': 'Journey F2', 'group': 'F', 'j': 6.8, 'f_share': 1.0, 'color': '#8E44AD'}
    ]

    for c in contestants:
        c['status'] = 'Active'
        c['j_growth'] = 0.1

    history = []

    for week in weeks:
        # 动态权重
        progress = (week - 1) / 9.0
        w_fan = 0.6 - (0.2 * progress)
        w_judge = 0.4 + (0.2 * progress)

        active = [c for c in contestants if c['status'] == 'Active']
        N = len(active)

        # 这里的判断是为了防止空转，实际决赛判断在下面
        if N < 2: break

        round_data = []
        for c in active:
            current_j = min(10, c['j'] + c['j_growth'] * (week - 1))
            scaling = 1.0 + (12 - N) * 0.05
            current_f_share = c['f_share'] * scaling
            current_f_score = calculate_fan_score(current_f_share)
            total = w_judge * current_j + w_fan * current_f_score
            gap = abs(current_j - current_f_score)

            round_data.append({
                'name': c['name'], 'group': c['group'],
                'j': current_j, 'f': current_f_score, 'total': total, 'gap': gap
            })

            history.append({
                'Week': week, 'Name': c['name'], 'Group': c['group'],
                'Total Score': total, 'Color': c['color'], 'Status': 'Safe'
            })

        round_data.sort(key=lambda x: x['total'])

        # --- 修改点 1: 决赛判定人数改为 4 ---
        if N <= 4:  # <--- 修改这里 (原本是 <= 3)
            winner = round_data[-1]
            print(f"🏆 WEEK {week} FINAL (Top 4): Winner is {winner['name']} (Score: {winner['total']:.2f})")
            break  # 停止模拟，决赛周不进行淘汰

        # 淘汰逻辑
        bottom_2 = round_data[:2]
        p1, p2 = bottom_2[0], bottom_2[1]
        victim = None

        if N > 7:
            # Phase 1: 流量保护 (Week 1-5)
            if p1['gap'] < p2['gap']:
                victim = p1
            else:
                victim = p2
        else:
            # Phase 2: 精英收束 (Week 6-8)
            # 因为我们要剩4个人，所以 Phase 2 会少淘汰一个人
            if p1['j'] < p2['j']:
                victim = p1
            else:
                victim = p2

        for c in contestants:
            if c['name'] == victim['name']:
                c['status'] = 'Eliminated'

        for h in history:
            if h['Name'] == victim['name'] and h['Week'] == week:
                h['Status'] = 'Eliminated'

    # 4. 可视化生成
    print("正在生成可视化图表...")
    df_hist = pd.DataFrame(history)
    fig, ax = plt.subplots(figsize=(14, 8))

    for c in contestants:
        subset = df_hist[df_hist['Name'] == c['name']]
        if subset.empty: continue

        alpha = 1.0
        lw = 3.0
        zorder = 5
        if 'Fodder' in c['name'] or 'Journey' in c['name']:
            alpha = 0.3
            lw = 1.5
            zorder = 1

        ax.plot(subset['Week'], subset['Total Score'], marker='o',
                color=c['color'], alpha=alpha, linewidth=lw, label=c['name'], zorder=zorder)

        elim = subset[subset['Status'] == 'Eliminated']
        if not elim.empty:
            ew = elim['Week'].values[0]
            es = elim['Total Score'].values[0]
            ax.scatter([ew], [es], color='black', marker='x', s=150, zorder=10)

    # --- 修改点 2: 调整背景区域坐标 ---

    # Phase 1 (Green): Week 1-5 (12人 -> 7人) - 不变
    ax.axvspan(0.5, 5.5, color='#E9F7EF', alpha=0.4)
    ax.text(3, 9.6, "PHASE 1: TRAFFIC PROTECTION\n(N > 7)", ha='center', color='green', fontweight='bold', fontsize=12)

    # Phase 2 (Red): Week 6-8 (7人 -> 4人) - 变窄了
    # Week 6: 7->6
    # Week 7: 6->5
    # Week 8: 5->4 (这就是最后一次淘汰)
    # Week 9: 4人进入决赛
    # 所以 Phase 2 是 Week 6, 7, 8 (坐标 5.5 到 8.5)
    ax.axvspan(5.5, 8.5, color='#FADBD8', alpha=0.4)  # <--- 修改这里 (原本是 9.5)
    ax.text(7, 9.6, "PHASE 2: ELITE QUALITY\n(N <= 7)", ha='center', color='#C0392B', fontweight='bold', fontsize=12)

    # Phase 3 (Gold): Week 9+ (Finale) - 提前了
    ax.axvspan(8.5, 10.5, color='#FEF9E7', alpha=0.4)  # <--- 修改这里 (原本是 9.5)
    ax.text(9.5, 9.6, "PHASE 3\nTOP 4 FINALE", ha='center', color='#F39C12', fontweight='bold',
            fontsize=12)  # <--- 坐标改到 9.5

    # 标注 Traffic King 淘汰
    tk = df_hist[df_hist['Name'].str.contains('Traffic King')]
    tk_elim = tk[tk['Status'] == 'Eliminated']
    for idx, row in tk_elim.iterrows():
        ax.annotate(f"{row['Name']}\nEliminated\n(Low Judge Score)",
                    xy=(row['Week'], row['Total Score']),
                    xytext=(row['Week'], row['Total Score'] + 0.8),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                    fontsize=9, fontweight='bold', ha='center', color='#C0392B')

    ax.set_title("Digital Twin Simulation (Top 4 Finale): Efficacy of the LDSS Model", fontsize=18, fontweight='bold',
                 pad=20)
    ax.set_xlabel("Competition Week", fontsize=14, fontweight='bold')
    ax.set_ylabel("Weighted Total Score", fontsize=14, fontweight='bold')
    ax.set_xticks(weeks)
    ax.set_ylim(0.5, 10.5)

    custom_lines = [
        Line2D([0], [0], color='#E74C3C', lw=3),
        Line2D([0], [0], color='#2E86C1', lw=3),
        Line2D([0], [0], color='#F1C40F', lw=3),
        Line2D([0], [0], color='gray', lw=3, alpha=0.5),
    ]
    ax.legend(custom_lines,
              ['Traffic King (Bobby Type)', 'Superstar (Champion)', 'Underrated Pro (Jerry Type)', 'Others'],
              loc='lower left', ncol=2, fontsize=10, frameon=True)

    plt.tight_layout()
    plt.savefig('LDSS_12_Player_Top4_Simulation.png')
    print("✅ 可视化完成! 图片已保存为: LDSS_12_Player_Top4_Simulation.png")


if __name__ == "__main__":
    run_simulation()