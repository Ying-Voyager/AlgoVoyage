import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_excel('data_preprocessed.xlsx')

# 分析的指标列表
indicator_cols = [
    'TG（甘油三酯）', 'TC（总胆固醇）',
    'LDL-C（低密度脂蛋白）', 'HDL-C（高密度脂蛋白）',
    '血尿酸', '空腹血糖', 'BMI'
]
abnormal_cols = ['TG_异常', 'TC_异常', 'LDL_异常', 'HDL_异常', '尿酸_异常', '血糖_异常', 'BMI_异常']

# 显示用的短名称（对应上面两个列表的顺序）
short_names = ['TG', 'TC', 'LDL-C', 'HDL-C', '血尿酸', '空腹血糖', 'BMI']

y = df['高血脂症二分类标签']

# ============================================================
# 第一步：Spearman 相关系数 + 显著性检验
# ============================================================
print("=" * 55)
print("  第一步：各指标与高血脂的 Spearman 相关性")
print("=" * 55)

spearman_results = []
for col, name in zip(indicator_cols, short_names):
    r, p = stats.spearmanr(df[col], y)
    sig = 'p<0.001' if p < 0.001 else ('p<0.01' if p < 0.01 else ('p<0.05' if p < 0.05 else 'ns'))
    spearman_results.append({'指标': name, '相关系数r': r, 'p值': p, '显著性': sig})
    print(f"  {name:8s}  r={r:+.4f}  p={p:.4f}  {sig}")

spearman_df = pd.DataFrame(spearman_results)

# ============================================================
# 第二步：卡方检验 —— 异常 vs 正常人群的高血脂发病率对比
# ============================================================
print("\n" + "=" * 55)
print("  第二步：各指标异常 vs 正常人群高血脂发病率（卡方检验）")
print("=" * 55)

chi2_results = []
for ab_col, name in zip(abnormal_cols, short_names):
    # 构建2x2列联表
    ct = pd.crosstab(df[ab_col], y)
    chi2, p, dof, _ = stats.chi2_contingency(ct)

    # 计算两组发病率
    rate_normal  = df[y == 1][ab_col].eq(0).sum() / df[ab_col].eq(0).sum() \
                   if df[ab_col].eq(0).sum() > 0 else 0
    rate_abnormal = df[(df[ab_col] == 1)]['高血脂症二分类标签'].mean()
    rate_normal   = df[(df[ab_col] == 0)]['高血脂症二分类标签'].mean()

    sig = 'p<0.001' if p < 0.001 else ('p<0.01' if p < 0.01 else ('p<0.05' if p < 0.05 else 'ns'))
    chi2_results.append({
        '指标': name,
        '正常组发病率': rate_normal,
        '异常组发病率': rate_abnormal,
        '发病率差值': rate_abnormal - rate_normal,
        'chi2': chi2, 'p值': p, '显著性': sig
    })
    print(f"  {name:8s}  正常组={rate_normal:.3f}  异常组={rate_abnormal:.3f}  "
          f"差值={rate_abnormal-rate_normal:+.3f}  chi2={chi2:.2f}  {sig}")

chi2_df = pd.DataFrame(chi2_results)

# ============================================================
# 第三步：画图（每张图独立弹出）
# 图1：Spearman 相关系数条形图（含显著性标注）
# 图2：异常 vs 正常的高血脂发病率分组柱状图
# ============================================================

# ---------- 图1：Spearman 相关系数 ----------
fig1, ax1 = plt.subplots(figsize=(10, 6))

colors = ['#d73027' if r > 0 else '#4575b4'
          for r in spearman_df['相关系数r']]
bars = ax1.barh(spearman_df['指标'], spearman_df['相关系数r'],
                color=colors, edgecolor='white', height=0.6)

# 在条形末端标注数值和显著性
# 注意：显著性用文字形式（p<0.001 等），避免*被 matplotlib 解析为数学符号
for bar, (_, row) in zip(bars, spearman_df.iterrows()):
    w = bar.get_width()
    offset = 0.01 if w >= 0 else -0.01
    ha = 'left' if w >= 0 else 'right'
    ax1.text(w + offset, bar.get_y() + bar.get_height() / 2,
             f"r={w:+.3f}  {row['显著性']}",
             va='center', ha=ha, fontsize=10)

ax1.axvline(0, color='black', linewidth=0.8)
ax1.axvline(0.2,  color='gray', linewidth=0.8, linestyle='--', alpha=0.5)
ax1.axvline(-0.2, color='gray', linewidth=0.8, linestyle='--', alpha=0.5)
ax1.set_xlabel('Spearman 相关系数 r', fontsize=12)
ax1.set_title('图1：各指标与高血脂的 Spearman 相关系数', fontsize=13, fontweight='bold')
ax1.set_xlim(-0.65, 0.85)

red_patch  = mpatches.Patch(color='#d73027', label='正相关（值越高风险越大）')
blue_patch = mpatches.Patch(color='#4575b4', label='负相关（值越高风险越小）')
ax1.legend(handles=[red_patch, blue_patch], fontsize=9, loc='lower right')
plt.tight_layout()
plt.show()

# ---------- 图2：发病率对比柱状图 ----------
fig2, ax2 = plt.subplots(figsize=(10, 6))

x = np.arange(len(short_names))
width = 0.35

bars_normal   = ax2.bar(x - width/2, chi2_df['正常组发病率'] * 100,
                         width, label='指标正常组', color='#74add1', edgecolor='white')
bars_abnormal = ax2.bar(x + width/2, chi2_df['异常组发病率'] * 100,
                         width, label='指标异常组', color='#f46d43', edgecolor='white')

for bar in bars_normal:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, h + 0.5,
             f'{h:.1f}%', ha='center', va='bottom', fontsize=9)
for bar in bars_abnormal:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, h + 0.5,
             f'{h:.1f}%', ha='center', va='bottom', fontsize=9)

# 显著性标注：文字形式，颜色区分
for i, (_, row) in enumerate(chi2_df.iterrows()):
    y_top = max(row['正常组发病率'], row['异常组发病率']) * 100 + 3.5
    sig   = row['显著性']
    color = 'red' if sig != 'ns' else 'gray'
    ax2.text(i, y_top, sig, ha='center', va='bottom', fontsize=9,
             color=color, fontweight='bold')

ax2.set_xticks(x)
ax2.set_xticklabels(short_names, fontsize=11)
ax2.set_ylabel('高血脂发病率（%）', fontsize=12)
ax2.set_title('图2：各指标正常 vs 异常人群的高血脂发病率对比', fontsize=13, fontweight='bold')
ax2.set_ylim(0, 120)
ax2.axhline(df['高血脂症二分类标签'].mean() * 100,
            color='black', linestyle='--', linewidth=1, alpha=0.6,
            label=f'总体发病率 {df["高血脂症二分类标签"].mean()*100:.1f}%')
ax2.legend(fontsize=10)
plt.tight_layout()
plt.show()

# ============================================================
# 第四步：打印结论汇总
# ============================================================
print("\n" + "=" * 55)
print("  结论汇总：能有效预警高血脂的关键指标")
print("=" * 55)

sig_spearman = spearman_df[spearman_df['显著性'] != 'ns']['指标'].tolist()
sig_chi2     = chi2_df[chi2_df['显著性'] != 'ns']['指标'].tolist()
both_sig     = [x for x in sig_spearman if x in sig_chi2]

print(f"  Spearman 显著指标（p<0.05）：{sig_spearman}")
print(f"  卡方检验显著指标（p<0.05）：{sig_chi2}")
print(f"  两项检验均显著的指标：{both_sig}")
print()
print("  各指标预警能力排序（按|r|降序）：")
spearman_df['abs_r'] = spearman_df['相关系数r'].abs()
for _, row in spearman_df.sort_values('abs_r', ascending=False).iterrows():
    direction = '↑风险' if row['相关系数r'] > 0 else '↓风险(保护)'
    print(f"    {row['指标']:8s}  |r|={row['abs_r']:.4f}  {direction}  {row['显著性']}")