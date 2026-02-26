"""
Monte Carlo Simulation for Fan Vote Estimation in DWTS - SEASON 27 ANALYSIS
-----------------------------------------------------------------------------
Demonstrating Model Generalization to Percentage Combination Method

PERCENTAGE COMBINATION METHOD (Season 3-27):
- Judge Percentage: Score_i / Σ(All Scores)
- Fan Percentage: Vote_i / Σ(All Votes)
  [Estimated using Zipf's Law: Vote ∝ 1/Rank]
- Total Score = Judge Percentage + Fan Percentage
- Lowest Total Score → Eliminated

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

# Set O-award publication-quality style
sns.set_style("whitegrid")
sns.set_context("talk")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 18
plt.rcParams['axes.titlesize'] = 26
plt.rcParams['axes.labelsize'] = 22
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18
plt.rcParams['legend.fontsize'] = 17
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']

# ============================================================================
# SECTION 1: Data Preprocessing
# ============================================================================

def load_and_preprocess_data(filepath, season=27):
    """Load DWTS data and extract specified season."""
    df = pd.read_csv(filepath)
    df_season = df[df['season'] == season].copy()

    week_cols = [col for col in df.columns if 'week' in col and 'judge' in col]
    max_week = max([int(col.split('_')[0].replace('week', '')) for col in week_cols])

    print(f"Season {season} loaded successfully")
    print(f"Maximum week number found: {max_week}")
    print(f"Total contestants in Season {season}: {len(df_season)}")

    return df_season, max_week


def extract_judge_scores_by_week(df, season, week):
    """
    Extract judge scores (RAW SCORES) for percentage-based system.
    Returns actual scores, not ranks.
    """
    season_data = df[df['season'] == season].copy()

    judge_cols = [col for col in df.columns
                  if col.startswith(f'week{week}_judge') and col.endswith('_score')]

    # Calculate total judge score
    season_data['judge_score_sum'] = season_data[judge_cols].sum(axis=1, skipna=True)

    # Filter active contestants (score > 0)
    active_contestants = season_data[season_data['judge_score_sum'] > 0].copy()

    return active_contestants[['celebrity_name', 'judge_score_sum']]


def get_eliminated_contestant(df, season, week):
    """
    Identify who was eliminated in a specific week.
    For finals week (4 people → 1st/2nd/3rd/4th), return complete rankings.

    Returns:
        eliminated_name (str): Name of eliminated contestant for regular weeks
        OR
        (eliminated_name, final_rankings) tuple for finals week
        where final_rankings = {name: placement} dict
    """
    season_data = df[df['season'] == season]

    # First, try to detect finals week and get complete rankings
    if week >= 9:  # Likely finals
        final_rankings = {}
        for idx, row in season_data.iterrows():
            celeb = row['celebrity_name']
            placement = row.get('placement', None)
            # For finals, we need top 4 placements
            if pd.notna(placement) and placement <= 4:
                final_rankings[celeb] = int(placement)

        # If we have complete top 4 rankings, return them
        if len(final_rankings) >= 4:
            fourth_place = [name for name, place in final_rankings.items() if place == 4]
            if fourth_place:
                print(f"  FINALS DETECTED: 4-person finale with complete rankings")
                print(f"  Rankings: {final_rankings}")
                return (fourth_place[0], final_rankings)

    # Standard elimination detection for non-finals weeks
    for idx, row in season_data.iterrows():
        result = str(row['results']).lower()

        # Standard elimination format
        if f'week {week}' in result or f'week{week}' in result:
            if 'eliminated' in result or 'elim' in result:
                return row['celebrity_name']

        # Check placement for finals (4th place in 4-person finale)
        if f'week {week}' in result or f'week{week}' in result:
            if '4th' in result or 'fourth' in result or '3rd' in result or 'third' in result:
                return row['celebrity_name']

        # Alternative format
        result_parts = result.split(',')
        for part in result_parts:
            if f'week {week}' in part or f'week{week}' in part:
                if 'elim' in part or '4th' in part or 'fourth' in part:
                    return row['celebrity_name']

    # Fallback: check placement column
    if week >= 9:
        if 'placement' in season_data.columns:
            # In 4-person finale, 4th place is "eliminated"
            fourth_place = season_data[season_data['placement'] == 4]
            if not fourth_place.empty:
                return fourth_place.iloc[0]['celebrity_name']

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
# SECTION 2: Monte Carlo Simulation - PERCENTAGE COMBINATION METHOD
# ============================================================================

def monte_carlo_simulation_finals(judge_scores, final_rankings, n_simulations=10000, week=None):
    """
    Monte Carlo simulation for FINALS WEEK with COMPLETE RANKING constraints.

    For Season 27 Week 9: 4 finalists competing for 1st/2nd/3rd/4th place.

    Instead of just constraining who gets eliminated (4th place), we constrain the
    entire ranking order (1st, 2nd, 3rd, 4th).

    Args:
        judge_scores: Judge scores for finalists (should be 4 people)
        final_rankings: Dict {name: placement}, e.g. {'Bobby': 1, 'Milo': 2, 'Evanna': 3, 'Alexis': 4}
        n_simulations: Number of simulations
        week: Week number

    Returns:
        Feasible fan ranks that produce the correct final ranking order
    """
    contestants = judge_scores['celebrity_name'].tolist()
    judge_score_dict = dict(zip(judge_scores['celebrity_name'],
                                judge_scores['judge_score_sum']))

    n_contestants = len(contestants)
    feasible_fan_ranks = []

    # Adaptive Zipf exponent
    if n_contestants >= 8:
        zipf_alpha = 1.0
    elif n_contestants >= 5:
        zipf_alpha = 1.3
    elif n_contestants >= 3:
        zipf_alpha = 1.8
    else:
        zipf_alpha = 2.0

    print(f"  FINALS MODE: Full ranking constraint")
    print(f"  Target rankings: {final_rankings}")
    print(f"  Adaptive Zipf exponent: α = {zipf_alpha:.1f}")

    # Calculate Judge Percentage
    total_judge_score = sum(judge_score_dict.values())
    judge_pct_dict = {c: score / total_judge_score
                      for c, score in judge_score_dict.items()}

    print(f"  Judge Percentages: {', '.join([f'{c}: {p*100:.1f}%' for c, p in judge_pct_dict.items()])}")
    print(f"  Running {n_simulations} simulations with full ranking constraint...")

    rank_assignments = [np.random.permutation(range(1, n_contestants + 1))
                       for _ in range(n_simulations)]

    test_counter = 0
    for fan_ranks in rank_assignments:
        test_counter += 1
        if test_counter % (n_simulations // 10) == 0:
            print(f"    Progress: {test_counter}/{n_simulations} ({100*test_counter/n_simulations:.1f}%)")

        # Calculate Fan Percentage using Enhanced Zipf
        fan_rank_dict = {contestants[i]: fan_ranks[i] for i in range(n_contestants)}
        zipf_scores = {c: 1.0 / (r ** zipf_alpha) for c, r in fan_rank_dict.items()}
        total_zipf = sum(zipf_scores.values())
        fan_pct_dict = {c: z / total_zipf for c, z in zipf_scores.items()}

        # Calculate Total Score
        total_scores = {c: judge_pct_dict[c] + fan_pct_dict[c]
                       for c in contestants}

        # Sort by total score (DESCENDING for percentage method - higher is better)
        sorted_contestants = sorted(total_scores.items(),
                                   key=lambda x: x[1], reverse=True)

        # Check if ranking matches target
        matches = True
        for rank_idx, (contestant, score) in enumerate(sorted_contestants):
            expected_placement = rank_idx + 1  # 1st, 2nd, 3rd
            actual_placement = final_rankings.get(contestant, None)

            if actual_placement != expected_placement:
                matches = False
                break

        if matches:
            feasible_fan_ranks.append(list(fan_ranks))

    print(f"  Found {len(feasible_fan_ranks)} feasible solutions with full ranking constraint")

    # Print example
    if len(feasible_fan_ranks) > 0:
        example_ranks = feasible_fan_ranks[0]
        example_dict = {contestants[i]: example_ranks[i] for i in range(n_contestants)}
        example_zipf = {c: 1.0 / (r ** zipf_alpha) for c, r in example_dict.items()}
        example_total_zipf = sum(example_zipf.values())
        example_fan_pct = {c: (z / example_total_zipf) * 100 for c, z in example_zipf.items()}

        print(f"\n  Example Solution (Finals):")
        for c in sorted(contestants, key=lambda x: final_rankings[x]):
            placement = final_rankings[c]
            print(f"    {placement}. {c}: Fan Rank {example_dict[c]:.2f} → {example_fan_pct[c]:.1f}% fan vote")

    return feasible_fan_ranks, contestants

def monte_carlo_simulation_percentage(judge_scores, eliminated_name, n_simulations=10000, week=None):
    """
    Monte Carlo simulation for PERCENTAGE COMBINATION METHOD (Season 3-27).
    
    Enhanced with ADAPTIVE ZIPF EXPONENT:
    - Regular weeks: Vote ∝ 1/Rank^1.0 (standard Zipf)
    - Finals weeks: Vote ∝ 1/Rank^1.8 (amplified to capture extreme polarization)
    
    Logic:
    1. Judge Percentage = Score_i / Σ(Scores)
    2. Fan Percentage = (1/Rank_i^α) / Σ(1/Rank^α)  [Enhanced Zipf's Law]
    3. Total Score = Judge Percentage + Fan Percentage
    4. Lowest Total Score → Eliminated
    5. Tie-breaker: Lower Fan Percentage → Eliminated
    """
    contestants = judge_scores['celebrity_name'].tolist()
    judge_score_dict = dict(zip(judge_scores['celebrity_name'],
                                judge_scores['judge_score_sum']))

    n_contestants = len(contestants)
    feasible_fan_ranks = []

    # ADAPTIVE ZIPF EXPONENT based on competition stage
    # More contestants → standard Zipf (α=1.0)
    # Fewer contestants (finals) → amplified Zipf (α=1.8)
    if n_contestants >= 8:
        zipf_alpha = 1.0  # Standard Zipf for early rounds
    elif n_contestants >= 5:
        zipf_alpha = 1.3  # Moderate amplification for mid-season
    elif n_contestants >= 3:
        zipf_alpha = 1.8  # Strong amplification for finals (3 people)
    else:
        zipf_alpha = 2.0  # Maximum amplification for final 2

    print(f"  Adaptive Zipf exponent: α = {zipf_alpha:.1f} ({n_contestants} contestants)")

    # Calculate Judge Percentage (normalized to sum = 1)
    total_judge_score = sum(judge_score_dict.values())
    judge_pct_dict = {c: score / total_judge_score
                      for c, score in judge_score_dict.items()}

    print(f"  Using percentage combination method with {n_simulations} simulations...")
    print(f"  Judge Percentages: {', '.join([f'{c}: {p*100:.1f}%' for c, p in judge_pct_dict.items()])}")

    rank_assignments = [np.random.permutation(range(1, n_contestants + 1))
                       for _ in range(n_simulations)]

    test_counter = 0
    for fan_ranks in rank_assignments:
        test_counter += 1
        if test_counter % (n_simulations // 10) == 0:
            print(f"    Progress: {test_counter}/{n_simulations} ({100*test_counter/n_simulations:.1f}%)")

        # Calculate Fan Percentage using ENHANCED Zipf's Law with exponent α
        fan_rank_dict = {contestants[i]: fan_ranks[i] for i in range(n_contestants)}

        # Enhanced Zipf: Vote ∝ 1/(Rank^α)
        zipf_scores = {c: 1.0 / (r ** zipf_alpha) for c, r in fan_rank_dict.items()}
        total_zipf = sum(zipf_scores.values())
        fan_pct_dict = {c: z / total_zipf for c, z in zipf_scores.items()}

        # Calculate Total Score (Judge % + Fan %)
        total_scores = {c: judge_pct_dict[c] + fan_pct_dict[c]
                       for c in contestants}

        # Find minimum total score (worst performer)
        min_total_score = min(total_scores.values())

        # Get all contestants with min total score (potential ties)
        tied_contestants = [c for c, s in total_scores.items() if s == min_total_score]

        # TIE-BREAKER: Lower Fan Percentage → Eliminated
        if len(tied_contestants) > 1:
            would_be_eliminated = min(tied_contestants, key=lambda c: fan_pct_dict[c])
        else:
            would_be_eliminated = tied_contestants[0]

        # Check if simulation matches historical elimination
        if would_be_eliminated == eliminated_name:
            feasible_fan_ranks.append(list(fan_ranks))

    print(f"  Found {len(feasible_fan_ranks)} feasible solutions")

    # Print example from first feasible solution to show the effect
    if len(feasible_fan_ranks) > 0:
        example_ranks = feasible_fan_ranks[0]
        example_dict = {contestants[i]: example_ranks[i] for i in range(n_contestants)}
        example_zipf = {c: 1.0 / (r ** zipf_alpha) for c, r in example_dict.items()}
        example_total_zipf = sum(example_zipf.values())
        example_fan_pct = {c: (z / example_total_zipf) * 100 for c, z in example_zipf.items()}

        print(f"\n  Example Fan Vote Distribution (with α={zipf_alpha}):")
        for c in sorted(contestants, key=lambda x: example_dict[x]):
            print(f"    {c}: Rank {example_dict[c]} → {example_fan_pct[c]:.1f}% fan vote")

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
    """Analyze a specific season and week with percentage combination method."""
    print(f"\n{'='*70}")
    print(f"Analyzing Season {season}, Week {week} (Percentage Combination)")
    print(f"{'='*70}")

    judge_scores = extract_judge_scores_by_week(df, season, week)

    if len(judge_scores) == 0:
        print(f"No active contestants found for Season {season} Week {week}")
        return None, None, None

    print(f"\nActive contestants: {len(judge_scores)}")
    print("\nJudge Scores:")
    print(judge_scores.to_string())

    # Special handling for week 9+ (finals) - print extra debug info
    if week >= 9:
        print(f"\n*** FINALS WEEK {week} - Special Detection ***")
        season_data = df[df['season'] == season]
        print("\nAll contestants and their results:")
        for idx, row in season_data.iterrows():
            print(f"  {row['celebrity_name']}: placement={row.get('placement', 'N/A')}, results={row.get('results', 'N/A')}")

    elimination_result = get_eliminated_contestant(df, season, week)

    # Check if this is finals week with complete rankings
    is_finals = False
    final_rankings = None
    eliminated_name = None

    if isinstance(elimination_result, tuple):
        # Finals week with complete rankings
        eliminated_name, final_rankings = elimination_result
        is_finals = True
        print(f"\n*** FINALS MODE: Using complete ranking constraint ***")
        print(f"Final Rankings: {final_rankings}")
    else:
        # Regular week with just elimination
        eliminated_name = elimination_result
        print(f"\nEliminated contestant: {eliminated_name}")

    if eliminated_name is None:
        print("WARNING: Could not identify eliminated contestant")
        print("Checking if this is a finals week with no elimination...")

        # For the actual final week (top 2), there's no elimination
        if len(judge_scores) == 2:
            print("This appears to be the FINAL week with only 2 contestants remaining.")
            print("Skipping elimination simulation (no one eliminated).")
            return None, None, judge_scores

        return None, None, judge_scores

    # Use appropriate simulation method
    if is_finals and final_rankings is not None:
        # Use complete ranking constraint for finals
        feasible_fan_ranks, contestants = monte_carlo_simulation_finals(
            judge_scores, final_rankings, n_simulations=n_simulations, week=week
        )
    else:
        # Use standard elimination constraint
        feasible_fan_ranks, contestants = monte_carlo_simulation_percentage(
            judge_scores, eliminated_name, n_simulations=n_simulations, week=week
        )

    if len(feasible_fan_ranks) == 0:
        return None, feasible_fan_ranks, judge_scores

    results_df = analyze_fan_ranks(feasible_fan_ranks, contestants)

    print("\nEstimated Fan Ranks:")
    print(results_df.to_string())

    return results_df, feasible_fan_ranks, judge_scores


# ============================================================================
# SECTION 3: ZIPF'S LAW VOTE SHARE CONVERSION
# ============================================================================

def calculate_vote_share_zipf(all_results):
    """
    Calculate estimated vote share percentage using ADAPTIVE Zipf's Law.
    Uses different exponents based on competition stage to better capture
    extreme fan mobilization in finals.
    """
    print("\n" + "="*70)
    print("Calculating Fan Vote Percentages using Adaptive Zipf's Law...")
    print("="*70)

    vote_share_data = []
    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    for week in weeks:
        results_df = all_results[week]
        if results_df is None or results_df.empty:
            continue

        contestants = results_df['celebrity_name'].tolist()
        fan_ranks = results_df['estimated_fan_rank_mean'].values
        n_contestants = len(contestants)

        # ADAPTIVE ZIPF EXPONENT based on number of contestants
        if n_contestants >= 8:
            zipf_alpha = 1.0  # Standard Zipf for early rounds
        elif n_contestants >= 5:
            zipf_alpha = 1.3  # Moderate amplification
        elif n_contestants >= 3:
            zipf_alpha = 1.8  # Strong amplification for finals
        else:
            zipf_alpha = 2.0  # Maximum amplification

        # Calculate Zipf scores with adaptive exponent
        zipf_scores = 1.0 / (fan_ranks ** zipf_alpha)
        total_zipf = zipf_scores.sum()
        vote_percentages = (zipf_scores / total_zipf) * 100

        for celeb, rank, pct in zip(contestants, fan_ranks, vote_percentages):
            vote_share_data.append({
                'week': week,
                'celebrity_name': celeb,
                'estimated_fan_rank': rank,
                'fan_vote_percentage': pct
            })

        print(f"\nWeek {week} Fan Vote Distribution (α={zipf_alpha}, {n_contestants} contestants):")
        week_df = pd.DataFrame({
            'Celebrity': contestants,
            'Fan Rank': fan_ranks,
            'Fan Vote %': vote_percentages
        })
        week_df = week_df.sort_values('Fan Vote %', ascending=False)
        print(week_df.to_string(index=False))

    return pd.DataFrame(vote_share_data)


# ============================================================================
# SECTION 4: VISUALIZATIONS
# ============================================================================

def plot_trajectories(all_results, season, output_dir):
    """Chart 1: Fan Rank Trajectories"""
    print(f"\nCreating Chart 1: Season {season} Fan Rank Trajectories...")

    if not all_results:
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
    ax.set_title(f'Season {season}: Fan Rank Evolution (Percentage Method)',
                fontsize=26, fontweight='bold', pad=25)
    ax.legend(loc='best', framealpha=0.95, fontsize=13, ncol=2,
             fancybox=True, shadow=True)
    ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
    ax.invert_yaxis()

    plt.tight_layout()
    save_path = os.path.join(output_dir, f'S{season}_Trajectories.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


def plot_heatmap(all_results, df, season, output_dir):
    """Chart 2: Uncertainty Heatmap"""
    print(f"\nCreating Chart 2: Season {season} Uncertainty Heatmap...")

    if not all_results:
        return

    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    all_celebrities = set()
    for week_num, results_df in all_results.items():
        if results_df is not None and not results_df.empty:
            all_celebrities.update(results_df['celebrity_name'].tolist())

    all_celebrities_sorted = sorted(list(all_celebrities))
    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    placement_dict = get_final_placement(df, season)
    all_celebrities_by_placement = sorted(
        all_celebrities_sorted,
        key=lambda x: placement_dict.get(x, 999)
    )

    heatmap_data = np.full((len(all_celebrities_by_placement), len(weeks)), np.nan)

    for week_idx, week_key in enumerate(weeks):
        results_df = all_results[week_key]
        if results_df is not None and not results_df.empty:
            for celeb_idx, celebrity in enumerate(all_celebrities_by_placement):
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    heatmap_data[celeb_idx, week_idx] = \
                        celeb_data['estimated_fan_rank_std'].values[0]

    sns.heatmap(heatmap_data,
                xticklabels=[f'Week {int(w)}' for w in weeks],
                yticklabels=all_celebrities_by_placement,
                cmap='YlOrRd', annot=True, fmt='.2f',
                cbar_kws={'label': 'Uncertainty (Std Dev)', 'shrink': 0.85},
                ax=ax, linewidths=1.8, linecolor='white',
                mask=np.isnan(heatmap_data), vmin=0,
                annot_kws={'fontsize': 13, 'fontweight': 'bold', 'family': 'serif'})

    ax.set_xlabel('Week Number', fontsize=22, fontweight='bold')
    ax.set_ylabel('Celebrity (Sorted by Final Placement)', fontsize=22, fontweight='bold')
    ax.set_title(f'Season {season}: Estimation Uncertainty Heatmap',
                fontsize=26, fontweight='bold', pad=25)

    plt.tight_layout()
    save_path = os.path.join(output_dir, f'S{season}_Uncertainty_Heatmap.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


def plot_vote_share_stacked(vote_share_df, season, output_dir):
    """Chart 3: Fan Vote Percentage Stacked Area"""
    print(f"\nCreating Chart 3: Season {season} Fan Vote Distribution...")

    if vote_share_df is None or vote_share_df.empty:
        return

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))

    pivot_df = vote_share_df.pivot(index='week',
                                    columns='celebrity_name',
                                    values='fan_vote_percentage')

    col_order = pivot_df.mean().sort_values(ascending=False).index
    pivot_df = pivot_df[col_order]

    pivot_df.plot(kind='area', stacked=True, ax=ax,
                 alpha=0.7, linewidth=2.5,
                 color=plt.cm.Set3(np.linspace(0, 1, len(pivot_df.columns))))

    ax.set_xlabel('Week Number', fontsize=22, fontweight='bold')
    ax.set_ylabel('Fan Vote Percentage (%)', fontsize=22, fontweight='bold')
    ax.set_title(f'Season {season}: Fan Vote Distribution (Adaptive Zipf\'s Law)\n' +
                'α = 1.0-1.8 based on contestants (higher α in finals)',
                fontsize=24, fontweight='bold', pad=25)
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
             framealpha=0.95, fontsize=13, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    ax.set_ylim([0, 100])

    plt.tight_layout()
    save_path = os.path.join(output_dir, f'S{season}_Vote_Percentage_Stacked.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


def plot_gap_analysis(all_results, all_judge_scores, season, output_dir):
    """Chart 4: Gap Analysis (Rank Gap for consistency)"""
    print(f"\nCreating Chart 4: Season {season} Gap Analysis...")

    if not all_results or not all_judge_scores:
        return

    # Get all contestants
    all_celebs = set()
    for results_df in all_results.values():
        if results_df is not None:
            all_celebs.update(results_df['celebrity_name'].tolist())

    # Select top 4 by final placement for display
    key_celebs = sorted(list(all_celebs))[:4] if len(all_celebs) >= 4 else list(all_celebs)

    n_celebs = len(key_celebs)
    n_cols = 2
    n_rows = int(np.ceil(n_celebs / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6*n_rows))
    if n_rows * n_cols > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    for idx, celebrity in enumerate(key_celebs):
        ax = axes[idx]

        gap_weeks = []
        gaps = []

        for week in weeks:
            # Calculate judge rank from scores
            judge_rank = None
            if week in all_judge_scores and all_judge_scores[week] is not None:
                judge_df = all_judge_scores[week].copy()
                judge_df['judge_rank'] = judge_df['judge_score_sum'].rank(ascending=False, method='min')
                celeb_judge = judge_df[judge_df['celebrity_name'] == celebrity]
                if not celeb_judge.empty:
                    judge_rank = celeb_judge['judge_rank'].values[0]

            # Get fan rank
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

        ax.bar(gap_weeks, gaps, color=colors_bars, alpha=0.75,
              edgecolor='black', linewidth=2.2, width=0.7)

        ax.axhspan(0, max(gaps) if gaps and max(gaps) > 0 else 1,
                  alpha=0.1, color='red', zorder=0)
        ax.axhspan(min(gaps) if gaps and min(gaps) < 0 else -1, 0,
                  alpha=0.1, color='blue', zorder=0)

        ax.axhline(y=0, color='black', linestyle='-', linewidth=2.5, zorder=5)

        for week, gap in zip(gap_weeks, gaps):
            label_y = gap + (0.15 if gap > 0 else -0.15)
            ax.text(week, label_y, f'{gap:+.2f}',
                   ha='center', va='bottom' if gap > 0 else 'top',
                   fontsize=11, fontweight='bold', family='serif')

        ax.set_title(celebrity, fontsize=20, fontweight='bold', pad=15)
        ax.set_xlabel('Week', fontsize=18, fontweight='bold')
        ax.set_ylabel('Rank Gap (Judge - Fan)', fontsize=18, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.8)

        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#E74C3C', alpha=0.75, label='Fan Saved (Gap > 0)'),
            Patch(facecolor='#3498DB', alpha=0.75, label='Fan Hurt (Gap < 0)')
        ]
        ax.legend(handles=legend_elements, loc='best', fontsize=13,
                 framealpha=0.95, fancybox=True, shadow=True)

    for idx in range(n_celebs, len(axes)):
        axes[idx].axis('off')

    plt.suptitle(f'Season {season}: Judge-Fan Rank Gap Analysis',
                fontsize=26, fontweight='bold', y=0.995)
    plt.tight_layout()

    save_path = os.path.join(output_dir, f'S{season}_Gap_Analysis.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


# ============================================================================
# SECTION 5: Main Execution
# ============================================================================

def main():
    """Main execution for Season 27 (Percentage Combination Method)"""
    print("="*70)
    print("DWTS Season 27 Analysis - Percentage Combination Method")
    print("Demonstrating Model Generalization")
    print("="*70)

    output_dir = './output_results_s27'
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {os.path.abspath(output_dir)}\n")

    filepath = '2026_MCM_Problem_C_Data.csv'

    if not os.path.exists(filepath):
        print(f"ERROR: Data file not found at {filepath}")
        print(f"Please update the filepath in the code.")
        return

    season = 27
    df, max_week = load_and_preprocess_data(filepath, season=season)

    # ========================================================================
    # DATA INSPECTION: Check which weeks have data
    # ========================================================================
    print("\n" + "="*70)
    print("DATA INSPECTION: Checking available weeks")
    print("="*70)

    season_data = df[df['season'] == season]
    for week in range(1, 13):
        week_cols = [col for col in df.columns
                    if col.startswith(f'week{week}_judge') and col.endswith('_score')]
        if week_cols:
            season_data_week = season_data.copy()
            season_data_week['week_sum'] = season_data_week[week_cols].sum(axis=1, skipna=True)
            active = season_data_week[season_data_week['week_sum'] > 0]
            if len(active) > 0:
                print(f"Week {week}: {len(active)} contestants with scores")
                print(f"  Contestants: {', '.join(active['celebrity_name'].tolist())}")

    # ========================================================================
    # SEASON 27 ANALYSIS
    # ========================================================================
    print("\n" + "="*70)
    print(f"SEASON {season} ANALYSIS (Percentage Combination Method)")
    print("="*70)

    season_results = {}
    season_judge_scores = {}

    # Analyze available weeks (Season 27 typically has 10-11 weeks)
    # Extended range to ensure we capture finals (week 9-10)
    for week in range(1, 13):
        results_df, feasible_ranks, judge_scores = analyze_season_week(
            df, season, week, n_simulations=10000)
        if results_df is not None:
            season_results[week] = results_df
        if judge_scores is not None:
            season_judge_scores[week] = judge_scores

    # Print summary of which weeks were successfully analyzed
    print("\n" + "="*70)
    print("Week Analysis Summary:")
    print("="*70)
    analyzed_weeks = sorted([k for k in season_results.keys() if season_results[k] is not None])
    print(f"Successfully analyzed weeks: {analyzed_weeks}")
    print(f"Total weeks analyzed: {len(analyzed_weeks)}")

    # ========================================================================
    # CALCULATE VOTE PERCENTAGES
    # ========================================================================

    vote_share_df = calculate_vote_share_zipf(season_results)

    # ========================================================================
    # SAVE RESULTS
    # ========================================================================

    all_results = []
    for week_id, results_df in season_results.items():
        if results_df is not None and not results_df.empty:
            results_df = results_df.copy()
            results_df['season'] = season
            results_df['week'] = week_id
            all_results.append(results_df)

    if all_results:
        final_results = pd.concat(all_results, ignore_index=True)
        final_results['week'] = final_results['week'].astype(int)
        final_results = final_results.sort_values(['week', 'celebrity_name']).reset_index(drop=True)

        csv_path = os.path.join(output_dir, f'S{season}_fan_rank_estimates.csv')
        final_results.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

    if not vote_share_df.empty:
        vote_csv_path = os.path.join(output_dir, f'S{season}_fan_vote_percentages.csv')
        vote_share_df.to_csv(vote_csv_path, index=False)
        print(f"Fan vote percentages saved to: {vote_csv_path}")

    # ========================================================================
    # CREATE VISUALIZATIONS
    # ========================================================================

    if season_results:
        plot_trajectories(season_results, season, output_dir)
        plot_heatmap(season_results, df, season, output_dir)
        plot_vote_share_stacked(vote_share_df, season, output_dir)
        plot_gap_analysis(season_results, season_judge_scores, season, output_dir)

    print("\n" + "="*70)
    print(f"ANALYSIS COMPLETE - Season {season} (Percentage Combination)")
    print(f"All outputs saved to: {os.path.abspath(output_dir)}")
    print("="*70)
    print("\nGenerated files:")
    print(f"  - S{season}_fan_rank_estimates.csv")
    print(f"  - S{season}_fan_vote_percentages.csv")
    print(f"  - S{season}_Trajectories.png")
    print(f"  - S{season}_Uncertainty_Heatmap.png")
    print(f"  - S{season}_Vote_Percentage_Stacked.png")
    print(f"  - S{season}_Gap_Analysis.png")
    print("\n🎯 Model Generalization to Percentage Method Demonstrated! 🎯")


if __name__ == "__main__":
    main()