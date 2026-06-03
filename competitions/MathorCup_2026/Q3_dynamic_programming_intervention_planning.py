import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_excel('data_with_risk.xlsx')

# ============================================================
# 工具函数
# ============================================================
def get_tcm_cost(score):
    """根据痰湿积分返回当月中医调理费用"""
    if score <= 58:   return 30,  1, '基础调理'
    elif score <= 61: return 80,  2, '中度调理'
    else:             return 130, 3, '强化调理'

def get_act_unit_cost(I):
    """活动干预单次成本"""
    return {1: 3, 2: 5, 3: 8}[I]

def get_intensity_limit(age_group, act_score):
    """年龄+活动量表综合强度上限"""
    age_max = 3 if age_group <= 2 else (2 if age_group <= 4 else 1)
    act_max = 1 if act_score < 40 else (2 if act_score < 60 else 3)
    return min(age_max, act_max), age_max, act_max

def get_decline_rate(I, f):
    """月度积分下降率（f<5时为0）"""
    return (0.03 * I + 0.01 * (f - 5)) if f >= 5 else 0.0

def simulate(S0, strategy):
    """
    模拟6个月干预过程
    strategy: list of (I, f) tuples, length 6
    返回：最终积分、总成本、积分轨迹、每月成本明细
    """
    S          = S0
    total_cost = 0
    scores     = [S0]
    monthly_details = []

    for I, f in strategy:
        tcm_cost, tcm_level, tcm_name = get_tcm_cost(S)
        act_cost  = 4 * f * get_act_unit_cost(I)
        month_cost = tcm_cost + act_cost
        total_cost += month_cost

        R      = get_decline_rate(I, f)
        S_next = S * (1 - R)

        monthly_details.append({
            'I': I, 'f': f,
            'R': R,
            'tcm_cost': tcm_cost, 'tcm_level': tcm_level,
            'tcm_name': tcm_name, 'act_cost': act_cost,
            'month_cost': month_cost,
            'S_before': S, 'S_after': S_next
        })
        S = S_next
        scores.append(S)

    return S, total_cost, scores, monthly_details

# ============================================================
# 动态规划求解器
# 状态：(月份t, 当前积分×100取整, 剩余预算×10取整)
# 每月决策空间：I∈{1..I_max}, f∈{5..f_max}
# （f<5时积分不下降，最优解不会选；f_max由活动量表耐受度决定）
# ============================================================
def get_frequency_limit(act_score):
    """根据活动量表评分返回频率耐受上限（C5约束）"""
    if act_score < 40:   return 5
    elif act_score < 60: return 8
    else:                return 10

def solve_dp(S0, I_max, f_max, budget=2000, months=6):
    I_choices = list(range(1, I_max + 1))
    f_choices = list(range(5, f_max + 1))

    @lru_cache(maxsize=None)
    def dp(month, S_round, budget_left_10):
        """
        返回 (最终积分, 后续最优策略列表)
        S_round     = round(S * 100)    积分×100取整避免浮点误差
        budget_left_10 = round(budget_left * 10)  预算×10取整
        """
        S          = S_round / 100.0
        budget_left = budget_left_10 / 10.0

        if month == months:
            return S, []

        best_final = float('inf')
        best_plan  = None

        for I in I_choices:
            for f in f_choices:
                tcm_cost, _, _ = get_tcm_cost(S)
                act_cost = 4 * f * get_act_unit_cost(I)
                cost = tcm_cost + act_cost

                if cost > budget_left + 1e-6:
                    continue

                R      = get_decline_rate(I, f)
                S_next = S * (1 - R)

                future_S, future_plan = dp(
                    month + 1,
                    round(S_next * 100),
                    round((budget_left - cost) * 10)
                )

                if future_S < best_final:
                    best_final = future_S
                    best_plan  = [(I, f)] + future_plan

        if best_plan is None:
            # 预算耗尽，维持现状（选最低成本策略保持积分）
            return S, [(1, 5)] * (months - month)

        return best_final, best_plan

    S0_round = round(S0 * 100)
    final_S, plan = dp(0, S0_round, round(budget * 10))
    dp.cache_clear()
    return final_S, plan

# ============================================================
# 第一步：三位患者基础信息
# ============================================================
print("=" * 65)
print("  模块E：最优干预方案求解（动态规划）")
print("=" * 65)

patients_raw = df[df['样本ID'].isin([1, 2, 3])].copy()

patient_info = {}
for _, row in patients_raw.iterrows():
    sid = int(row['样本ID'])
    S0  = float(row['痰湿质'])
    act = float(row['活动量表总分（ADL总分+IADL总分）'])
    age = int(row['年龄组'])
    I_max, age_max, act_max = get_intensity_limit(age, act)
    f_max = get_frequency_limit(act)
    patient_info[sid] = {
        'S0': S0, 'act': act, 'age': age,
        'I_max': I_max, 'age_max': age_max, 'act_max': act_max,
        'f_max': f_max
    }

# ============================================================
# 第二步：DP 求解每位患者最优方案
# ============================================================
print("\n" + "=" * 65)
print("  第二步：动态规划求解最优6个月方案")
print("=" * 65)

intensity_label = {1: '低强度', 2: '中强度', 3: '高强度'}
solutions = {}

for sid, info in patient_info.items():
    S0    = info['S0']
    I_max = info['I_max']

    f_max = info['f_max']
    print(f"\n  ── 样本{sid}（S0={S0}, I_max={I_max}, f_max={f_max}次/周）──")
    final_S, plan = solve_dp(S0, I_max, f_max)
    final_S2, total_cost, scores, details = simulate(S0, plan)

    solutions[sid] = {
        'plan': plan, 'final_S': final_S2,
        'total_cost': total_cost,
        'scores': scores, 'details': details,
        'S0': S0, 'I_max': I_max, 'f_max': f_max
    }

    drop = S0 - final_S2
    drop_pct = drop / S0 * 100

    print(f"  初始积分：{S0:.1f}  →  最终积分：{final_S2:.2f}")
    print(f"  积分降幅：{drop:.2f}分（{drop_pct:.1f}%）")
    print(f"  6个月总成本：{total_cost:.0f}元（预算上限2000元）")
    print()
    print(f"  {'月份':>4} {'强度':>4} {'频率':>6} {'下降率':>8} "
          f"{'中医调理':>10} {'活动成本':>8} {'月总费':>8} {'月末积分':>8}")
    print("  " + "-" * 62)
    for t, d in enumerate(details, 1):
        print(f"  {t:>4}月 {intensity_label[d['I']]:>4} "
              f"{d['f']:>4}次/周 {d['R']*100:>7.1f}% "
              f"  {d['tcm_name']}({d['tcm_level']}级){d['tcm_cost']:>4}元 "
              f"{d['act_cost']:>6}元 {d['month_cost']:>6}元 "
              f"{d['S_after']:>7.2f}分")

# ============================================================
# 第三步：患者特征-最优方案匹配规律总结
# ============================================================
print("\n" + "=" * 65)
print("  第三步：患者特征-最优方案匹配规律")
print("=" * 65)

print("""
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  规律一｜受限型患者（样本1）：双重受限，频率踩线
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  特征：活动量表 38分（<40），强度上限 I_max=1，
        频率耐受上限 f_max=5次/周（耐受度弱）。
  策略：全程 I=1, f=5（强度和频率均触底）。
  机制：活动量表低于40分，强度和频率双重受限，
        每月下降率仅3%（I=1, f=5的最低有效率），
        积分下降缓慢，但调理费随积分自然递降，
        预算利用率低，干预空间极为有限。
  关键词：双重耐受受限 → 频率踩及格线 → 缓慢下降

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  规律二｜均衡型患者（样本2）：强度拉满，频率受限
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  特征：活动量表 40分，强度上限 I_max=2，
        频率耐受上限 f_max=8次/周（耐受度中等）。
  策略：全程 I=2, f=8（强度最大，频率取耐受上限）。
  机制：初始积分58分已在基础调理范围（30元/月），
        调理成本全程最低，预算集中于活动干预。
        月下降率固定9%（I=2, f=8），6个月积分降幅约43%。
  关键词：成本优势 → 强度拉满 → 频率受耐受度约束

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  规律三｜激进型患者（样本3）：动态调整，先均衡后拉满
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  特征：活动量表 63分（≥60），强度上限 I_max=3，
        频率耐受上限 f_max=10次/周（耐受度强，无额外限制）。
  策略：第1月 I=2, f=10；第2月起 I=3, f=9-10。
  机制：初始积分59分处于中度调理（80元/月），预算紧张，
        第1月先用中强度将积分降至58分以下触发基础调理，
        第2月起切换为高强度+高频，积分持续加速下降。
        活动量表≥60分保证了高频率的耐受度，方案无频率瓶颈。
  关键词：耐受度充足 → 预算敏感 → 动态跃迁
""")

# ============================================================
# 画图：三位患者方案全景图
# 图1：积分下降趋势折线图
# 图2：每月成本构成堆叠柱状图
# 图3：策略热力图（强度×频率，按月展示）
# ============================================================
fig = plt.figure(figsize=(20, 15))
gs  = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.38)

colors_p   = {1: '#d73027', 2: '#4575b4', 3: '#1a9850'}
month_labels = ['第1月', '第2月', '第3月', '第4月', '第5月', '第6月']

# ---------- 图1-3：三位患者积分趋势图（第一行）----------
for idx, sid in enumerate([1, 2, 3]):
    ax = fig.add_subplot(gs[0, idx])
    sol = solutions[sid]
    x   = list(range(7))
    ax.plot(x, sol['scores'], 'o-', color=colors_p[sid],
            linewidth=2.5, markersize=8, zorder=3)

    # 标注每月积分
    for xi, s in enumerate(sol['scores']):
        ax.annotate(f'{s:.1f}',
                    (xi, s),
                    xytext=(0, 10), textcoords='offset points',
                    ha='center', fontsize=9, color=colors_p[sid],
                    fontweight='bold')

    # 调理等级边界线
    ax.axhline(58, color='#fdae61', linewidth=1.2, linestyle='--',
               alpha=0.8, label='58分（3→1级调理临界）')
    ax.axhline(62, color='#d73027', linewidth=1.2, linestyle=':',
               alpha=0.6, label='62分（强化调理起点）')

    ax.fill_between(x, sol['scores'],
                    alpha=0.1, color=colors_p[sid])
    ax.set_xticks(x)
    ax.set_xticklabels(['初始'] + month_labels, fontsize=8, rotation=15)
    ax.set_ylabel('痰湿积分', fontsize=10)
    ax.set_title(f'样本{sid} 痰湿积分下降趋势\n'
                 f'({sol["S0"]:.0f}分 → {sol["final_S"]:.2f}分，'
                 f'降幅{(sol["S0"]-sol["final_S"])/sol["S0"]*100:.1f}%)',
                 fontsize=10, fontweight='bold')
    ax.legend(fontsize=7, loc='upper right')
    ax.set_ylim(min(sol['scores']) - 5, sol['S0'] + 5)

# ---------- 图4-6：三位患者月度成本堆叠图（第二行）----------
for idx, sid in enumerate([1, 2, 3]):
    ax = fig.add_subplot(gs[1, idx])
    sol = solutions[sid]

    tcm_costs = [d['tcm_cost'] for d in sol['details']]
    act_costs = [d['act_cost'] for d in sol['details']]
    x = np.arange(6)

    b1 = ax.bar(x, tcm_costs, color='#74add1',
                label='中医调理费', edgecolor='white', alpha=0.9)
    b2 = ax.bar(x, act_costs, bottom=tcm_costs,
                color=colors_p[sid], label='活动干预费',
                edgecolor='white', alpha=0.85)

    # 柱顶标注月总费
    for xi, (tc, ac) in enumerate(zip(tcm_costs, act_costs)):
        ax.text(xi, tc + ac + 2, f'{tc+ac}元',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

    # 标注调理等级变化
    for xi, d in enumerate(sol['details']):
        ax.text(xi, tc/2 if (tc := d['tcm_cost']) > 0 else 5,
                f'{d["tcm_level"]}级',
                ha='center', va='center', fontsize=8,
                color='white', fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(month_labels, fontsize=9)
    ax.set_ylabel('费用（元）', fontsize=10)
    ax.set_title(f'样本{sid} 月度成本构成\n总计 {sol["total_cost"]:.0f}元',
                 fontsize=10, fontweight='bold')
    ax.legend(fontsize=9)
    ax.set_ylim(0, max(tc + ac for tc, ac in zip(tcm_costs, act_costs)) * 1.2)

# ---------- 图7：三患者策略对比热力图（第三行通栏）----------
ax_heat = fig.add_subplot(gs[2, :])

# 构建策略矩阵（行=患者，列=月份，值=强度×频率编码）
strategy_matrix_I = np.zeros((3, 6))
strategy_matrix_f = np.zeros((3, 6))
for ri, sid in enumerate([1, 2, 3]):
    for ci, (I, f) in enumerate(solutions[sid]['plan']):
        strategy_matrix_I[ri, ci] = I
        strategy_matrix_f[ri, ci] = f

# 用强度作为颜色，频率作为文字
im = ax_heat.imshow(strategy_matrix_I, cmap='RdYlGn',
                    aspect='auto', vmin=1, vmax=3)
cbar = plt.colorbar(im, ax=ax_heat, orientation='vertical',
                    fraction=0.02, pad=0.02)
cbar.set_label('活动干预强度 I', fontsize=10)
cbar.set_ticks([1, 2, 3])
cbar.set_ticklabels(['1级（低）', '2级（中）', '3级（高）'])

for ri in range(3):
    for ci in range(6):
        I = int(strategy_matrix_I[ri, ci])
        f = int(strategy_matrix_f[ri, ci])
        R = get_decline_rate(I, f)
        ax_heat.text(ci, ri,
                     f'I={I}, f={f}\n↓{R*100:.0f}%/月',
                     ha='center', va='center', fontsize=10,
                     fontweight='bold',
                     color='white' if I == 3 else 'black')

ax_heat.set_xticks(range(6))
ax_heat.set_xticklabels(month_labels, fontsize=11)
ax_heat.set_yticks([0, 1, 2])
ax_heat.set_yticklabels(
    [f'样本{sid}\n(I_max={solutions[sid]["I_max"]}级)' for sid in [1, 2, 3]],
    fontsize=11)
ax_heat.set_title('三位患者最优方案策略矩阵\n'
                  '（颜色=干预强度，文字=强度×频率×月下降率）',
                  fontsize=12, fontweight='bold')

plt.suptitle('模块E：最优干预方案求解（动态规划）\n'
             '目标：6个月内使痰湿积分降至最低，总成本 ≤ 2000元',
             fontsize=14, fontweight='bold', y=1.01)
plt.savefig('模块E_最优干预方案.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# 第四步：论文正文可直接引用的方案描述
# ============================================================
print("=" * 65)
print("  第四步：论文正文方案描述（可直接引用）")
print("=" * 65)

for sid in [1, 2, 3]:
    sol  = solutions[sid]
    info = patient_info[sid]
    drop = sol['S0'] - sol['final_S']
    print(f"""
  【样本{sid}最优干预方案】
  患者基本特征：年龄组{info['age']}（{'40-49' if info['age']==1 else '50-59'}岁），
  活动量表总分{info['act']:.0f}分，初始痰湿积分{sol['S0']:.0f}分，
  干预强度上限 I_max = {info['I_max']}级。

  最优方案：""")
    for t, d in enumerate(sol['details'], 1):
        print(f"    第{t}月：{intensity_label[d['I']]}（I={d['I']}）× "
              f"{d['f']}次/周，月降{d['R']*100:.0f}%，"
              f"月费{d['month_cost']}元（{d['tcm_name']}{d['tcm_cost']}元+"
              f"活动{d['act_cost']}元）")
    print(f"  方案效果：6个月痰湿积分从{sol['S0']:.0f}分降至"
          f"{sol['final_S']:.2f}分，")
    print(f"            累计下降{drop:.2f}分（{drop/sol['S0']*100:.1f}%），")
    print(f"            6个月总费用{sol['total_cost']:.0f}元，")
    print(f"            预算利用率{sol['total_cost']/2000*100:.1f}%。")

print()
print("✅ 模块E完成，结果已保存至 模块E_最优干预方案.png")
print("   下一步：模块F（结果可视化与匹配规律汇总）")
