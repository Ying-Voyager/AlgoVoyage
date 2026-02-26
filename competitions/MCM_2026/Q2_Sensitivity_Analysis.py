"""
Sensitivity Analysis: Fan Power vs Survival Probability
========================================================

Research Question: How does fan support strength affect survival under different methods?
Scenario: Technically weak contestant (Judge Rank 12/12)

Author: MCM 2026 Team
Date: January 31, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 设置专业级绘图风格
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['font.size'] = 13


def calculate_zipf_distribution(n, alpha=1.3):
    """
    Calculate Zipf distribution for fan vote shares.

    Args:
        n: Number of contestants
        alpha: Zipf exponent (1.3 based on DWTS empirical data)

    Returns:
        Array of vote shares (sum to 1.0)
    """
    ranks = np.arange(1, n + 1)
    weights = 1.0 / (ranks ** alpha)
    shares = weights / weights.sum()
    return shares


def run_sensitivity_analysis():
    """
    Run sensitivity analysis: Fan strength vs survival probability
    """
    print("="*70)
    print("SENSITIVITY ANALYSIS: FAN POWER VS SURVIVAL")
    print("="*70)
    print("\nScenario: Technically weak contestant (Judge Rank 12/12)")
    print("Question: What fan rank is needed to survive?\n")

    # ============================================================================
    # 1. Parameter Setup
    # ============================================================================

    n_contestants = 12
    judge_rank = 12  # Worst judge rank (Bobby Bones scenario)

    # Assume judge score for rank 12: approximately 18 points
    judge_score = 18.0
    estimated_total_judge = n_contestants * 22.5

    fan_ranks = np.arange(1, n_contestants + 1)

    # Calculate Zipf distribution for fan votes
    fan_shares = calculate_zipf_distribution(n_contestants, alpha=1.3)

    print(f"Setup:")
    print(f"  N contestants: {n_contestants}")
    print(f"  Your judge rank: {judge_rank}/{n_contestants} (worst)")
    print(f"  Your judge score: {judge_score} points")
    print(f"\nFan vote distribution (Zipf α=1.3):")
    print(f"  Rank 1: {fan_shares[0]*100:.1f}%")
    print(f"  Rank 6: {fan_shares[5]*100:.1f}%")
    print(f"  Rank 12: {fan_shares[11]*100:.1f}%")

    # ============================================================================
    # 2. Calculate Safety Margins
    # ============================================================================

    results = []

    for fan_rank in fan_ranks:
        # --- Method A: Rank Sum ---
        your_total_rank = judge_rank + fan_rank

        # Elimination threshold: worst possible combination
        # In 12-person competition: 12 + 11 = 23
        elimination_threshold_rank = n_contestants + (n_contestants - 1)

        # Safety margin: positive = safe, negative = danger
        rank_sum_margin = elimination_threshold_rank - your_total_rank

        # --- Method B: Percentage ---
        your_judge_pct = (judge_score / estimated_total_judge) * 100
        your_fan_pct = fan_shares[fan_rank - 1] * 100
        your_total_pct = your_judge_pct + your_fan_pct

        # Elimination threshold: Bottom 2 typically around 7-8%
        elimination_threshold_pct = 8.0

        # Safety margin: positive = safe, negative = danger
        pct_margin = your_total_pct - elimination_threshold_pct

        results.append({
            'Fan_Rank': fan_rank,
            'Fan_Share_Pct': your_fan_pct,
            'Total_Rank': your_total_rank,
            'Rank_Sum_Margin': rank_sum_margin,
            'Total_Pct': your_total_pct,
            'Pct_Margin': pct_margin
        })

    df_sens = pd.DataFrame(results)

    # ============================================================================
    # 3. Analysis Summary
    # ============================================================================

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    # Find critical fan ranks
    critical_rank_sum = df_sens[df_sens['Rank_Sum_Margin'] > 0]['Fan_Rank'].max()
    critical_pct = df_sens[df_sens['Pct_Margin'] > 0]['Fan_Rank'].max()

    print(f"\nCritical Fan Ranks (maximum to survive):")
    print(f"  Rank Sum Method: Need Fan Rank ≤ {critical_rank_sum if not pd.isna(critical_rank_sum) else 0}")
    print(f"  Percentage Method: Need Fan Rank ≤ {critical_pct if not pd.isna(critical_pct) else 0}")

    if not pd.isna(critical_pct) and not pd.isna(critical_rank_sum):
        tolerance_diff = critical_pct - critical_rank_sum
        print(f"\n🎯 KEY FINDING:")
        print(f"   Percentage Method gives {tolerance_diff:.0f} more ranks of tolerance")
        print(f"   This is the 'Superstar Immunity' effect!")

    # Print table
    print(f"\nDetailed Results Table:")
    print("-"*70)
    print(df_sens[['Fan_Rank', 'Total_Rank', 'Rank_Sum_Margin',
                   'Total_Pct', 'Pct_Margin']].to_string(index=False))

    # ============================================================================
    # 4. Visualization
    # ============================================================================

    plot_safety_margins(df_sens, n_contestants)

    # Save data
    df_sens.to_csv('Sensitivity_Analysis_Results.csv', index=False)
    print("\n✅ Data saved: Sensitivity_Analysis_Results.csv")

    return df_sens


def plot_safety_margins(df, n_contestants):
    """
    Create safety margin plot (dual axis)
    """
    print("\n" + "="*70)
    print("CREATING VISUALIZATION")
    print("="*70)

    fig, ax1 = plt.subplots(figsize=(14, 9))

    color_rank = '#E74C3C'  # Red
    color_pct = '#3498DB'   # Blue

    ax2 = ax1.twinx()

    # ============================================================================
    # Plot Rank Sum (left axis, red)
    # ============================================================================

    line1 = ax1.plot(df['Fan_Rank'], df['Rank_Sum_Margin'],
                    color=color_rank, marker='o', linewidth=4, markersize=11,
                    markeredgewidth=2.5, markeredgecolor='white',
                    label='Rank Sum Method', zorder=10)

    ax1.set_xlabel('Fan Rank (1 = Most Popular, 12 = Least Popular)',
                  fontsize=16, fontweight='bold')
    ax1.set_ylabel('Safety Margin\n(Rank Sum Method)', color=color_rank,
                  fontsize=16, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color_rank, labelsize=13)

    # ============================================================================
    # Plot Percentage (right axis, blue)
    # ============================================================================

    line2 = ax2.plot(df['Fan_Rank'], df['Pct_Margin'],
                    color=color_pct, marker='s', linewidth=4, markersize=11,
                    markeredgewidth=2.5, markeredgecolor='white',
                    linestyle='--', label='Percentage Method', zorder=10)

    ax2.set_ylabel('Safety Margin\n(Percentage Method, percentage points)',
                  color=color_pct, fontsize=16, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color_pct, labelsize=13)

    # ============================================================================
    # Add zero line (elimination threshold)
    # ============================================================================

    ax1.axhline(0, color='black', linestyle='-', linewidth=3, alpha=0.8, zorder=5)
    ax1.text(n_contestants + 0.4, 0, 'Elimination\nThreshold',
            fontsize=12, fontweight='bold', va='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                     edgecolor='black', linewidth=2))

    # ============================================================================
    # Add danger zones (shaded areas below zero)
    # ============================================================================

    y_min = min(df['Rank_Sum_Margin'].min(), df['Pct_Margin'].min()) - 2

    ax1.fill_between(df['Fan_Rank'], y_min, 0,
                    color=color_rank, alpha=0.12, zorder=1)
    ax1.text(9, y_min + 1, 'DANGER ZONE\n(Likely Elimination)',
            color=color_rank, fontsize=13, fontweight='bold',
            ha='center', alpha=0.7)

    # ============================================================================
    # Add annotations
    # ============================================================================

    # Superstar immunity
    superstar_margin = df['Pct_Margin'].iloc[0]
    ax2.annotate('Superstar\nImmunity',
                xy=(1, superstar_margin),
                xytext=(2.5, superstar_margin - 4),
                arrowprops=dict(arrowstyle='->', color=color_pct, lw=3),
                fontsize=13, fontweight='bold', color=color_pct,
                bbox=dict(boxstyle='round,pad=0.6', facecolor='lightblue',
                         edgecolor=color_pct, linewidth=2.5, alpha=0.9))

    # Critical point for Rank Sum
    if df['Rank_Sum_Margin'].min() < 0:
        first_danger_idx = df[df['Rank_Sum_Margin'] < 0].index[0]
        first_danger_rank = df.loc[first_danger_idx, 'Fan_Rank']
        first_danger_margin = df.loc[first_danger_idx, 'Rank_Sum_Margin']

        ax1.annotate('Elimination\nStarts Here',
                    xy=(first_danger_rank, first_danger_margin),
                    xytext=(first_danger_rank - 2.5, first_danger_margin - 2),
                    arrowprops=dict(arrowstyle='->', color=color_rank, lw=3),
                    fontsize=13, fontweight='bold', color=color_rank,
                    bbox=dict(boxstyle='round,pad=0.6', facecolor='lightcoral',
                             edgecolor=color_rank, linewidth=2.5, alpha=0.9))

    # ============================================================================
    # Legend
    # ============================================================================

    lines = line1 + line2
    labels = ['Rank Sum: Linear decline with fan rank',
             'Percentage: Exponential protection (Zipf α=1.3)']

    legend = ax1.legend(lines, labels, loc='upper right', fontsize=14,
                       framealpha=0.95, fancybox=True, shadow=True)
    legend.get_frame().set_linewidth(2)
    legend.get_frame().set_edgecolor('black')

    # ============================================================================
    # Title and styling
    # ============================================================================

    plt.title('Sensitivity Analysis: The "Superstar Immunity" Effect\n' +
             'How fan support strength determines survival for technically weak contestants\n' +
             'Scenario: Judge Rank 12/12 (Worst Technical Performance)',
             fontsize=17, fontweight='bold', pad=25)

    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=1)
    ax1.set_axisbelow(True)
    ax1.set_xticks(df['Fan_Rank'])
    ax1.set_xlim(0.5, n_contestants + 0.5)

    # Set y-axis limits to show full range
    ax1.set_ylim(y_min, df['Rank_Sum_Margin'].max() + 2)
    ax2.set_ylim(y_min, df['Pct_Margin'].max() + 2)

    plt.tight_layout()
    plt.savefig('Sensitivity_Analysis_Q2.png', dpi=300,
               bbox_inches='tight', facecolor='white')

    print("✅ Visualization saved: Sensitivity_Analysis_Q2.png")
    print("\n📊 Figure shows:")
    print("   - Red line (Rank Sum): Linear decline")
    print("   - Blue line (Percentage): Exponential protection")
    print("   - Clear 'Superstar Immunity' at Fan Rank 1-3")
    print("   - Danger zone shaded in red")


if __name__ == "__main__":
    print("\n" + "🎯"*35)
    print("SENSITIVITY ANALYSIS: FAN POWER VS SURVIVAL PROBABILITY")
    print("🎯"*35 + "\n")

    df = run_sensitivity_analysis()

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\n💡 HOW TO INTERPRET THE RESULTS:")
    print("\n1. RED LINE (Rank Sum Method):")
    print("   - Declines linearly as fan rank worsens")
    print("   - Crosses zero around Fan Rank 11")
    print("   - Below zero = elimination likely")
    print("\n2. BLUE LINE (Percentage Method):")
    print("   - Stays high for top fan ranks (1-5)")
    print("   - Shows 'Superstar Immunity' effect")
    print("   - Much more forgiving than Rank Sum")
    print("\n3. KEY INSIGHT:")
    print("   Even with WORST judge scores, top fan favorites")
    print("   can survive under Percentage Method!")
    print("   This explains Bobby Bones, Bristol Palin, etc.")
    print("\n" + "="*70)