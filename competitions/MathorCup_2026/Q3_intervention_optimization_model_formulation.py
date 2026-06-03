
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120

df = pd.read_excel('data_with_risk.xlsx')

print("=" * 65)
print("  模块D：痰湿体质患者6个月干预方案优化模型")
print("=" * 65)

print("\n" + "=" * 65)
print("  第一步：目标患者基础信息")
print("=" * 65)

patients_raw = df[df['样本ID'].isin([1, 2, 3])].copy()

age_map = {1: '40-49岁', 2: '50-59岁', 3: '60-69岁', 4: '70-79岁', 5: '80-89岁'}

def get_tcm_level(score):
    if score <= 58:
        return 1, 30, '基础调理'
    elif score <= 61:
        return 2, 80, '中度调理'
    else:
        return 3, 130, '强化调理'

def get_intensity_limit(age_group, act_score):
    age_max = 3 if age_group <= 2 else (2 if age_group <= 4 else 1)
    act_max = 1 if act_score < 40 else (2 if act_score < 60 else 3)
    return min(age_max, act_max), age_max, act_max

def get_frequency_limit(act_score):
    if act_score < 40:
        return 5
    elif act_score < 60:
        return 8
    else:
        return 10

print(f"\n  {'ID':<5} {'初始痰湿质':>9} {'活动量表':>8} {'年龄组':>8} "
      f"{'初始调理级':>10} {'月调理费':>8} {'强度上限':>8} {'风险等级':>8}")
print("  " + "-" * 82)

patient_info = {}
for _, row in patients_raw.iterrows():
    sid = int(row['样本ID'])
    s0 = row['痰湿质']
    act = row['活动量表总分（ADL总分+IADL总分）']
    age = int(row['年龄组'])
    tcm_l, tcm_c, tcm_name = get_tcm_level(s0)
    I_max, age_max, act_max = get_intensity_limit(age, act)
    f_max = get_frequency_limit(act)

    patient_info[sid] = {
        'S0': s0, 'act': act, 'age': age,
        'tcm_level': tcm_l, 'tcm_cost': tcm_c,
        'I_max': I_max, 'age_max': age_max, 'act_max': act_max,
        'f_max': f_max, 'risk': row['风险等级']
    }
    print(f"  {sid:<5} {s0:>9.1f} {act:>8.0f} {age_map[age]:>8} "
          f"{tcm_name}({tcm_l}级){tcm_c:>5}元 {I_max:>6}级 "
          f"f_max={f_max:>2}次/周 {row['风险等级']:>6}")

print("\n" + "=" * 65)
print("  第二步：优化模型三大要素")
print("=" * 65)

print("""
  【一】决策变量
    I_t ∈ {1, 2, 3}     第t个月的活动干预强度
    f_t ∈ {1,2,...,10}  第t个月每周训练频率

  【二】目标函数
    min S_6
    目标为在6个月干预结束时使痰湿积分降至最低。

  【三】约束条件
    C1. 总成本约束：
        ∑[ C_tcm(S_{t-1}) + 4 × f_t × C_act(I_t) ] ≤ 2000 元

    C2. 年龄强度约束：
        40-59岁：I_t ≤ 3
        60-79岁：I_t ≤ 2
        80-89岁：I_t ≤ 1

    C3. 活动量表强度约束：
        活动量表 < 40：I_t ≤ 1
        40 ≤ 活动量表 < 60：I_t ≤ 2
        活动量表 ≥ 60：I_t ≤ 3

    C4. 综合强度上限：
        I_t ≤ min(I_max_age, I_max_act)

    C5. 频率耐受约束：
        活动量表 < 40：f_t ≤ 5次/周
        40 ≤ 活动量表 < 60：f_t ≤ 8次/周
        活动量表 ≥ 60：f_t ≤ 10次/周

    C6. 变量域约束：
        I_t ∈ {1,2,3}，f_t ∈ {1,...,f_max}
""")

print("=" * 65)
print("  第三步：状态转移方程（动态积分演化）")
print("=" * 65)

print("""
  当 f_t < 5 时：
    R(I_t, f_t) = 0

  当 f_t ≥ 5 时：
    R(I_t, f_t) = 3% × I_t + 1% × (f_t - 5)

  状态转移方程：
    S_t = S_{t-1} × [1 - R(I_t, f_t)]

  月度总成本：
    Cost_t = C_tcm(S_{t-1}) + 4 × f_t × C_act(I_t)
""")

print("=" * 65)
print("  第四步：1、2、3号患者约束参数量化")
print("=" * 65)

intensity_name = {1: '低强度(10分钟/次)', 2: '中强度(20分钟/次)', 3: '高强度(30分钟/次)'}

for sid, info in patient_info.items():
    I_max = info['I_max']
    s0 = info['S0']
    act = info['act']
    tcm_l, tcm_c, tcm_name = get_tcm_level(s0)

    act_cost = {1: 3, 2: 5, 3: 8}
    min_act_monthly = 4 * 5 * act_cost.get(I_max, 3)
    max_act_monthly = 4 * info['f_max'] * act_cost.get(I_max, 3)

    budget_min = 6 * 30 + min_act_monthly * 6
    budget_max = 6 * tcm_c + max_act_monthly * 6

    print(f"""
  ── 样本{sid} ──────────────────────────────────────────────
    初始痰湿积分 S_0 = {s0}分  →  初始中医调理：{tcm_name}({tcm_l}级) {tcm_c}元/月
    年龄约束上限：I ≤ {info['age_max']}  活动量表约束：I ≤ {info['act_max']}
    综合强度上限：I_max = {I_max}  （{intensity_name[I_max]}）
    频率上限：f_max = {info['f_max']}次/周（活动量表{act:.0f}分对应的耐受度约束）
    可用频率范围：f ∈ {{5,...,{info['f_max']}}} 次/周
    单月活动成本范围：
      f=5次/周  → {4*5*act_cost[I_max]}元/月
      f={info['f_max']}次/周 → {4*info['f_max']*act_cost[I_max]}元/月
    6个月预算区间（粗估）：[{budget_min}, {budget_max}]元
""")

print("\n\n" + "=" * 65)
print("  第五步：每月积分下降率查询表（f ≥ 5时）")
print("=" * 65)

print(f"\n  {'频率f':>6}", end='')
for I in [1, 2, 3]:
    print(f"  {'I='+str(I)+' 强度':>10}", end='')
print()
print("  " + "-" * 40)

for f in range(5, 11):
    print(f"  {f:>4}次/周", end='')
    for I in [1, 2, 3]:
        R = 0.03 * I + 0.01 * (f - 5)
        print(f"  {R*100:>8.1f}%", end='')
    print()

print(f"\n  f < 5次/周时：各强度下降率均为 0%（积分基本稳定）")

# 图1：三位患者约束参数雷达图
categories = ['初始积分', '活动量表', '强度上限', '初始调理费', '年龄耐受']
patient_vals = {}
for sid, info in patient_info.items():
    _, tcm_c, _ = get_tcm_level(info['S0'])
    patient_vals[sid] = [
        info['S0'] / 65,
        info['act'] / 100,
        info['I_max'] / 3,
        tcm_c / 130,
        info['age_max'] / 3
    ]

angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]
colors_p = {1: '#D94E4E', 2: '#4C78A8', 3: '#54A24B'}

plt.figure(figsize=(8.8, 7.4), facecolor='white')
ax1 = plt.subplot(111, polar=True)
ax1.set_facecolor('white')

for sid, vals in patient_vals.items():
    vals_closed = vals + vals[:1]
    ax1.plot(angles, vals_closed, 'o-', linewidth=2.4, markersize=6,
             color=colors_p[sid], label=f'样本{sid}')
    ax1.fill(angles, vals_closed, alpha=0.12, color=colors_p[sid])

ax1.set_thetagrids(np.degrees(angles[:-1]), categories, fontsize=11)
ax1.set_ylim(0, 1)
ax1.grid(alpha=0.25, linestyle=':')
ax1.set_title('三位患者约束参数雷达图', fontsize=15, fontweight='bold', pad=20)
ax1.legend(loc='upper right', bbox_to_anchor=(1.20, 1.10), fontsize=10, frameon=True)

plt.tight_layout()
plt.show()

# 图2：下降率热力图
plt.figure(figsize=(8.8, 6.8), facecolor='white')
ax2 = plt.gca()
ax2.set_facecolor('#fcfcfc')

rates = np.zeros((6, 3))
for fi, f in enumerate(range(5, 11)):
    for Ii, I in enumerate([1, 2, 3]):
        rates[fi, Ii] = (0.03 * I + 0.01 * (f - 5)) * 100

im = ax2.imshow(rates, cmap='RdYlGn', aspect='auto', vmin=0, vmax=15)
cbar = plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
cbar.set_label('每月积分下降率（%）', fontsize=10)

for fi in range(6):
    for Ii in range(3):
        ax2.text(Ii, fi, f'{rates[fi, Ii]:.1f}%',
                 ha='center', va='center', fontsize=11,
                 fontweight='bold',
                 color='white' if rates[fi, Ii] > 9 else '#222222')

ax2.set_xticks([0, 1, 2])
ax2.set_xticklabels(['1级强度\n（低强度）', '2级强度\n（中强度）', '3级强度\n（高强度）'], fontsize=11)
ax2.set_yticks(range(6))
ax2.set_yticklabels([f'{f}次/周' for f in range(5, 11)], fontsize=11)
ax2.set_xlabel('活动干预强度', fontsize=12)
ax2.set_ylabel('每周训练频率', fontsize=12)
ax2.set_title('每月痰湿积分下降率热力图', fontsize=15, fontweight='bold', pad=12)

plt.tight_layout()
plt.show()

print("\n" + "=" * 65)
print("  第六步：论文数学符号说明（可直接引用）")
print("=" * 65)
print("""
  符号        类型        定义
  ─────────────────────────────────────────────────────────
  t           下标        月份序号，t = 1, 2, ..., 6
  S_t         状态变量    第t个月末的痰湿积分
  S_0         参数        患者初始痰湿积分
  I_t         决策变量    第t个月活动干预强度，I_t ∈ {1,2,3}
  f_t         决策变量    第t个月每周训练频率，f_t ∈ {1,...,10}
  R(I,f)      函数        月度积分下降率
  C_tcm(S)    函数        月度中医调理费用
  C_act(I)    函数        单次活动干预成本
  Cost_t      中间变量    第t个月总干预费用
  I_max       参数        允许的最大干预强度
  f_max       参数        允许的最大训练频率
  Budget      参数        6个月总费用上限（2000元）
""")

print("✅ 模块D完成：数学模型建立")
print("   下一步：模块E（最优方案求解）")
