import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120

df = pd.read_excel('data_preprocessed.xlsx')

act_col = '活动量表总分（ADL总分+IADL总分）'
if '活动能力_低' not in df.columns:
    df['活动能力_低'] = (df[act_col] < 40).astype(int)

indicator_cols = [
    'TG（甘油三酯）', 'TC（总胆固醇）', 'LDL-C（低密度脂蛋白）',
    'HDL-C（高密度脂蛋白）', '血尿酸', '空腹血糖', 'BMI', act_col
]
adverse_cols = [
    'TG_异常', 'TC_异常', 'LDL_异常', 'HDL_异常',
    '尿酸_异常', '血糖_异常', 'BMI_异常', '活动能力_低'
]
short_names = ['TG', 'TC', 'LDL-C', 'HDL-C', '血尿酸', '空腹血糖', 'BMI', '活动量表']

required_cols = indicator_cols + adverse_cols + ['体质标签', '高血脂症二分类标签']
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    raise ValueError(f'数据中缺少以下列，请先运行修改后的代码1进行预处理：{missing_cols}')

tanshi = df[df['体质标签'] == 5]
other = df[df['体质标签'] != 5]
y = df['高血脂症二分类标签']

print('=' * 70)
print('  双维度筛选矩阵 —— 各指标坐标计算')
print('=' * 70)
print(f"  {'指标':<8} {'X: |r|与高血脂':<18} {'p值':<10} {'Y: 痰湿不利状态比例':<20} {'指标类型':<10} {'证据等级'}")
print('  ' + '-' * 85)

literature_level = {
    'TG': ('核心', '#c73e3a', '生理代谢核心指标'),
    'TC': ('核心', '#c73e3a', '生理代谢核心指标'),
    'BMI': ('核心', '#c73e3a', '生理代谢核心指标'),
    'LDL-C': ('重要', '#ee7b30', '血脂分型重要指标'),
    'HDL-C': ('重要', '#ee7b30', '血脂分型重要指标'),
    '活动量表': ('辅助', '#2a9d8f', '行为功能辅助指标'),
    '血尿酸': ('参考', '#5b8fd1', '代谢参考指标'),
    '空腹血糖': ('参考', '#5b8fd1', '代谢参考指标'),
}

def p_label(p):
    if p < 0.001:
        return 'p<0.001'
    elif p < 0.01:
        return 'p<0.01'
    elif p < 0.05:
        return 'p<0.05'
    else:
        return ''

matrix_data = []
for col, adv_col, name in zip(indicator_cols, adverse_cols, short_names):
    r, p = stats.spearmanr(df[col], y)
    abs_r = abs(r)
    tanshi_adverse_rate = tanshi[adv_col].mean()
    other_adverse_rate = other[adv_col].mean()
    diff = tanshi_adverse_rate - other_adverse_rate
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
    p_text = p_label(p)
    level, color, indicator_type = literature_level[name]

    matrix_data.append({
        '指标': name,
        '连续变量列': col,
        '不利状态列': adv_col,
        'X_abs_r': abs_r,
        'r_raw': r,
        'p值': p,
        '显著性': sig,
        'p标注': p_text,
        'Y_tanshi_adverse': tanshi_adverse_rate,
        '其他体质不利状态比例': other_adverse_rate,
        '不利状态率差值': diff,
        '文献等级': level,
        '指标类型': indicator_type,
        '颜色': color,
    })

    print(f"  {name:<8} {abs_r:<18.4f} {p:<10.4f} {tanshi_adverse_rate:<20.3f} {indicator_type:<12} {level}")

matrix_df = pd.DataFrame(matrix_data)

x_threshold = 0.15
y_threshold = 0.35

matrix_df['是否双重关键'] = (
    (matrix_df['X_abs_r'] >= x_threshold) &
    (matrix_df['p值'] < 0.05) &
    (matrix_df['Y_tanshi_adverse'] >= y_threshold)
)
matrix_df['最终定位'] = np.where(
    matrix_df['是否双重关键'],
    '双重关键指标',
    np.where(matrix_df['指标'] == '活动量表', '行为功能辅助指标', '候选/参考指标')
)

print('\n' + '=' * 70)
print(f'  筛选阈值：|r| ≥ {x_threshold}（且p<0.05）& 痰湿不利状态比例 ≥ {y_threshold*100:.0f}%')
print('=' * 70)
key_indicators = matrix_df[matrix_df['是否双重关键']]['指标'].tolist()
aux_indicators = matrix_df[matrix_df['最终定位'] == '行为功能辅助指标']['指标'].tolist()
non_key = matrix_df[~matrix_df['是否双重关键']]['指标'].tolist()
print(f'  ✅ 双重关键指标：{key_indicators}')
print(f'  🟩 行为功能辅助指标：{aux_indicators}')
print(f'  ❌ 未进入双重关键区指标：{non_key}')

score_df = matrix_df.copy()
score_df['X_norm'] = score_df['X_abs_r'] / matrix_df['X_abs_r'].max()
score_df['Y_norm'] = score_df['Y_tanshi_adverse'] / matrix_df['Y_tanshi_adverse'].max()
score_df['证据分'] = score_df['文献等级'].map({'核心': 1.00, '重要': 0.67, '辅助': 0.50, '参考': 0.33})
score_df['综合得分'] = score_df['X_norm'] * 0.5 + score_df['Y_norm'] * 0.3 + score_df['证据分'] * 0.2
score_df = score_df.sort_values('综合得分', ascending=True)

x_max = max(0.62, matrix_df['X_abs_r'].max() + 0.08)
y_max = max(0.75, matrix_df['Y_tanshi_adverse'].max() + 0.08)
y_min = max(0.08, matrix_df['Y_tanshi_adverse'].min() - 0.08)

label_offset = {
    'TG': (0.010, 0.015),
    'TC': (0.010, -0.028),
    'LDL-C': (-0.004, 0.020),
    'HDL-C': (0.010, 0.018),
    '血尿酸': (0.010, 0.016),
    '空腹血糖': (-0.004, -0.028),
    'BMI': (0.010, 0.016),
    '活动量表': (0.012, -0.032),
}

# 图1：双维度矩阵
plt.figure(figsize=(9.2, 7.2), facecolor='white')
ax = plt.gca()
ax.set_facecolor('#fcfcfc')

ax.axvspan(x_threshold, x_max, ymin=(y_threshold - y_min) / (y_max - y_min), ymax=1, color='#f7e7a9', alpha=0.32, zorder=0)
ax.axvspan(0, x_threshold, ymin=(y_threshold - y_min) / (y_max - y_min), ymax=1, color='#eaf4fb', alpha=0.65, zorder=0)
ax.axvspan(x_threshold, x_max, ymin=0, ymax=(y_threshold - y_min) / (y_max - y_min), color='#fdebe4', alpha=0.52, zorder=0)
ax.axvspan(0, x_threshold, ymin=0, ymax=(y_threshold - y_min) / (y_max - y_min), color='#f4f4f4', alpha=0.85, zorder=0)

ax.axvline(x_threshold, color='#7a7a7a', linewidth=1.2, linestyle=(0, (4, 3)), zorder=1)
ax.axhline(y_threshold, color='#7a7a7a', linewidth=1.2, linestyle=(0, (4, 3)), zorder=1)

for _, row in matrix_df.iterrows():
    size = 380 + abs(row['不利状态率差值']) * 3300
    edge_color = '#111111' if row['是否双重关键'] else ('#0d5c52' if row['指标'] == '活动量表' else 'white')
    line_width = 2.3 if row['是否双重关键'] else (1.8 if row['指标'] == '活动量表' else 0.9)

    ax.scatter(
        row['X_abs_r'], row['Y_tanshi_adverse'],
        s=size, color=row['颜色'], edgecolors=edge_color,
        linewidths=line_width, alpha=0.9, zorder=3
    )

    if row['p标注'] != '':
        ax.text(
            row['X_abs_r'] + 0.007, row['Y_tanshi_adverse'] + 0.007,
            row['p标注'], fontsize=8, color='#333333', zorder=4
        )

    ox, oy = label_offset.get(row['指标'], (0.01, 0.015))
    ax.text(
        row['X_abs_r'] + ox, row['Y_tanshi_adverse'] + oy,
        row['指标'], fontsize=11,
        fontweight='bold' if row['是否双重关键'] or row['指标'] == '活动量表' else 'normal',
        color='#1f1f1f', zorder=5
    )

ax.text((x_threshold + x_max) / 2, y_max - 0.02, '双重关键区\n（预警高血脂 + 表征痰湿）',
        fontsize=10, color='#7b5b00', ha='center', va='top', fontweight='bold')

ax.set_xlabel('预警高血脂能力（Spearman |r|）', fontsize=12)
ax.set_ylabel('表征痰湿体质能力\n（痰湿体质人群不利状态比例）', fontsize=12)
ax.set_title('双维度关键指标筛选矩阵', fontsize=14, fontweight='bold', pad=12)
ax.set_xlim(0, x_max)
ax.set_ylim(y_min, y_max)
ax.grid(axis='both', linestyle=':', linewidth=0.6, alpha=0.25)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.text(x_threshold + 0.004, y_min + 0.015, f'|r|={x_threshold}', fontsize=9, color='#666666')
ax.text(0.005, y_threshold + 0.006, f'不利状态比例={y_threshold*100:.0f}%', fontsize=9, color='#666666')

legend_elements = [
    mpatches.Patch(color='#c73e3a', label='核心指标'),
    mpatches.Patch(color='#ee7b30', label='重要指标'),
    mpatches.Patch(color='#2a9d8f', label='辅助指标'),
    mpatches.Patch(color='#5b8fd1', label='参考指标'),
]
ax.legend(handles=legend_elements, fontsize=9, loc='lower right',
          title='证据等级', title_fontsize=9, frameon=True,
          facecolor='white', edgecolor='#dddddd')

ax.text(0.5, -0.16,
        '注：血脂、血糖、尿酸、BMI依据临床参考范围定义不利状态；活动量表以总分<40定义低活动能力。',
        transform=ax.transAxes, ha='center', va='top', fontsize=8.5, color='#666666')

plt.tight_layout()
plt.show()

# 图2：综合评分排名
plt.figure(figsize=(8.6, 6.8), facecolor='white')
ax2 = plt.gca()
ax2.set_facecolor('#fcfcfc')

colors_bar = [literature_level[n][1] for n in score_df['指标']]
bars = ax2.barh(score_df['指标'], score_df['综合得分'],
                color=colors_bar, edgecolor='white', height=0.62)

for bar, (_, row) in zip(bars, score_df.iterrows()):
    w = bar.get_width()
    label = f"{w:.3f}  {row['文献等级']}"
    ax2.text(w + 0.008, bar.get_y() + bar.get_height() / 2,
             label, va='center', ha='left', fontsize=10, color='#222222')

ax2.axvline(0.5, color='#8a8a8a', linewidth=1.0, linestyle=(0, (4, 3)), alpha=0.8)
ax2.set_xlabel('综合评分（预警能力×50% + 痰湿表征×30% + 证据支撑×20%）', fontsize=11)
ax2.set_title('候选指标综合评分排名', fontsize=14, fontweight='bold', pad=12)
ax2.set_xlim(0, max(1.05, score_df['综合得分'].max() + 0.16))
ax2.grid(axis='x', linestyle=':', linewidth=0.6, alpha=0.25)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

for tick in ax2.get_yticklabels():
    if tick.get_text() in key_indicators or tick.get_text() == '活动量表':
        tick.set_fontweight('bold')

plt.tight_layout()
plt.show()

print('\n' + '=' * 70)
print('  模块四结论：双维度关键指标最终筛选结果')
print('=' * 70)

score_df_sorted = score_df.sort_values('综合得分', ascending=False)
key_df_sorted = score_df_sorted[score_df_sorted['是否双重关键']].copy()

mechanism_text = {
    'TG': 'TG升高是痰湿内蕴和脂代谢失常的重要体现，同时是高血脂风险识别的核心指标。',
    'TC': 'TC异常反映胆固醇代谢紊乱，与高血脂诊断和痰湿膏脂内停机制均具有较强关联。',
    'LDL-C': 'LDL-C升高参与动脉粥样硬化和血脂异常分型，是高血脂风险判断的重要指标。',
    'HDL-C': 'HDL-C降低提示保护性脂蛋白不足，可作为脂代谢紊乱的负向标志。',
    'BMI': 'BMI反映形体偏胖和代谢负担，是痰湿体质客观表征的重要指标。',
    '血尿酸': '血尿酸升高与代谢综合征相关，可作为高血脂伴随代谢风险的参考指标。',
    '空腹血糖': '空腹血糖反映糖代谢状态，可作为血脂异常相关代谢风险的参考指标。',
    '活动量表': '活动量表总分反映中老年人日常活动能力，低分状态可作为行为功能不利状态，并为后续干预强度约束提供依据。',
}

for _, row in score_df_sorted.iterrows():
    direction = '正向（值越高风险越大）' if row['r_raw'] > 0 else '负向（值越低风险越大）'
    tag = '双重关键' if row['是否双重关键'] else ('行为辅助' if row['指标'] == '活动量表' else '候选参考')
    print(f'''
  【{row['指标']}】综合评分 {row['综合得分']:.3f} — {row['文献等级']}指标，定位：{tag}
    · 预警高血脂：Spearman r={row['r_raw']:+.4f}（{row['显著性']}），{direction}
    · 表征痰湿质：痰湿体质人群不利状态比例 {row['Y_tanshi_adverse']*100:.1f}%
    · 指标类型：{row['指标类型']}
    · 机制说明：{mechanism_text[row['指标']]}
''')

print(f'''
  ═══════════════════════════════════════════════════
  最终结论：
  双重关键指标：{' > '.join(key_df_sorted['指标'].tolist()) if len(key_df_sorted) > 0 else '无'}
  行为功能辅助指标：活动量表总分

  解释：
  TG、TC、BMI、LDL-C、HDL-C等指标主要反映生理代谢风险，
  可用于高血脂风险预警和痰湿体质客观表征；
  活动量表总分不属于临床生化异常指标，但其低分状态反映活动能力不足，
  可作为行为功能维度的辅助指标，并为后续风险分层和干预方案优化提供依据。
  ═══════════════════════════════════════════════════
''')