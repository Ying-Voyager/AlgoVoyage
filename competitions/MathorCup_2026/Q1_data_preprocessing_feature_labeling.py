import pandas as pd
import numpy as np

# ============================================================
# 模块一：数据预处理
# 输入：data.xlsx（原始数据）
# 输出：data_preprocessed.xlsx（预处理后数据，供后续模块使用）
# 说明：
#   1. 生成血脂/代谢指标临床异常标签；
#   2. 生成痰湿质严重程度分组；
#   3. 依据附件3生成活动能力分组与“低活动能力”标签；
#   4. 生成体质标签文字映射列。
# ============================================================

# ---------- 读取数据 ----------
input_path = 'data.xlsx'
df = pd.read_excel(input_path)
original_col_num = df.shape[1]

print("=" * 55)
print("  第一步：原始数据基本情况")
print("=" * 55)
print(f"样本总数：{len(df)} 例")
print(f"特征维度：{df.shape[1]} 列")
print(f"高血脂确诊人数：{df['高血脂症二分类标签'].sum()} 例 "
      f"（占比 {df['高血脂症二分类标签'].mean() * 100:.1f}%）")
print(f"痰湿体质人数（体质标签=5）："
      f"{(df['体质标签'] == 5).sum()} 例 "
      f"（占比 {(df['体质标签'] == 5).mean() * 100:.1f}%）")

missing_info = df.isnull().sum()
missing_info = missing_info[missing_info > 0]
if len(missing_info) == 0:
    print("缺失值情况：无缺失值")
else:
    print(f"缺失值情况：\n{missing_info}")

# ============================================================
# 第二步：生成血脂/代谢指标异常标签（依据临床正常参考范围）
# 参考题目附表1中的临床正常范围
# 0 = 正常，1 = 异常
# ============================================================
print("\n" + "=" * 55)
print("  第二步：生成各指标临床异常标签（0=正常，1=异常）")
print("=" * 55)

# TC 总胆固醇：正常范围 3.1-6.2 mmol/L
df['TC_异常'] = df['TC（总胆固醇）'].apply(
    lambda x: 0 if 3.1 <= x <= 6.2 else 1
)

# TG 甘油三酯：正常范围 0.56-1.7 mmol/L
df['TG_异常'] = df['TG（甘油三酯）'].apply(
    lambda x: 0 if 0.56 <= x <= 1.7 else 1
)

# LDL-C 低密度脂蛋白：正常范围 2.07-3.1 mmol/L
df['LDL_异常'] = df['LDL-C（低密度脂蛋白）'].apply(
    lambda x: 0 if 2.07 <= x <= 3.1 else 1
)

# HDL-C 高密度脂蛋白：正常范围 1.04-1.55 mmol/L
df['HDL_异常'] = df['HDL-C（高密度脂蛋白）'].apply(
    lambda x: 0 if 1.04 <= x <= 1.55 else 1
)

# 空腹血糖：正常范围 3.9-6.1 mmol/L
df['血糖_异常'] = df['空腹血糖'].apply(
    lambda x: 0 if 3.9 <= x <= 6.1 else 1
)

# BMI：正常范围 18.5-23.9 kg/m²
df['BMI_异常'] = df['BMI'].apply(
    lambda x: 0 if 18.5 <= x <= 23.9 else 1
)

# 血尿酸：男女正常范围不同（性别：0=女，1=男）
def uric_acid_label(row):
    if row['性别'] == 1:  # 男：208-428 μmol/L
        return 0 if 208 <= row['血尿酸'] <= 428 else 1
    else:                 # 女：155-357 μmol/L
        return 0 if 155 <= row['血尿酸'] <= 357 else 1


df['尿酸_异常'] = df.apply(uric_acid_label, axis=1)

# 打印各指标异常率
abnormal_cols = [
    'TC_异常', 'TG_异常', 'LDL_异常', 'HDL_异常',
    '血糖_异常', 'BMI_异常', '尿酸_异常'
]
print("各指标异常人数及异常率：")
for col in abnormal_cols:
    n = int(df[col].sum())
    rate = df[col].mean() * 100
    print(f"  {col}：{n} 例（{rate:.1f}%）")

# ============================================================
# 第三步：生成痰湿质严重程度分组（按积分三分位数）
# 低度：积分 < 33.3% 分位数
# 中度：33.3% ≤ 积分 < 66.7% 分位数
# 高度：积分 ≥ 66.7% 分位数
# ============================================================
print("\n" + "=" * 55)
print("  第三步：生成痰湿质严重程度分组")
print("=" * 55)

q33 = df['痰湿质'].quantile(0.333)
q67 = df['痰湿质'].quantile(0.667)


def tanshi_group(score):
    if score < q33:
        return 0   # 低度
    elif score < q67:
        return 1   # 中度
    else:
        return 2   # 高度


df['痰湿质_严重程度'] = df['痰湿质'].apply(tanshi_group)
df['痰湿质_严重程度_文字'] = df['痰湿质_严重程度'].map({
    0: '低度(<' + f'{q33:.0f}分)',
    1: f'中度({q33:.0f}-{q67:.0f}分)',
    2: '高度(≥' + f'{q67:.0f}分)'
})

print(f"三分位阈值：低/中 分界={q33:.1f}分，中/高 分界={q67:.1f}分")
print("各组人数：")
for k, v in {0: '低度', 1: '中度', 2: '高度'}.items():
    n = (df['痰湿质_严重程度'] == k).sum()
    print(f"  {v}：{n} 例")

# ============================================================
# 第四步：生成活动能力分组（依据题目附件3评分约束）
# 低：活动量表总分 < 40
# 中：40 ≤ 活动量表总分 < 60
# 高：活动量表总分 ≥ 60
#
# 补充说明：
#   “活动能力_低”用于后续双维度筛选矩阵或风险分层。
#   这里不称为“活动异常”，而称为“低活动能力/行为功能不利状态”，
#   避免与血脂、血糖、BMI等临床异常指标混淆。
# ============================================================
print("\n" + "=" * 55)
print("  第四步：生成活动能力分组与低活动能力标签")
print("=" * 55)

act_col = '活动量表总分（ADL总分+IADL总分）'


def activity_group(score):
    if score < 40:
        return 0   # 低活动能力
    elif score < 60:
        return 1   # 中等活动能力
    else:
        return 2   # 高活动能力


df['活动能力_分组'] = df[act_col].apply(activity_group)
df['活动能力_分组_文字'] = df['活动能力_分组'].map({
    0: '低(<40分)',
    1: '中(40-59分)',
    2: '高(≥60分)'
})

# 新增：二分类标签，供代码4等后续模块使用
# 1 = 低活动能力，即行为功能不利状态；0 = 非低活动能力
df['活动能力_低'] = df[act_col].apply(lambda x: 1 if x < 40 else 0)
df['活动能力_低_文字'] = df['活动能力_低'].map({
    0: '非低活动能力(≥40分)',
    1: '低活动能力(<40分)'
})

print("活动能力三分类人数：")
for k, v in {0: '低(<40分)', 1: '中(40-59分)', 2: '高(≥60分)'}.items():
    n = (df['活动能力_分组'] == k).sum()
    print(f"  {v}：{n} 例")

low_n = int(df['活动能力_低'].sum())
low_rate = df['活动能力_低'].mean() * 100
print(f"低活动能力人数：{low_n} 例（{low_rate:.1f}%）")

# ============================================================
# 第五步：生成体质标签的文字映射列（方便画图）
# ============================================================
label_map = {
    1: '平和质', 2: '气虚质', 3: '阳虚质',
    4: '阴虚质', 5: '痰湿质', 6: '湿热质',
    7: '血瘀质', 8: '气郁质', 9: '特禀质'
}
df['体质标签_文字'] = df['体质标签'].map(label_map)

# ============================================================
# 第六步：打印核心描述性统计，确认数据无误
# ============================================================
print("\n" + "=" * 55)
print("  第六步：核心指标描述性统计")
print("=" * 55)

key_cols = [
    '痰湿质', act_col,
    'HDL-C（高密度脂蛋白）', 'LDL-C（低密度脂蛋白）',
    'TG（甘油三酯）', 'TC（总胆固醇）',
    '空腹血糖', '血尿酸', 'BMI'
]
stats = df[key_cols].describe().T[['min', 'mean', 'max', 'std']]
stats.columns = ['最小值', '均值', '最大值', '标准差']
print(stats.round(2).to_string())

# ============================================================
# 保存预处理结果
# ============================================================
output_path = 'data_preprocessed.xlsx'
df.to_excel(output_path, index=False)

new_cols = df.shape[1] - original_col_num
print(f"\n✅ 预处理完成，已保存至：{output_path}")
print(f"   原始列数：{original_col_num}  →  处理后列数：{df.shape[1]}")
print(f"   新增列：{new_cols} 列")
print("   其中包括：临床异常标签7列、痰湿严重程度分组2列、")
print("             活动能力分组2列、低活动能力标签2列、体质文字1列")

# ============================================================
# 第七步：可视化——数据预处理结果全览（每张图独立弹出）
# 图1：各指标临床异常率横向条形图
# 图2：痰湿质严重程度 × 活动能力交叉分布热力图
# 图3：九种体质人数分布（痰湿质高亮）
# 图4：各指标异常组的高血脂发病率对比
# ============================================================
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

abnormal_cols  = ['TC_异常', 'TG_异常', 'LDL_异常', 'HDL_异常',
                  '血糖_异常', 'BMI_异常', '尿酸_异常']
abnormal_names = ['TC（总胆固醇）', 'TG（甘油三酯）', 'LDL-C（低密度脂蛋白）',
                  'HDL-C（高密度脂蛋白）', '空腹血糖', 'BMI', '血尿酸']

rates = [df[c].mean() * 100 for c in abnormal_cols]
order = sorted(range(len(rates)), key=lambda i: rates[i])
names_sorted = [abnormal_names[i] for i in order]
rates_sorted = [rates[i] for i in order]

# ── 图1：各指标异常率横向条形图 ────────────────────────────
fig1, ax1 = plt.subplots(figsize=(10, 6))

colors_bar = ['#d73027' if r > 50 else '#f46d43' if r > 35 else '#74add1'
              for r in rates_sorted]
bars = ax1.barh(names_sorted, rates_sorted,
                color=colors_bar, edgecolor='white', height=0.65)
ax1.axvline(50, color='gray', linewidth=1.2, linestyle='--', alpha=0.6)
ax1.text(50.5, -0.7, '50%', fontsize=8.5, color='gray')
for bar, rate in zip(bars, rates_sorted):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
             f'{rate:.1f}%', va='center', ha='left', fontsize=10, fontweight='bold')
ax1.set_xlabel('异常率（%）', fontsize=11)
ax1.set_xlim(0, 82)
ax1.set_title('图1：各临床指标异常率\n（1000例样本，按异常率排序）',
              fontsize=12, fontweight='bold')
ax1.legend(handles=[
    mpatches.Patch(color='#d73027', label='>50%（高异常率）'),
    mpatches.Patch(color='#f46d43', label='35-50%（中异常率）'),
    mpatches.Patch(color='#74add1', label='<35%（低异常率）'),
], fontsize=9, loc='lower right')
plt.tight_layout()
plt.show()

# ── 图2：痰湿质严重程度 × 活动能力交叉热力图 ──────────────
fig2, ax2 = plt.subplots(figsize=(8, 6))

tanshi_order = ['低度(<21分)', '中度(21-42分)', '高度(≥42分)']
act_order    = ['低(<40分)', '中(40-59分)', '高(≥60分)']
cross_matrix = np.zeros((3, 3))
for ri, ts in enumerate(tanshi_order):
    for ci, ac in enumerate(act_order):
        cross_matrix[ri, ci] = ((df['痰湿质_严重程度_文字'] == ts) &
                                 (df['活动能力_分组_文字'] == ac)).sum()
im = ax2.imshow(cross_matrix, cmap='YlOrRd', aspect='auto')
plt.colorbar(im, ax=ax2, label='人数')
for ri in range(3):
    for ci in range(3):
        n   = int(cross_matrix[ri, ci])
        pct = n / len(df) * 100
        ax2.text(ci, ri, f'{n}例\n({pct:.1f}%)',
                 ha='center', va='center', fontsize=10, fontweight='bold',
                 color='white' if n > 180 else 'black')
ax2.set_xticks([0, 1, 2])
ax2.set_xticklabels(act_order, fontsize=10)
ax2.set_yticks([0, 1, 2])
ax2.set_yticklabels(tanshi_order, fontsize=10)
ax2.set_xlabel('活动能力分组', fontsize=11)
ax2.set_ylabel('痰湿质严重程度', fontsize=11)
ax2.set_title('图2：痰湿质严重程度 × 活动能力\n交叉分布热力图（人数）',
              fontsize=12, fontweight='bold')
plt.tight_layout()
plt.show()

# ── 图3：九种体质人数分布 ──────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(11, 6))

constitution_order = ['平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质',
                      '湿热质', '血瘀质', '气郁质', '特禀质']
counts   = [df[df['体质标签_文字'] == c].shape[0] for c in constitution_order]
colors_c = ['#d73027' if c == '痰湿质' else '#4393c3' for c in constitution_order]
bars3 = ax3.bar(constitution_order, counts,
                color=colors_c, edgecolor='white', width=0.7)
for bar, cnt in zip(bars3, counts):
    pct = cnt / len(df) * 100
    ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             f'{cnt}\n({pct:.1f}%)',
             ha='center', va='bottom', fontsize=9, fontweight='bold')
ax3.set_ylabel('人数（例）', fontsize=11)
ax3.set_ylim(0, max(counts) * 1.22)
ax3.set_title('图3：九种体质人数分布\n（痰湿质人数最多，占比最高）',
              fontsize=12, fontweight='bold')
ax3.tick_params(axis='x', labelsize=10)
ax3.legend(handles=[
    mpatches.Patch(color='#d73027', label='痰湿质（重点研究对象）'),
    mpatches.Patch(color='#4393c3', label='其他体质'),
], fontsize=9)
plt.tight_layout()
plt.show()

# ── 图4：各指标异常组的高血脂发病率对比 ────────────────────
fig4, ax4 = plt.subplots(figsize=(10, 6))

overall_rate    = df['高血脂症二分类标签'].mean() * 100
ab_rates        = [df[df[c] == 1]['高血脂症二分类标签'].mean() * 100
                   for c in abnormal_cols]
ab_rates_sorted = [ab_rates[i] for i in order]
colors_rate = ['#d73027' if r > 90 else '#f46d43' if r > 80 else '#74add1'
               for r in ab_rates_sorted]
bars4 = ax4.barh(names_sorted, ab_rates_sorted,
                 color=colors_rate, edgecolor='white', height=0.65)
ax4.axvline(overall_rate, color='black', linewidth=1.5, linestyle='--', alpha=0.7,
            label=f'总体发病率 {overall_rate:.1f}%')
for bar, rate in zip(bars4, ab_rates_sorted):
    ax4.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
             f'{rate:.1f}%', va='center', ha='left', fontsize=10, fontweight='bold')
ax4.set_xlabel('高血脂发病率（%）', fontsize=11)
ax4.set_xlim(0, 115)
ax4.set_title('图4：各指标异常人群的高血脂发病率\n（异常组 vs 总体基准线）',
              fontsize=12, fontweight='bold')
ax4.legend(fontsize=9)
plt.tight_layout()
plt.show()

print("\n✅ 可视化完成，4张图已依次弹出。")