"""
Sensitivity Analysis for DWTS Season 27 - Zipf's Law Exponent (α)
==================================================================

Objective: Find the "tipping point" for Zipf exponent α where Bobby Bones
can survive despite low judge scores.

Test Case: Season 27, Week 8
- Bobby Bones has low judge scores but high fan support
- We vary α from 0.0 to 3.0 to see how vote concentration affects survival

Metrics:
A. Success Rate: % of simulations where Bobby survives
B. Bobby's Estimated Vote Share: Average fan vote % when he survives

Author: MCM 2026 Team
Date: January 30, 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import permutations
import warnings

warnings.filterwarnings('ignore')

# Set publication-quality style
sns.set_style("whitegrid")
sns.set_context("talk")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 18
plt.rcParams['axes.titlesize'] = 24
plt.rcParams['axes.labelsize'] = 20
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']


# ============================================================================
# Data Loading and Preprocessing
# ============================================================================

def load_week_data(filepath, season=27, week=8):
    """Load Season 27 Week 8 data"""
    df = pd.read_csv(filepath)
    season_data = df[df['season'] == season].copy()

    # Extract judge scores
    judge_cols = [col for col in df.columns
                  if col.startswith(f'week{week}_judge') and col.endswith('_score')]

    season_data['judge_score_sum'] = season_data[judge_cols].sum(axis=1, skipna=True)
    active_contestants = season_data[season_data['judge_score_sum'] > 0].copy()

    # Calculate judge ranks
    active_contestants['judge_rank'] = active_contestants['judge_score_sum'].rank(
        ascending=False, method='min'
    )

    return active_contestants[['celebrity_name', 'judge_score_sum', 'judge_rank']]


def get_eliminated_contestant(df, season=27, week=8):
    """Get who was eliminated in Week 8"""
    season_data = df[df['season'] == season]

    for idx, row in season_data.iterrows():
        result = str(row['results']).lower()
        if f'week {week}' in result or f'week{week}' in result:
            if 'eliminated' in result or 'elim' in result:
                return row['celebrity_name']

    return None


# ============================================================================
# Monte Carlo Simulation with Variable Zipf Exponent
# ============================================================================

def monte_carlo_with_zipf_alpha(judge_scores, eliminated_name, alpha, n_simulations=10000):
    """
    Run Monte Carlo simulation with specified Zipf exponent α.

    Args:
        judge_scores: DataFrame with judge scores and ranks
        eliminated_name: Name of contestant who was eliminated
        alpha: Zipf exponent (0 = uniform, 1 = standard Zipf, >1 = more concentrated)
        n_simulations: Number of simulations

    Returns:
        feasible_fan_ranks: List of feasible fan rank assignments
        success_rate: Percentage of simulations that were successful
    """
    contestants = judge_scores['celebrity_name'].tolist()
    judge_score_dict = dict(zip(judge_scores['celebrity_name'],
                                judge_scores['judge_score_sum']))

    n_contestants = len(contestants)
    feasible_fan_ranks = []

    # Generate random rank assignments
    rank_assignments = [np.random.permutation(range(1, n_contestants + 1))
                        for _ in range(n_simulations)]

    for fan_ranks in rank_assignments:
        fan_rank_dict = {contestants[i]: fan_ranks[i] for i in range(n_contestants)}

        # Calculate fan vote percentages using Zipf's Law with exponent α
        if alpha == 0:
            # Special case: uniform distribution
            zipf_scores = {c: 1.0 for c in contestants}
        else:
            # Zipf distribution: Vote ∝ 1 / (Rank^α)
            zipf_scores = {c: 1.0 / (fan_rank_dict[c] ** alpha) for c in contestants}

        total_zipf = sum(zipf_scores.values())
        vote_percentages = {c: (zipf_scores[c] / total_zipf) * 100
                            for c in contestants}

        # Calculate total percentages
        judge_percentages = {}
        total_judge_score = sum(judge_score_dict.values())
        for c in contestants:
            judge_percentages[c] = (judge_score_dict[c] / total_judge_score) * 100

        total_percentages = {c: judge_percentages[c] + vote_percentages[c]
                             for c in contestants}

        # Find who would be eliminated (lowest total percentage)
        would_be_eliminated = min(total_percentages, key=total_percentages.get)

        # Check if simulation matches history
        if would_be_eliminated == eliminated_name:
            feasible_fan_ranks.append(list(fan_ranks))

    success_rate = (len(feasible_fan_ranks) / n_simulations) * 100

    return feasible_fan_ranks, success_rate


def analyze_bobby_vote_share(feasible_fan_ranks, contestants, alpha):
    """
    Calculate Bobby Bones' average vote share from feasible solutions.

    Args:
        feasible_fan_ranks: List of feasible fan rank assignments
        contestants: List of contestant names
        alpha: Zipf exponent used

    Returns:
        bobby_vote_share: Average vote share percentage for Bobby Bones
    """
    if len(feasible_fan_ranks) == 0:
        return 0.0

    bobby_vote_shares = []
    bobby_index = contestants.index('Bobby Bones')

    for fan_ranks in feasible_fan_ranks:
        # Calculate vote shares for this solution
        fan_rank_dict = {contestants[i]: fan_ranks[i] for i in range(len(contestants))}

        if alpha == 0:
            zipf_scores = {c: 1.0 for c in contestants}
        else:
            zipf_scores = {c: 1.0 / (fan_rank_dict[c] ** alpha) for c in contestants}

        total_zipf = sum(zipf_scores.values())
        vote_percentages = {c: (zipf_scores[c] / total_zipf) * 100 for c in contestants}

        bobby_vote_shares.append(vote_percentages['Bobby Bones'])

    return np.mean(bobby_vote_shares)


# ============================================================================
# Sensitivity Analysis
# ============================================================================

def run_sensitivity_analysis(judge_scores, eliminated_name, alpha_range, n_simulations=10000):
    """
    Run sensitivity analysis across different α values.

    Args:
        judge_scores: DataFrame with judge scores
        eliminated_name: Name of eliminated contestant
        alpha_range: List of α values to test
        n_simulations: Number of simulations per α

    Returns:
        results: DataFrame with α, success_rate, bobby_vote_share
    """
    results = []
    contestants = judge_scores['celebrity_name'].tolist()

    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS: Zipf Exponent α")
    print("=" * 70)
    print(f"Testing {len(alpha_range)} different α values...")
    print(f"Simulations per α: {n_simulations}")
    print()

    for i, alpha in enumerate(alpha_range):
        print(f"Progress: {i + 1}/{len(alpha_range)} | α = {alpha:.2f}...", end=" ")

        feasible_ranks, success_rate = monte_carlo_with_zipf_alpha(
            judge_scores, eliminated_name, alpha, n_simulations
        )

        bobby_vote_share = analyze_bobby_vote_share(feasible_ranks, contestants, alpha)

        results.append({
            'alpha': alpha,
            'success_rate': success_rate,
            'bobby_vote_share': bobby_vote_share,
            'n_feasible': len(feasible_ranks)
        })

        print(f"Success Rate: {success_rate:.2f}%, Bobby Vote: {bobby_vote_share:.2f}%")

    return pd.DataFrame(results)


# ============================================================================
# Visualization
# ============================================================================

def plot_sensitivity_results(results_df, output_path='S27_Sensitivity_Analysis.png'):
    """
    Create dual-axis plot showing success rate and Bobby's vote share vs α.
    """
    print("\nCreating visualization...")

    fig, ax1 = plt.subplots(1, 1, figsize=(14, 8))

    # Left Y-axis: Success Rate
    color_success = '#2E86AB'
    ax1.set_xlabel('Zipf Exponent (α)', fontsize=22, fontweight='bold')
    ax1.set_ylabel('Success Rate (%)', fontsize=22, fontweight='bold', color=color_success)

    line1 = ax1.plot(results_df['alpha'], results_df['success_rate'],
                     color=color_success, linewidth=4, marker='o', markersize=10,
                     markeredgewidth=2, markeredgecolor='white',
                     label='Success Rate', zorder=10)

    ax1.tick_params(axis='y', labelcolor=color_success, labelsize=18)
    ax1.tick_params(axis='x', labelsize=18)
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    ax1.set_ylim(0, 100)

    # Right Y-axis: Bobby's Vote Share
    ax2 = ax1.twinx()
    color_bobby = '#F77F00'
    ax2.set_ylabel("Bobby's Estimated Vote Share (%)",
                   fontsize=22, fontweight='bold', color=color_bobby)

    line2 = ax2.plot(results_df['alpha'], results_df['bobby_vote_share'],
                     color=color_bobby, linewidth=4, marker='s', markersize=10,
                     markeredgewidth=2, markeredgecolor='white',
                     label="Bobby's Vote Share", zorder=10)

    ax2.tick_params(axis='y', labelcolor=color_bobby, labelsize=18)
    ax2.set_ylim(0, max(results_df['bobby_vote_share']) * 1.2)

    # Find tipping point (where success rate becomes > 0)
    tipping_idx = results_df[results_df['success_rate'] > 0].index
    if len(tipping_idx) > 0:
        tipping_alpha = results_df.loc[tipping_idx[0], 'alpha']
        ax1.axvline(x=tipping_alpha, color='red', linestyle='--', linewidth=3,
                    alpha=0.7, label=f'Tipping Point (α = {tipping_alpha:.2f})')

        # Add annotation
        ax1.annotate(f'Critical α = {tipping_alpha:.2f}',
                     xy=(tipping_alpha, 50), xytext=(tipping_alpha + 0.3, 50),
                     fontsize=16, color='red', fontweight='bold',
                     arrowprops=dict(arrowstyle='->', color='red', lw=2))

    # Mark standard Zipf (α = 1.0)
    if 1.0 in results_df['alpha'].values:
        ax1.axvline(x=1.0, color='green', linestyle=':', linewidth=2.5,
                    alpha=0.6, label='Standard Zipf (α = 1.0)')

    # Title
    plt.title('Sensitivity Analysis: Zipf Exponent Impact on Bobby Bones Survival\n' +
              'Season 27, Week 8',
              fontsize=24, fontweight='bold', pad=25)

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper left', fontsize=16, framealpha=0.95,
               fancybox=True, shadow=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {output_path}")
    plt.close()


def print_analysis_summary(results_df):
    """Print summary statistics and findings"""
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)

    # Find tipping point
    feasible = results_df[results_df['success_rate'] > 0]
    if len(feasible) > 0:
        tipping_alpha = feasible['alpha'].min()
        tipping_success = feasible.iloc[0]['success_rate']
        print(f"\n🎯 TIPPING POINT FOUND:")
        print(f"   Critical α = {tipping_alpha:.2f}")
        print(f"   At this point, success rate = {tipping_success:.2f}%")
        print(f"   Interpretation: Fan votes must be concentrated with α ≥ {tipping_alpha:.2f}")
        print(f"   for Bobby Bones to survive despite low judge scores.")
    else:
        print(f"\n⚠️  NO TIPPING POINT FOUND in range [0, 3.0]")
        print(f"   Bobby Bones cannot survive with any tested α value.")

    # Standard Zipf performance
    if 1.0 in results_df['alpha'].values:
        std_zipf = results_df[results_df['alpha'] == 1.0].iloc[0]
        print(f"\n📊 STANDARD ZIPF (α = 1.0) PERFORMANCE:")
        print(f"   Success Rate: {std_zipf['success_rate']:.2f}%")
        print(f"   Bobby's Vote Share: {std_zipf['bobby_vote_share']:.2f}%")

    # Extreme cases
    print(f"\n📈 EXTREME CASES:")
    min_alpha = results_df['alpha'].min()
    max_alpha = results_df['alpha'].max()

    min_case = results_df[results_df['alpha'] == min_alpha].iloc[0]
    max_case = results_df[results_df['alpha'] == max_alpha].iloc[0]

    print(f"   α = {min_alpha:.2f} (Uniform):")
    print(f"      Success Rate: {min_case['success_rate']:.2f}%")
    print(f"      Bobby's Vote: {min_case['bobby_vote_share']:.2f}%")

    print(f"   α = {max_alpha:.2f} (Winner-Takes-All):")
    print(f"      Success Rate: {max_case['success_rate']:.2f}%")
    print(f"      Bobby's Vote: {max_case['bobby_vote_share']:.2f}%")

    # Key insight
    print(f"\n💡 KEY INSIGHT:")
    vote_increase = max_case['bobby_vote_share'] - min_case['bobby_vote_share']
    print(f"   As α increases from {min_alpha} to {max_alpha}, Bobby's vote share")
    print(f"   increases by {vote_increase:.1f} percentage points.")
    print(f"   This demonstrates the critical role of vote concentration in")
    print(f"   enabling underdog contestants to overcome judge score deficits.")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Run complete sensitivity analysis"""
    print("=" * 70)
    print("SENSITIVITY ANALYSIS: ZIPF EXPONENT (α)")
    print("Season 27, Week 8 - Bobby Bones Survival")
    print("=" * 70)

    # Load data
    filepath = r'C:\Users\tx\AppData\Roaming\Kingsoft\office6\templates\wps\zh_CN\2026_MCM_Problem_C_Data.csv'
    df = pd.read_csv(filepath)

    print("\nLoading Season 27 Week 8 data...")
    judge_scores = load_week_data(filepath, season=27, week=8)
    eliminated_name = get_eliminated_contestant(df, season=27, week=8)

    print(f"\nActive contestants: {len(judge_scores)}")
    print(f"Eliminated contestant: {eliminated_name}")
    print("\nJudge Rankings:")
    print(judge_scores.to_string(index=False))

    # Check if Bobby Bones is in the data
    if 'Bobby Bones' not in judge_scores['celebrity_name'].values:
        print("\n❌ ERROR: Bobby Bones not found in Week 8 data!")
        print("Available contestants:", judge_scores['celebrity_name'].tolist())
        return

    bobby_rank = judge_scores[judge_scores['celebrity_name'] == 'Bobby Bones']['judge_rank'].values[0]
    print(f"\n🎯 Bobby Bones Judge Rank: {bobby_rank}")

    # Define α range
    alpha_range = np.arange(0.0, 3.1, 0.2)
    print(f"\nTesting α values: {alpha_range[0]:.1f} to {alpha_range[-1]:.1f} (step 0.2)")

    # Run sensitivity analysis
    results_df = run_sensitivity_analysis(
        judge_scores, eliminated_name, alpha_range, n_simulations=10000
    )

    # Save results
    results_df.to_csv('S27_Sensitivity_Results.csv', index=False)
    print("\n✅ Results saved to: S27_Sensitivity_Results.csv")

    # Print detailed results table
    print("\n" + "=" * 70)
    print("DETAILED RESULTS TABLE")
    print("=" * 70)
    print(results_df.to_string(index=False))

    # Create visualization
    plot_sensitivity_results(results_df)

    # Print summary
    print_analysis_summary(results_df)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print("\n📁 Generated Files:")
    print("   - S27_Sensitivity_Results.csv (detailed data)")
    print("   - S27_Sensitivity_Analysis.png (visualization)")
    print("\n🎯 Use these results to demonstrate model robustness in your paper!")


if __name__ == "__main__":
    main()