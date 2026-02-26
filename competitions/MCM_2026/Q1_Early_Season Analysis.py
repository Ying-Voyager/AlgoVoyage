"""
Monte Carlo Simulation for Fan Vote Estimation in DWTS - ENHANCED WITH VOTE SHARE
-----------------------------------------------------------------------------------
O-Award Level Visualizations for Season 2 + Zipf's Law Vote Share Estimation

NEW FEATURE:
4. Rank-to-Vote Conversion using Zipf's Law: Votes ∝ 1/Rank

Author: MCM 2026 Team
Date: January 30, 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import permutations
import warnings
import os
warnings.filterwarnings('ignore')

# Set O-award publication-quality style with Times New Roman
sns.set_style("whitegrid")
sns.set_context("talk")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 18          # Increased
plt.rcParams['axes.titlesize'] = 26    # Increased
plt.rcParams['axes.labelsize'] = 22    # Increased
plt.rcParams['xtick.labelsize'] = 18   # Increased
plt.rcParams['ytick.labelsize'] = 18   # Increased
plt.rcParams['legend.fontsize'] = 17   # Increased
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']

# ============================================================================
# SECTION 1: Data Preprocessing
# ============================================================================

def load_and_preprocess_data(filepath):
    """Load DWTS data and extract Season 2 information."""
    df = pd.read_csv(filepath)
    df_s2 = df[df['season'] == 2].copy()

    week_cols = [col for col in df.columns if 'week' in col and 'judge' in col]
    max_week = max([int(col.split('_')[0].replace('week', '')) for col in week_cols])

    print(f"Maximum week number found: {max_week}")
    print(f"Total contestants in Season 2: {len(df_s2)}")

    return df_s2, max_week


def extract_judge_scores_by_week(df, season, week):
    """
    Extract judge scores and calculate ranks.
    CRITICAL: ascending=False, method='min' (high score = Rank 1)
    """
    season_data = df[df['season'] == season].copy()

    judge_cols = [col for col in df.columns
                  if col.startswith(f'week{week}_judge') and col.endswith('_score')]

    season_data['judge_score_sum'] = season_data[judge_cols].sum(axis=1, skipna=True)
    active_contestants = season_data[season_data['judge_score_sum'] > 0].copy()

    # CRITICAL: ascending=False, method='min'
    active_contestants['judge_rank'] = active_contestants['judge_score_sum'].rank(
        ascending=False, method='min'
    )

    return active_contestants[['celebrity_name', 'judge_score_sum', 'judge_rank']]


def get_eliminated_contestant(df, season, week):
    """Identify who was eliminated in a specific week."""
    season_data = df[df['season'] == season]

    for idx, row in season_data.iterrows():
        result = str(row['results']).lower()
        if f'week {week}' in result or f'week{week}' in result:
            if 'eliminated' in result or 'elim' in result:
                return row['celebrity_name']

    return None


def get_final_placement(df, season):
    """Get final placement for each celebrity."""
    season_data = df[df['season'] == season]
    placement_dict = {}
    for idx, row in season_data.iterrows():
        celeb = row['celebrity_name']
        placement = row.get('placement', 999)
        if pd.notna(placement):
            placement_dict[celeb] = placement
        else:
            placement_dict[celeb] = 999
    return placement_dict


# ============================================================================
# SECTION 2: Monte Carlo Simulation Core WITH TIE-BREAKER LOGIC
# ============================================================================

def monte_carlo_simulation_with_tiebreaker(judge_ranks, eliminated_name, n_simulations=10000):
    """
    Monte Carlo simulation with TIE-BREAKER LOGIC.

    When total_rank ties occur:
    - Compare fan ranks
    - Lower fan rank (better) = survivor wins
    - Keep simulation only if it matches historical elimination
    """
    contestants = judge_ranks['celebrity_name'].tolist()
    judge_rank_dict = dict(zip(judge_ranks['celebrity_name'],
                               judge_ranks['judge_rank']))

    n_contestants = len(contestants)
    feasible_fan_ranks = []

    print(f"  Using random sampling with tie-breaker: {n_simulations} simulations...")
    rank_assignments = [np.random.permutation(range(1, n_contestants + 1))
                       for _ in range(n_simulations)]

    test_counter = 0
    for fan_ranks in rank_assignments:
        test_counter += 1
        if test_counter % (n_simulations // 10) == 0:
            print(f"    Progress: {test_counter}/{n_simulations} ({100*test_counter/n_simulations:.1f}%)")

        # Calculate total ranks (judge + fan)
        total_ranks = {}
        fan_rank_dict = {}
        for i, contestant in enumerate(contestants):
            total_ranks[contestant] = judge_rank_dict[contestant] + fan_ranks[i]
            fan_rank_dict[contestant] = fan_ranks[i]

        # Find maximum total rank (worst performer)
        max_total_rank = max(total_ranks.values())

        # Get all contestants with max total rank (potential ties)
        tied_contestants = [c for c, r in total_ranks.items() if r == max_total_rank]

        # CRITICAL TIE-BREAKER LOGIC
        if len(tied_contestants) > 1:
            # TIE SITUATION: Use fan rank as tie-breaker
            # Higher fan rank number = worse fan support = eliminated
            would_be_eliminated = max(tied_contestants, key=lambda c: fan_rank_dict[c])
        else:
            # NO TIE: Single contestant with worst total rank
            would_be_eliminated = tied_contestants[0]

        # Check if simulation matches historical elimination
        if would_be_eliminated == eliminated_name:
            feasible_fan_ranks.append(list(fan_ranks))

    print(f"  Found {len(feasible_fan_ranks)} feasible solutions (with tie-breaker)")

    return feasible_fan_ranks, contestants


def analyze_fan_ranks(feasible_fan_ranks, contestants):
    """Analyze the distribution of feasible fan ranks."""
    if len(feasible_fan_ranks) == 0:
        print("  WARNING: No feasible solutions found!")
        return pd.DataFrame()

    fan_ranks_array = np.array(feasible_fan_ranks)

    results = []
    for i, contestant in enumerate(contestants):
        contestant_ranks = fan_ranks_array[:, i]
        results.append({
            'celebrity_name': contestant,
            'estimated_fan_rank_mean': contestant_ranks.mean(),
            'estimated_fan_rank_std': contestant_ranks.std(),
            'estimated_fan_rank_min': contestant_ranks.min(),
            'estimated_fan_rank_max': contestant_ranks.max(),
            'n_feasible_solutions': len(feasible_fan_ranks)
        })

    return pd.DataFrame(results)


def analyze_season_week(df, season, week, n_simulations=10000):
    """Analyze a specific season and week."""
    print(f"\n{'='*70}")
    print(f"Analyzing Season {season}, Week {week}")
    print(f"{'='*70}")

    judge_ranks = extract_judge_scores_by_week(df, season, week)

    if len(judge_ranks) == 0:
        print(f"No active contestants found for Season {season} Week {week}")
        return None, None, None

    print(f"\nActive contestants: {len(judge_ranks)}")
    print("\nJudge Scores and Ranks:")
    print(judge_ranks.to_string())

    eliminated_name = get_eliminated_contestant(df, season, week)
    print(f"\nEliminated contestant: {eliminated_name}")

    if eliminated_name is None:
        print("WARNING: Could not identify eliminated contestant")
        return None, None, judge_ranks

    # Use tie-breaker version
    feasible_fan_ranks, contestants = monte_carlo_simulation_with_tiebreaker(
        judge_ranks, eliminated_name, n_simulations=n_simulations
    )

    if len(feasible_fan_ranks) == 0:
        return None, feasible_fan_ranks, judge_ranks

    results_df = analyze_fan_ranks(feasible_fan_ranks, contestants)

    print("\nEstimated Fan Ranks:")
    print(results_df.to_string())

    return results_df, feasible_fan_ranks, judge_ranks


# ============================================================================
# SECTION 2.5: ZIPF'S LAW VOTE SHARE CONVERSION
# ============================================================================

def calculate_vote_share_zipf(all_results):
    """
    Calculate estimated vote share using Zipf's Law.

    Zipf's Law: Votes ∝ 1/Rank
    Vote Share % = (1/Rank_i) / Σ(1/Rank_j) × 100%

    Returns:
        DataFrame with vote shares for each contestant per week
    """
    print("\n" + "="*70)
    print("Calculating Vote Shares using Zipf's Law...")
    print("="*70)

    vote_share_data = []

    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    for week in weeks:
        results_df = all_results[week]
        if results_df is None or results_df.empty:
            continue

        # Get fan ranks for this week
        contestants = results_df['celebrity_name'].tolist()
        fan_ranks = results_df['estimated_fan_rank_mean'].values

        # Calculate Zipf scores (1/Rank)
        zipf_scores = 1.0 / fan_ranks
        total_zipf = zipf_scores.sum()

        # Calculate vote share percentages
        vote_shares = (zipf_scores / total_zipf) * 100

        # Store results
        for celeb, rank, share in zip(contestants, fan_ranks, vote_shares):
            vote_share_data.append({
                'week': week,
                'celebrity_name': celeb,
                'estimated_fan_rank': rank,
                'vote_share_percent': share
            })

        print(f"\nWeek {week} Vote Share Distribution:")
        week_df = pd.DataFrame({
            'Celebrity': contestants,
            'Fan Rank': fan_ranks,
            'Vote Share %': vote_shares
        })
        week_df = week_df.sort_values('Vote Share %', ascending=False)
        print(week_df.to_string(index=False))

    return pd.DataFrame(vote_share_data)


# ============================================================================
# SECTION 3A: VISUALIZATION - TRAJECTORIES
# ============================================================================

def plot_s2_trajectories(all_results, output_dir):
    """Chart 1A: Fan Rank Trajectories"""
    print("\n" + "="*70)
    print("Creating Chart 1A: Fan Rank Trajectories...")
    print("="*70)

    if not all_results:
        print("No results to plot")
        return

    fig, ax = plt.subplots(1, 1, figsize=(14, 9))

    all_celebrities = set()
    for week_num, results_df in all_results.items():
        if results_df is not None and not results_df.empty:
            all_celebrities.update(results_df['celebrity_name'].tolist())

    all_celebrities_sorted = sorted(list(all_celebrities))
    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    n_celebs = len(all_celebrities_sorted)
    colors = plt.cm.Set3(np.linspace(0, 1, 12)) if n_celebs <= 12 else plt.cm.tab20(np.linspace(0, 1, 20))
    celeb_colors = {celeb: colors[i % len(colors)] for i, celeb in enumerate(all_celebrities_sorted)}

    for celebrity in all_celebrities_sorted:
        trajectory_weeks = []
        trajectory_means = []
        trajectory_stds = []
        elimination_week = None

        for week in weeks:
            results_df = all_results[week]
            if results_df is not None and not results_df.empty:
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    trajectory_weeks.append(week)
                    trajectory_means.append(celeb_data['estimated_fan_rank_mean'].values[0])
                    trajectory_stds.append(celeb_data['estimated_fan_rank_std'].values[0])
                elif len(trajectory_weeks) > 0:
                    elimination_week = trajectory_weeks[-1]
                    break

        if len(trajectory_weeks) == 0:
            continue

        trajectory_means = np.array(trajectory_means)
        trajectory_stds = np.array(trajectory_stds)
        color = celeb_colors[celebrity]

        ax.plot(trajectory_weeks, trajectory_means,
               label=celebrity, color=color, alpha=0.85, linewidth=3.2,
               marker='o', markersize=10, zorder=10, markeredgewidth=2.2,
               markeredgecolor='white')

        ax.fill_between(trajectory_weeks,
                       trajectory_means - trajectory_stds,
                       trajectory_means + trajectory_stds,
                       color=color, alpha=0.15, zorder=5)

        if elimination_week is not None:
            elim_idx = trajectory_weeks.index(elimination_week)
            ax.plot(trajectory_weeks[elim_idx], trajectory_means[elim_idx],
                   'X', color='darkred', markersize=22, markeredgewidth=3,
                   markeredgecolor='white', zorder=20)

    ax.set_xlabel('Week Number', fontsize=22, fontweight='bold')
    ax.set_ylabel('Estimated Fan Rank', fontsize=22, fontweight='bold')
    ax.set_title('Season 2: Fan Rank Evolution Over Time', fontsize=26, fontweight='bold', pad=25)
    ax.legend(loc='best', framealpha=0.95, fontsize=14, ncol=2,
             fancybox=True, shadow=True)
    ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
    ax.invert_yaxis()

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'S2_Trajectories.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


# ============================================================================
# SECTION 3B: VISUALIZATION - HEATMAP
# ============================================================================

def plot_s2_heatmap(all_results, df, output_dir):
    """Chart 1B: Uncertainty Heatmap"""
    print("\n" + "="*70)
    print("Creating Chart 1B: Uncertainty Heatmap...")
    print("="*70)

    if not all_results:
        print("No results to plot")
        return

    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    all_celebrities = set()
    for week_num, results_df in all_results.items():
        if results_df is not None and not results_df.empty:
            all_celebrities.update(results_df['celebrity_name'].tolist())

    all_celebrities_sorted = sorted(list(all_celebrities))
    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])
    weeks_sorted = sorted(weeks)

    placement_dict = get_final_placement(df, 2)
    all_celebrities_by_placement = sorted(
        all_celebrities_sorted,
        key=lambda x: placement_dict.get(x, 999)
    )

    heatmap_data = np.full((len(all_celebrities_by_placement), len(weeks_sorted)), np.nan)

    for week_idx, week_key in enumerate(weeks_sorted):
        results_df = all_results[week_key]
        if results_df is not None and not results_df.empty:
            for celeb_idx, celebrity in enumerate(all_celebrities_by_placement):
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    heatmap_data[celeb_idx, week_idx] = \
                        celeb_data['estimated_fan_rank_std'].values[0]

    sns.heatmap(heatmap_data,
                xticklabels=[f'Week {int(w)}' for w in weeks_sorted],
                yticklabels=all_celebrities_by_placement,
                cmap='YlOrRd', annot=True, fmt='.2f',
                cbar_kws={'label': 'Uncertainty (Std Dev)', 'shrink': 0.85},
                ax=ax, linewidths=1.8, linecolor='white',
                mask=np.isnan(heatmap_data), vmin=0,
                annot_kws={'fontsize': 13, 'fontweight': 'bold', 'family': 'serif'})

    ax.set_xlabel('Week Number', fontsize=22, fontweight='bold')
    ax.set_ylabel('Celebrity (Sorted by Final Placement)', fontsize=22, fontweight='bold')
    ax.set_title('Season 2: Estimation Uncertainty Heatmap', fontsize=26, fontweight='bold', pad=25)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'S2_Uncertainty_Heatmap.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


# ============================================================================
# SECTION 3C: VISUALIZATION - VOTE SHARE (NEW!)
# ============================================================================

def plot_vote_share_evolution(vote_share_df, output_dir):
    """
    NEW CHART: Vote Share Evolution using Zipf's Law
    Shows estimated vote percentage for each contestant over time
    """
    print("\n" + "="*70)
    print("Creating NEW Chart: Vote Share Evolution (Zipf's Law)...")
    print("="*70)

    if vote_share_df is None or vote_share_df.empty:
        print("No vote share data to plot")
        return

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))

    # Get unique celebrities
    celebrities = vote_share_df['celebrity_name'].unique()
    weeks = sorted(vote_share_df['week'].unique())

    # Color palette
    n_celebs = len(celebrities)
    colors = plt.cm.Set3(np.linspace(0, 1, 12)) if n_celebs <= 12 else plt.cm.tab20(np.linspace(0, 1, 20))
    celeb_colors = {celeb: colors[i % len(colors)] for i, celeb in enumerate(sorted(celebrities))}

    # Plot each celebrity's vote share evolution
    for celebrity in sorted(celebrities):
        celeb_data = vote_share_df[vote_share_df['celebrity_name'] == celebrity]
        celeb_weeks = celeb_data['week'].values
        vote_shares = celeb_data['vote_share_percent'].values

        if len(celeb_weeks) == 0:
            continue

        color = celeb_colors[celebrity]

        # Plot line
        ax.plot(celeb_weeks, vote_shares,
               label=celebrity, color=color, alpha=0.85,
               linewidth=3.5, marker='o', markersize=11,
               markeredgewidth=2.5, markeredgecolor='white', zorder=10)

        # Add percentage labels at key points
        for i, (week, share) in enumerate(zip(celeb_weeks, vote_shares)):
            if i == len(celeb_weeks) - 1:  # Last point
                ax.annotate(f'{share:.1f}%',
                          xy=(week, share),
                          xytext=(5, 0),
                          textcoords='offset points',
                          fontsize=11, fontweight='bold',
                          color=color, family='serif')

    ax.set_xlabel('Week Number', fontsize=22, fontweight='bold')
    ax.set_ylabel('Estimated Vote Share (%)', fontsize=22, fontweight='bold')
    ax.set_title('Season 2: Estimated Fan Vote Share Evolution (Zipf\'s Law)',
                fontsize=26, fontweight='bold', pad=25)
    ax.legend(loc='best', framealpha=0.95, fontsize=14, ncol=2,
             fancybox=True, shadow=True)
    ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)

    # Add horizontal reference line at equal share
    if len(weeks) > 0:
        first_week = weeks[0]
        n_contestants_first = len(vote_share_df[vote_share_df['week'] == first_week])
        equal_share = 100.0 / n_contestants_first if n_contestants_first > 0 else 10
        ax.axhline(y=equal_share, color='gray', linestyle=':',
                  linewidth=2, alpha=0.5, label=f'Equal Share ({equal_share:.1f}%)')

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'S2_Vote_Share_Evolution.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


def plot_vote_share_stacked_area(vote_share_df, output_dir):
    """
    Alternative: Stacked Area Chart showing vote share distribution
    Shows how the "vote pie" changes over time
    """
    print("\n" + "="*70)
    print("Creating Chart: Vote Share Distribution (Stacked Area)...")
    print("="*70)

    if vote_share_df is None or vote_share_df.empty:
        print("No vote share data to plot")
        return

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))

    # Pivot data for stacked area
    pivot_df = vote_share_df.pivot(index='week',
                                    columns='celebrity_name',
                                    values='vote_share_percent')

    # Sort columns by final average vote share
    col_order = pivot_df.mean().sort_values(ascending=False).index
    pivot_df = pivot_df[col_order]

    # Create stacked area plot
    pivot_df.plot(kind='area', stacked=True, ax=ax,
                 alpha=0.7, linewidth=2.5,
                 color=plt.cm.Set3(np.linspace(0, 1, len(pivot_df.columns))))

    ax.set_xlabel('Week Number', fontsize=22, fontweight='bold')
    ax.set_ylabel('Vote Share (%)', fontsize=22, fontweight='bold')
    ax.set_title('Season 2: Vote Share Distribution Over Time (Zipf\'s Law)',
                fontsize=26, fontweight='bold', pad=25)
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
             framealpha=0.95, fontsize=13, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    ax.set_ylim([0, 100])

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'S2_Vote_Share_Stacked.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


# ============================================================================
# SECTION 4: VISUALIZATION - KEY CASE STUDIES
# ============================================================================

def plot_s2_case_studies(all_results, all_judge_ranks, output_dir):
    """Chart 2: Key Case Studies"""
    print("\n" + "="*70)
    print("Creating Chart 2: Season 2 Case Studies...")
    print("="*70)

    if not all_results or not all_judge_ranks:
        print("No results to plot")
        return

    key_celebs = ['Master P', 'Jerry Rice', 'Drew Lachey', 'Stacy Keibler']

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()

    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    for idx, celebrity in enumerate(key_celebs):
        ax = axes[idx]

        fan_weeks = []
        fan_means = []
        fan_stds = []
        judge_weeks = []
        judge_ranks = []

        for week in weeks:
            results_df = all_results[week]
            if results_df is not None and not results_df.empty:
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    fan_weeks.append(week)
                    fan_means.append(celeb_data['estimated_fan_rank_mean'].values[0])
                    fan_stds.append(celeb_data['estimated_fan_rank_std'].values[0])

            if week in all_judge_ranks and all_judge_ranks[week] is not None:
                judge_df = all_judge_ranks[week]
                celeb_judge = judge_df[judge_df['celebrity_name'] == celebrity]
                if not celeb_judge.empty:
                    judge_weeks.append(week)
                    judge_ranks.append(celeb_judge['judge_rank'].values[0])

        if len(fan_weeks) == 0 and len(judge_weeks) == 0:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                   fontsize=16, transform=ax.transAxes)
            ax.set_title(celebrity, fontsize=18, fontweight='bold')
            ax.axis('off')
            continue

        fan_means = np.array(fan_means)
        fan_stds = np.array(fan_stds)

        if len(judge_weeks) > 0:
            ax.plot(judge_weeks, judge_ranks,
                   color='#2E86AB', linestyle='--', label='Judge Rank',
                   linewidth=4.2, marker='s', markersize=11,
                   markeredgewidth=2.5, markeredgecolor='white', alpha=0.9)

        if len(fan_weeks) > 0:
            ax.plot(fan_weeks, fan_means,
                   color='#F77F00', linestyle='-', label='Est. Fan Rank',
                   linewidth=4.2, marker='o', markersize=11,
                   markeredgewidth=2.5, markeredgecolor='white', alpha=0.9)
            ax.fill_between(fan_weeks,
                           fan_means - fan_stds,
                           fan_means + fan_stds,
                           color='#F77F00', alpha=0.2)

        ax.set_title(celebrity, fontsize=22, fontweight='bold', pad=18)
        ax.set_xlabel('Week', fontsize=19, fontweight='bold')
        ax.set_ylabel('Rank', fontsize=19, fontweight='bold')
        ax.legend(loc='best', fontsize=16, framealpha=0.95, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
        ax.invert_yaxis()

    plt.suptitle('Case Studies: Judge vs. Fan Perspective',
                fontsize=28, fontweight='bold', y=0.995)
    plt.tight_layout()

    save_path = os.path.join(output_dir, 'S2_Case_Studies.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


# ============================================================================
# SECTION 5: VISUALIZATION - GAP ANALYSIS
# ============================================================================

def plot_s2_gap_analysis_bars(all_results, all_judge_ranks, output_dir):
    """Chart 3: Gap Analysis Bar Chart"""
    print("\n" + "="*70)
    print("Creating Chart 3: Gap Analysis Bar Chart...")
    print("="*70)

    if not all_results or not all_judge_ranks:
        print("No results to plot")
        return

    key_celebs = ['Master P', 'Jerry Rice', 'Drew Lachey', 'Stacy Keibler']

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()

    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    for idx, celebrity in enumerate(key_celebs):
        ax = axes[idx]

        gap_weeks = []
        gaps = []

        for week in weeks:
            judge_rank = None
            if week in all_judge_ranks and all_judge_ranks[week] is not None:
                judge_df = all_judge_ranks[week]
                celeb_judge = judge_df[judge_df['celebrity_name'] == celebrity]
                if not celeb_judge.empty:
                    judge_rank = celeb_judge['judge_rank'].values[0]

            fan_rank = None
            results_df = all_results[week]
            if results_df is not None and not results_df.empty:
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    fan_rank = celeb_data['estimated_fan_rank_mean'].values[0]

            if judge_rank is not None and fan_rank is not None:
                gap = judge_rank - fan_rank
                gap_weeks.append(week)
                gaps.append(gap)

        if len(gap_weeks) == 0:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                   fontsize=16, transform=ax.transAxes)
            ax.set_title(celebrity, fontsize=18, fontweight='bold')
            ax.axis('off')
            continue

        colors_bars = ['#E74C3C' if g > 0 else '#3498DB' for g in gaps]

        bars = ax.bar(gap_weeks, gaps, color=colors_bars, alpha=0.75,
                     edgecolor='black', linewidth=2.2, width=0.7)

        ax.axhspan(0, max(gaps) if len(gaps) > 0 and max(gaps) > 0 else 1,
                  alpha=0.1, color='red', zorder=0)
        ax.axhspan(min(gaps) if len(gaps) > 0 and min(gaps) < 0 else -1, 0,
                  alpha=0.1, color='blue', zorder=0)

        ax.axhline(y=0, color='black', linestyle='-', linewidth=2.5, zorder=5)

        for i, (week, gap) in enumerate(zip(gap_weeks, gaps)):
            label_y = gap + (0.15 if gap > 0 else -0.15)
            ax.text(week, label_y, f'{gap:+.2f}',
                   ha='center', va='bottom' if gap > 0 else 'top',
                   fontsize=11, fontweight='bold', family='serif')

        ax.set_title(celebrity, fontsize=22, fontweight='bold', pad=18)
        ax.set_xlabel('Week', fontsize=19, fontweight='bold')
        ax.set_ylabel('Rank Gap (Judge - Fan)', fontsize=19, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.8)

        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#E74C3C', alpha=0.75, label='Fan Saved (Gap > 0)'),
            Patch(facecolor='#3498DB', alpha=0.75, label='Fan Hurt (Gap < 0)')
        ]
        ax.legend(handles=legend_elements, loc='best', fontsize=14,
                 framealpha=0.95, fancybox=True, shadow=True)

    plt.suptitle('Judge-Fan Rank Gap Analysis',
                fontsize=28, fontweight='bold', y=0.995)
    plt.tight_layout()

    save_path = os.path.join(output_dir, 'S2_Gap_Analysis_Bars.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


# ============================================================================
# SECTION 6: Main Execution
# ============================================================================

def main():
    """Main execution with VOTE SHARE estimation"""
    print("="*70)
    print("DWTS Fan Vote Estimation - Season 2 with Vote Share (Zipf's Law)")
    print("="*70)

    output_dir = './output_results'
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {os.path.abspath(output_dir)}\n")

    filepath = r'C:\Users\tx\AppData\Roaming\Kingsoft\office6\templates\wps\zh_CN\2026_MCM_Problem_C_Data.csv'

    if not os.path.exists(filepath):
        print(f"ERROR: Data file not found at {filepath}")
        print(f"Current working directory: {os.getcwd()}")
        return

    df, max_week = load_and_preprocess_data(filepath)

    # ========================================================================
    # SEASON 2 ANALYSIS
    # ========================================================================
    print("\n" + "="*70)
    print("SEASON 2 ANALYSIS (With Tie-Breaker Logic)")
    print("="*70)

    season2_results = {}
    season2_judge_ranks = {}

    for week in range(1, 11):
        results_df, feasible_ranks, judge_ranks = analyze_season_week(
            df, 2, week, n_simulations=10000)
        if results_df is not None:
            season2_results[week] = results_df
        if judge_ranks is not None:
            season2_judge_ranks[week] = judge_ranks

    # ========================================================================
    # CALCULATE VOTE SHARES (NEW!)
    # ========================================================================

    vote_share_df = calculate_vote_share_zipf(season2_results)

    # ========================================================================
    # SAVE RESULTS
    # ========================================================================

    all_results = []
    for week_id, results_df in season2_results.items():
        if results_df is not None and not results_df.empty:
            results_df = results_df.copy()
            results_df['season'] = 2
            results_df['week'] = week_id
            all_results.append(results_df)

    if all_results:
        final_results = pd.concat(all_results, ignore_index=True)
        final_results['week'] = final_results['week'].astype(int)
        final_results = final_results.sort_values(['week', 'celebrity_name']).reset_index(drop=True)

        csv_path = os.path.join(output_dir, 'S2_fan_rank_estimates.csv')
        final_results.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

    # Save vote share data
    if not vote_share_df.empty:
        vote_csv_path = os.path.join(output_dir, 'S2_vote_share_estimates.csv')
        vote_share_df.to_csv(vote_csv_path, index=False)
        print(f"Vote share data saved to: {vote_csv_path}")

    # ========================================================================
    # CREATE VISUALIZATIONS
    # ========================================================================

    if season2_results:
        plot_s2_trajectories(season2_results, output_dir)
        plot_s2_heatmap(season2_results, df, output_dir)
        plot_s2_case_studies(season2_results, season2_judge_ranks, output_dir)
        plot_s2_gap_analysis_bars(season2_results, season2_judge_ranks, output_dir)

        # NEW: Vote share visualizations
        plot_vote_share_evolution(vote_share_df, output_dir)
        plot_vote_share_stacked_area(vote_share_df, output_dir)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE - Season 2 with Vote Share Estimation")
    print(f"All outputs saved to: {os.path.abspath(output_dir)}")
    print("="*70)
    print("\nGenerated files:")
    print("  - S2_fan_rank_estimates.csv")
    print("  - S2_vote_share_estimates.csv (NEW!)")
    print("  - S2_Trajectories.png")
    print("  - S2_Uncertainty_Heatmap.png")
    print("  - S2_Case_Studies.png")
    print("  - S2_Gap_Analysis_Bars.png")
    print("  - S2_Vote_Share_Evolution.png (NEW!)")
    print("  - S2_Vote_Share_Stacked.png (NEW!)")
    print("\n🏆 Complete with Zipf's Law Vote Share Estimation! 🏆")


if __name__ == "__main__":
    main()