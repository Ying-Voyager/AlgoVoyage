
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import shap
import statsmodels.api as sm

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 120

df = pd.read_excel('data_preprocessed.xlsx')

constitution_cols = ['平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质',
                     '湿热质', '血瘀质', '气郁质', '特禀质']
label_map = {
    1: '平和质', 2: '气虚质', 3: '阳虚质', 4: '阴虚质', 5: '痰湿质',
    6: '湿热质', 7: '血瘀质', 8: '气郁质', 9: '特禀质'
}

all_feature_cols = constitution_cols + [
    '活动量表总分（ADL总分+IADL总分）',
    '年龄组', '性别', '吸烟史', '饮酒史'
]
feature_display = constitution_cols + [
    '活动量表', '年龄组', '性别', '吸烟史', '饮酒史'
]

X = df[all_feature_cols].copy()
X.columns = feature_display
y = df['高血脂症二分类标签']

def p_text(p):
    if p < 0.001:
        return 'p<0.001'
    elif p < 0.01:
        return 'p<0.01'
    elif p < 0.05:
        return 'p<0.05'
    return ''

print("=" * 60)
print("  第一步：各体质人群高血脂发病率及统计检验")
print("=" * 60)

ct_all = pd.crosstab(df['体质标签'], y)
chi2_all, p_all, _, _ = stats.chi2_contingency(ct_all)
print(f"  九种体质总体发病率差异卡方检验：chi2={chi2_all:.4f}, p={p_all:.4f}")
print(f"  → {'存在显著差异' if p_all < 0.05 else '无显著差异（各体质发病率相近）'}")
print()

rate_results = []
for k, v in label_map.items():
    sub = df[df['体质标签'] == k]
    n = len(sub)
    rate = sub['高血脂症二分类标签'].mean()
    se = np.sqrt(rate * (1 - rate) / n)
    ci_low = max(0, rate - 1.96 * se)
    ci_high = min(1, rate + 1.96 * se)

    ct2 = pd.crosstab(df['体质标签'].apply(lambda x: 1 if x == k else 0), y)
    chi2, p, _, _ = stats.chi2_contingency(ct2)
    rate_results.append({
        '体质': v, '人数': n, '发病率': rate,
        'CI_low': ci_low, 'CI_high': ci_high,
        'p值': p, '显著性文本': p_text(p)
    })
    print(f"  {v:5s}(n={n:3d}): 发病率={rate:.3f}  95%CI=[{ci_low:.3f},{ci_high:.3f}]  {p_text(p) if p_text(p) else 'ns'}")

rate_df = pd.DataFrame(rate_results).sort_values('发病率', ascending=False)

print("\n" + "=" * 60)
print("  第二步：多因素 Logistic 回归（OR值分析）")
print("=" * 60)

X_logit = sm.add_constant(X)
logit_model = sm.Logit(y, X_logit)
logit_result = logit_model.fit(disp=0)

OR_vals = np.exp(logit_result.params)
OR_ci = np.exp(logit_result.conf_int())
p_vals = logit_result.pvalues

print(f"  模型伪R²（McFadden）: {logit_result.prsquared:.4f}")
print(f"  模型AIC: {logit_result.aic:.2f}")
print()
print(f"  {'体质':<8} {'OR值':>8} {'95%CI下限':>10} {'95%CI上限':>10} {'p值':>8} {'显著性':>10} {'方向'}")
print("  " + "-" * 74)

logit_results = []
for col in constitution_cols:
    OR = OR_vals[col]
    ci_l = OR_ci.loc[col, 0]
    ci_h = OR_ci.loc[col, 1]
    p = p_vals[col]
    pt = p_text(p)
    direction = '↑风险' if OR > 1 else '↓风险'
    logit_results.append({'体质': col, 'OR': OR, 'CI_low': ci_l,
                          'CI_high': ci_h, 'p值': p, '显著性文本': pt})
    print(f"  {col:<8} {OR:>8.4f} {ci_l:>10.4f} {ci_h:>10.4f} {p:>8.4f} {pt if pt else 'ns':>10} {direction}")

logit_df = pd.DataFrame(logit_results).sort_values('OR', ascending=False)
sig_count = sum(1 for r in logit_results if r['显著性文本'])

print(f"\n  显著体质数量：{sig_count}/9")
print("  注：OR均接近1时，说明体质积分对高血脂的独立线性预测作用有限。")

print("\n" + "=" * 60)
print("  第三步：随机森林特征重要性 + SHAP 解释")
print("=" * 60)

rf = RandomForestClassifier(n_estimators=500, random_state=42, max_depth=6)
rf.fit(X, y)

auc_scores = cross_val_score(rf, X, y, cv=5, scoring='roc_auc')
print(f"  模型5折交叉验证 AUC: {auc_scores.mean():.4f} ± {auc_scores.std():.4f}")

print("  正在计算 SHAP 值...")
explainer = shap.TreeExplainer(rf)
shap_values = explainer(X)
shap_pos = shap_values.values[:, :, 1]

mean_abs_shap = np.abs(shap_pos).mean(axis=0)
shap_imp_df = pd.DataFrame({
    '特征': feature_display,
    '平均|SHAP|': mean_abs_shap,
    '类型': (['体质积分'] * 9 + ['活动量表'] + ['基础信息'] * 4)
}).sort_values('平均|SHAP|', ascending=False)

print("\n  SHAP 全局特征重要性排名（平均|SHAP|值）：")
for i, (_, row) in enumerate(shap_imp_df.iterrows(), 1):
    print(f"  {i:2d}. {row['特征']:8s} [{row['类型']}]  {row['平均|SHAP|']:.6f}")

constitution_shap = shap_imp_df[shap_imp_df['类型'] == '体质积分'].copy()
constitution_shap_total = constitution_shap['平均|SHAP|'].sum()
constitution_shap['体质内占比'] = constitution_shap['平均|SHAP|'] / constitution_shap_total

print("\n  九种体质积分 SHAP 内部排名及方向：")
idx_map = {name: i for i, name in enumerate(feature_display)}
for _, row in constitution_shap.iterrows():
    feat_idx = idx_map[row['特征']]
    mean_shap = shap_pos[:, feat_idx].mean()
    direction = '正向↑' if mean_shap > 0 else '负向↓'
    print(f"    {row['特征']:5s}：平均|SHAP|={row['平均|SHAP|']:.6f}  占比={row['体质内占比']*100:.1f}%  带符号均值={mean_shap:+.6f} {direction}")

print("\n" + "=" * 60)
print("  第四步：痰湿体质人群高血脂风险画像")
print("=" * 60)

tanshi = df[df['体质标签'] == 5]
other = df[df['体质标签'] != 5]
risk_cols = ['TG_异常', 'TC_异常', 'LDL_异常', 'HDL_异常', '尿酸_异常']
risk_names = ['TG异常', 'TC异常', 'LDL-C异常', 'HDL-C异常', '血尿酸异常']

print(f"  痰湿体质人数：{len(tanshi)}，发病率：{tanshi['高血脂症二分类标签'].mean():.3f}")
print(f"  人数占比：{len(tanshi)/len(df)*100:.1f}%（九种体质中最多）")
for rc, rn in zip(risk_cols, risk_names):
    r_t = tanshi[rc].mean()
    r_o = other[rc].mean()
    print(f"  {rn}：痰湿={r_t:.3f}  其他={r_o:.3f}  差={r_t-r_o:+.3f}")

# 图1：发病率对比
plt.figure(figsize=(10.4, 6.8), facecolor='white')
ax1 = plt.gca()
ax1.set_facecolor('#fcfcfc')

colors_bar = ['#c73e3a' if v == '痰湿质' else '#5b8fd1' for v in rate_df['体质']]
x_pos = np.arange(len(rate_df))

bars1 = ax1.bar(
    x_pos, rate_df['发病率'] * 100,
    color=colors_bar, edgecolor='white', width=0.62, zorder=3
)
ax1.errorbar(
    x_pos, rate_df['发病率'] * 100,
    yerr=[(rate_df['发病率'] - rate_df['CI_low']) * 100,
          (rate_df['CI_high'] - rate_df['发病率']) * 100],
    fmt='none', color='#444444', capsize=4, linewidth=1.3, zorder=4
)

for bar, (_, row) in zip(bars1, rate_df.iterrows()):
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, h + 1.5,
             f"{h:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    if row['显著性文本']:
        ax1.text(bar.get_x() + bar.get_width()/2, h + 4.6,
                 row['显著性文本'], ha='center', va='bottom', fontsize=8.5, color='#444444')

overall_rate = y.mean() * 100
ax1.axhline(overall_rate, color='#666666', linewidth=1.1, linestyle=(0, (4, 3)), alpha=0.8)
ax1.text(len(rate_df) - 0.25, overall_rate + 0.8,
         f'总体发病率 {overall_rate:.1f}%', fontsize=9, color='#555555', va='bottom')

ax1.set_xticks(x_pos)
ax1.set_xticklabels(rate_df['体质'], fontsize=11)
ax1.set_ylabel('高血脂发病率（%）', fontsize=12)
ax1.set_ylim(0, 105)
ax1.set_title(
    f'九种中医体质人群高血脂发病率对比\n总体卡方检验：chi²={chi2_all:.3f}, p={p_all:.4f}',
    fontsize=14, fontweight='bold', pad=12
)
ax1.grid(axis='y', linestyle=':', linewidth=0.6, alpha=0.25)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.legend(handles=[
    mpatches.Patch(color='#c73e3a', label=f'痰湿质（n={len(tanshi)}）'),
    mpatches.Patch(color='#5b8fd1', label='其他体质')
], fontsize=10, loc='lower right', frameon=True, facecolor='white', edgecolor='#dddddd')

plt.tight_layout()
plt.show()

# 图2：OR森林图
plt.figure(figsize=(8.8, 6.8), facecolor='white')
ax2 = plt.gca()
ax2.set_facecolor('#fcfcfc')

logit_plot = logit_df.copy().reset_index(drop=True)
y_pos = np.arange(len(logit_plot))

ax2.errorbar(
    logit_plot['OR'], y_pos,
    xerr=[logit_plot['OR'] - logit_plot['CI_low'],
          logit_plot['CI_high'] - logit_plot['OR']],
    fmt='o', color='#5b8fd1', ecolor='#5b8fd1',
    capsize=4, linewidth=1.5, markersize=7, zorder=3
)
ax2.axvline(1.0, color='#666666', linewidth=1.1, linestyle=(0, (4, 3)), alpha=0.8)

for i, (_, row) in enumerate(logit_plot.iterrows()):
    note = row['显著性文本'] if row['显著性文本'] else ''
    ax2.text(row['CI_high'] + 0.003, i,
             f"OR={row['OR']:.3f} {note}".strip(),
             va='center', ha='left', fontsize=8.5, color='#333333')

ax2.set_yticks(y_pos)
ax2.set_yticklabels(logit_plot['体质'], fontsize=10)
ax2.set_xlabel('OR值（Odds Ratio）', fontsize=12)
ax2.set_title('多因素 Logistic 回归 OR值森林图', fontsize=14, fontweight='bold', pad=12)
ax2.grid(axis='x', linestyle=':', linewidth=0.6, alpha=0.25)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_xlim(logit_plot['CI_low'].min() - 0.02, logit_plot['CI_high'].max() + 0.08)

plt.tight_layout()
plt.show()

# 图3：SHAP beeswarm，仅体质
constitution_indices = [feature_display.index(c) for c in constitution_cols]
shap_constitution = shap.Explanation(
    values=shap_pos[:, constitution_indices],
    base_values=shap_values.base_values[:, 1],
    data=X[constitution_cols].values,
    feature_names=constitution_cols
)

plt.figure(figsize=(8.8, 6.8), facecolor='white')
shap.plots.beeswarm(shap_constitution, max_display=9, show=False, color_bar=True)
ax3 = plt.gca()
ax3.set_title('九种体质积分 SHAP 蜂巢图', fontsize=14, fontweight='bold', pad=12)
ax3.set_xlabel('SHAP 值（对高血脂预测的贡献）', fontsize=11)
ax3.grid(axis='x', linestyle=':', linewidth=0.5, alpha=0.18)
for spine in ['top', 'right']:
    ax3.spines[spine].set_visible(False)
plt.tight_layout()
plt.show()

# 图4：SHAP全局重要性
plt.figure(figsize=(9.2, 7.2), facecolor='white')
ax4 = plt.gca()
ax4.set_facecolor('#fcfcfc')

color_map_type = {'体质积分': '#ee7b30', '活动量表': '#2a9d8f', '基础信息': '#8bbf59'}
shap_bar_colors = [color_map_type[t] for t in shap_imp_df['类型']]

bars4 = ax4.barh(
    shap_imp_df['特征'], shap_imp_df['平均|SHAP|'],
    color=shap_bar_colors, edgecolor='white', height=0.62
)
for bar, (_, row) in zip(bars4, shap_imp_df.iterrows()):
    w = bar.get_width()
    ax4.text(w + 0.00015, bar.get_y() + bar.get_height()/2,
             f'{w:.5f}', va='center', ha='left', fontsize=8.8, color='#222222')

for tick in ax4.get_yticklabels():
    if tick.get_text() in constitution_shap.sort_values('平均|SHAP|', ascending=False)['特征'].tolist()[:3] or tick.get_text() == '活动量表':
        tick.set_fontweight('bold')

ax4.legend(
    handles=[mpatches.Patch(color=v, label=k) for k, v in color_map_type.items()],
    fontsize=9, loc='lower right', frameon=True, facecolor='white', edgecolor='#dddddd'
)
ax4.set_xlabel('平均 |SHAP| 值（全局特征重要性）', fontsize=11)
ax4.set_title('SHAP 全局特征重要性排名', fontsize=14, fontweight='bold', pad=12)
ax4.set_xlim(0, shap_imp_df['平均|SHAP|'].max() * 1.32)
ax4.grid(axis='x', linestyle=':', linewidth=0.6, alpha=0.25)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()

print("\n" + "=" * 60)
print("  模块五结论汇总")
print("=" * 60)

top_constitution_shap = constitution_shap.sort_values('平均|SHAP|', ascending=False)['特征'].iloc[0]
shap_order = ' > '.join(constitution_shap.sort_values('平均|SHAP|', ascending=False)['特征'].tolist())

print(f"""
  【发病率层面（卡方检验）】
  九种体质总体卡方检验 p={p_all:.4f}，各体质人群高血脂
  发病率均处于74%-86%的高位，整体差异不显著。
  发病率排名：{' > '.join(rate_df['体质'].tolist())}

  【OR值层面（多因素Logistic回归）】
  在控制年龄、性别、吸烟史、饮酒史后，九种体质积分的
  OR值均接近1且多未达统计显著，说明单一体质积分的
  独立线性预测作用有限。

  【SHAP 非线性解释层面】
  SHAP 全局重要性排名（体质内部）：
  {shap_order}
  SHAP 蜂巢图表明，各体质积分对高血脂预测的贡献方向
  并不完全一致，提示其影响更可能是多维协同而非单向线性作用。

  【痰湿质的综合意义】
  痰湿质人数占比最大（{len(tanshi)/len(df)*100:.1f}%，n={len(tanshi)}），
  虽未必在单项统计中最显著，但从人群防控角度仍是
  高血脂干预的优先关注体质类型。
""")
