"""
Monte Carlo Simulation for Fan Vote Estimation in DWTS - SEASON 28 ANALYSIS
-----------------------------------------------------------------------------
Rank Sum Method with Judges' Save Mechanism

SEASON 28 SYSTEM:
- Total Rank = Judge Rank + Fan Rank (like Season 2)
- NEW: Bottom Two contestants enter elimination zone
- NEW: Judges' Save - judges save the one with BETTER judge rank
- The one with WORSE judge rank gets eliminated

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

def load_and_preprocess_data(filepath, season=28):
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
    """
    Identify who was eliminated AND who withdrew in a specific week.
    For finals week (Week 11), also return complete rankings if available.

    Returns:
        eliminated_name (str): Name of eliminated contestant
        OR
        (eliminated_name, withdrawn_names) tuple if there are withdrawals
        OR
        (eliminated_name, final_rankings) tuple for finals week
    """
    season_data = df[df['season'] == season]

    # Check for finals week first (Week 11 with top 4)
    if week >= 11:
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

    eliminated_name = None
    withdrawn_names = []

    for idx, row in season_data.iterrows():
        result = str(row['results']).lower()
        celeb = row['celebrity_name']

        # Check for withdrawal/quit
        if f'week {week}' in result or f'week{week}' in result:
            if 'withdraw' in result or 'withdrew' in result or 'quit' in result:
                withdrawn_names.append(celeb)
                print(f"  Detected WITHDRAWAL: {celeb}")
                continue  # Don't count as eliminated

        # Check for normal elimination
        if f'week {week}' in result or f'week{week}' in result:
            if 'eliminated' in result or 'elim' in result:
                eliminated_name = celeb

    # Return appropriate format
    if len(withdrawn_names) > 0:
        return (eliminated_name, withdrawn_names)
    else:
        return eliminated_name


def get_withdrawn_contestants(df, season, week):
    """
    Separate function to get list of withdrawn contestants for a specific week.
    Used for data cleaning before simulation.
    """
    season_data = df[df['season'] == season]
    withdrawn = []

    for idx, row in season_data.iterrows():
        result = str(row['results']).lower()
        if f'week {week}' in result or f'week{week}' in result:
            if 'withdraw' in result or 'withdrew' in result or 'quit' in result:
                withdrawn.append(row['celebrity_name'])

    return withdrawn


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
# SECTION 2: Monte Carlo Simulation with JUDGES' SAVE (Season 28)
# ============================================================================

def monte_carlo_simulation_finals(judge_ranks, final_rankings, n_simulations=10000):
    """
    Monte Carlo simulation for FINALS WEEK (Week 11) with complete ranking constraints.

    For Season 28 finals: 4 contestants competing for 1st/2nd/3rd/4th place.
    Different from regular weeks - we need to match the ENTIRE ranking order.

    Args:
        judge_ranks: Judge scores for 4 finalists
        final_rankings: Dict {name: placement}, e.g. {'Hannah': 1, 'Ally': 2, ...}
        n_simulations: Number of simulations

    Returns:
        Feasible fan ranks that produce the correct final ranking order
    """
    contestants = judge_ranks['celebrity_name'].tolist()
    judge_rank_dict = dict(zip(judge_ranks['celebrity_name'],
                               judge_ranks['judge_rank']))

    n_contestants = len(contestants)
    feasible_fan_ranks = []

    print(f"  FINALS MODE: Complete ranking constraint (4 finalists)")
    print(f"  Target rankings: {final_rankings}")
    print(f"  Running {n_simulations} simulations...")

    rank_assignments = [np.random.permutation(range(1, n_contestants + 1))
                       for _ in range(n_simulations)]

    test_counter = 0
    for fan_ranks in rank_assignments:
        test_counter += 1
        if test_counter % (n_simulations // 10) == 0:
            print(f"    Progress: {test_counter}/{n_simulations} ({100*test_counter/n_simulations:.1f}%)")

        # Calculate Total Rank for finals
        fan_rank_dict = {contestants[i]: fan_ranks[i] for i in range(n_contestants)}
        total_ranks = {c: judge_rank_dict[c] + fan_rank_dict[c]
                      for c in contestants}

        # Sort by total rank (ASCENDING - lower is better in rank sum)
        sorted_contestants = sorted(total_ranks.items(), key=lambda x: x[1])

        # Check if ranking matches target
        matches = True
        for rank_idx, (contestant, score) in enumerate(sorted_contestants):
            expected_placement = rank_idx + 1  # 1st, 2nd, 3rd, 4th
            actual_placement = final_rankings.get(contestant, None)

            if actual_placement != expected_placement:
                matches = False
                break

        if matches:
            feasible_fan_ranks.append(list(fan_ranks))

    print(f"  Found {len(feasible_fan_ranks)} feasible solutions (finals)")

    # Print example
    if len(feasible_fan_ranks) > 0:
        example_ranks = feasible_fan_ranks[0]
        example_dict = {contestants[i]: example_ranks[i] for i in range(n_contestants)}

        print(f"\n  Example Solution (Finals):")
        for c in sorted(contestants, key=lambda x: final_rankings[x]):
            placement = final_rankings[c]
            judge_r = judge_rank_dict[c]
            fan_r = example_dict[c]
            total = judge_r + fan_r
            print(f"    {placement}. {c}: Judge Rank {judge_r}, Fan Rank {fan_r:.1f}, Total {total:.1f}")

    return feasible_fan_ranks, contestants


def monte_carlo_simulation_judges_save(judge_ranks, eliminated_name, n_simulations=10000):
    """
    Monte Carlo simulation for SEASON 28 with JUDGES' SAVE mechanism.

    IMPORTANT: This function works on ACTIVE contestants only.
    Withdrawn contestants should be filtered out BEFORE calling this function.

    New Logic:
    1. Calculate Total Rank = Judge Rank + Fan Rank (for ACTIVE contestants)
    2. Identify BOTTOM TWO contestants (highest total ranks)
    3. JUDGES' SAVE: Among bottom two, judge saves the one with BETTER judge rank
    4. The one with WORSE judge rank gets eliminated
    5. Check if eliminated person matches history

    Example:
    - Contestant A: Judge Rank 4, Fan Rank 6 → Total 10 (bottom 2)
    - Contestant B: Judge Rank 5, Fan Rank 4 → Total 9 (bottom 2)
    - Judges save A (better judge rank 4 < 5)
    - B gets eliminated (despite having better total rank!)

    Args:
        judge_ranks: DataFrame with ACTIVE contestants only (withdrawn removed)
        eliminated_name: Name of contestant who was eliminated (must be in active list)
        n_simulations: Number of Monte Carlo simulations

    Returns:
        feasible_fan_ranks: List of feasible fan rank assignments
        contestants: List of active contestant names
    """
    contestants = judge_ranks['celebrity_name'].tolist()
    judge_rank_dict = dict(zip(judge_ranks['celebrity_name'],
                               judge_ranks['judge_rank']))

    n_contestants = len(contestants)
    feasible_fan_ranks = []

    print(f"  Season 28 with Judges' Save: {n_simulations} simulations...")
    print(f"  Active contestants in simulation: {n_contestants}")
    print(f"  Judge Ranks: {', '.join([f'{c}: {r}' for c, r in judge_rank_dict.items()])}")

    rank_assignments = [np.random.permutation(range(1, n_contestants + 1))
                       for _ in range(n_simulations)]

    test_counter = 0
    for fan_ranks in rank_assignments:
        test_counter += 1
        if test_counter % (n_simulations // 10) == 0:
            print(f"    Progress: {test_counter}/{n_simulations} ({100*test_counter/n_simulations:.1f}%)")

        # Step 1: Calculate Total Rank
        fan_rank_dict = {contestants[i]: fan_ranks[i] for i in range(n_contestants)}
        total_ranks = {c: judge_rank_dict[c] + fan_rank_dict[c]
                      for c in contestants}

        # Step 2: Identify Bottom Two (highest total ranks)
        sorted_by_total = sorted(total_ranks.items(), key=lambda x: x[1], reverse=True)

        # Get the worst two (or more if there are ties)
        worst_total_rank = sorted_by_total[0][1]
        second_worst_total_rank = sorted_by_total[1][1] if len(sorted_by_total) > 1 else worst_total_rank

        bottom_zone = []
        for contestant, total_rank in sorted_by_total:
            if total_rank == worst_total_rank or total_rank == second_worst_total_rank:
                bottom_zone.append(contestant)
            if len(bottom_zone) >= 2 and total_rank < second_worst_total_rank:
                break

        # Ensure we have at least 2 in bottom zone
        if len(bottom_zone) < 2:
            bottom_zone = [c for c, _ in sorted_by_total[:2]]

        # Step 3: Judges' Save - eliminate the one with WORSE judge rank
        # Among bottom zone, find who has the worst judge rank (highest number)
        worst_judge_rank_in_zone = max([judge_rank_dict[c] for c in bottom_zone])
        candidates_for_elimination = [c for c in bottom_zone
                                      if judge_rank_dict[c] == worst_judge_rank_in_zone]

        # If multiple people tied for worst judge rank, pick the one with worse total rank
        if len(candidates_for_elimination) > 1:
            would_be_eliminated = max(candidates_for_elimination,
                                     key=lambda c: total_ranks[c])
        else:
            would_be_eliminated = candidates_for_elimination[0]

        # Step 4: Check if simulation matches historical elimination
        if would_be_eliminated == eliminated_name:
            feasible_fan_ranks.append(list(fan_ranks))

    print(f"  Found {len(feasible_fan_ranks)} feasible solutions (with Judges' Save)")

    # Print example to show the mechanism
    if len(feasible_fan_ranks) > 0:
        example_ranks = feasible_fan_ranks[0]
        example_fan_dict = {contestants[i]: example_ranks[i] for i in range(n_contestants)}
        example_total = {c: judge_rank_dict[c] + example_fan_dict[c] for c in contestants}

        print(f"\n  Example showing Judges' Save mechanism:")
        sorted_example = sorted(example_total.items(), key=lambda x: x[1], reverse=True)
        for i, (c, total) in enumerate(sorted_example[:min(3, len(sorted_example))]):
            marker = " ← ELIMINATED" if c == eliminated_name else ""
            print(f"    {c}: Judge Rank {judge_rank_dict[c]}, Fan Rank {example_fan_dict[c]:.1f}, Total {total:.1f}{marker}")

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
    """
    Analyze a specific season and week with Judges' Save.

    NEW: Handles weeks with NO elimination (like Week 1, Week 5)
    NEW: Handles mixed situations where someone withdraws AND someone is eliminated.
    NEW: Handles finals week (Week 11) with complete 1-4 rankings.

    Process:
    1. Extract all contestants with judge scores
    2. Identify withdrawn contestants
    3. Remove withdrawn contestants from active list
    4. Check if there's an elimination this week
    5. If NO elimination, just return the active list (no simulation needed)
    6. If elimination exists, run simulation
    """
    print(f"\n{'='*70}")
    print(f"Analyzing Season {season}, Week {week} (Rank Sum + Judges' Save)")
    print(f"{'='*70}")

    # Step 1: Extract all contestants with judge scores
    judge_scores_all = extract_judge_scores_by_week(df, season, week)

    if len(judge_scores_all) == 0:
        print(f"No active contestants found for Season {season} Week {week}")
        return None, None, None

    print(f"\nTotal contestants with scores: {len(judge_scores_all)}")
    print("\nAll Judge Scores and Ranks:")
    print(judge_scores_all.to_string())

    # Step 2: Identify withdrawn contestants
    withdrawn_contestants = get_withdrawn_contestants(df, season, week)

    if len(withdrawn_contestants) > 0:
        print(f"\n*** WITHDRAWAL DETECTED ***")
        print(f"Withdrawn contestants: {', '.join(withdrawn_contestants)}")
        print(f"These contestants will be removed from ranking calculation.")

    # Step 3: Clean contestant list (remove withdrawn)
    judge_scores_active = judge_scores_all[
        ~judge_scores_all['celebrity_name'].isin(withdrawn_contestants)
    ].copy()

    # Recalculate ranks after removing withdrawn contestants
    if len(judge_scores_active) > 0:
        judge_scores_active['judge_rank'] = judge_scores_active['judge_score_sum'].rank(
            ascending=False, method='min'
        )

    print(f"\n*** ACTIVE CONTESTANTS (after removing withdrawn) ***")
    print(f"Active contestants: {len(judge_scores_active)}")
    print("\nActive Contestants - Judge Scores and Ranks:")
    print(judge_scores_active.to_string())

    # Step 4: Identify eliminated contestant or finals rankings
    elimination_result = get_eliminated_contestant(df, season, week)

    # Parse result - check if it's finals with complete rankings
    is_finals = False
    final_rankings = None
    eliminated_name = None

    if isinstance(elimination_result, tuple) and len(elimination_result) == 2:
        # Could be (eliminated, withdrawn) or (eliminated, final_rankings)
        first, second = elimination_result
        if isinstance(second, dict):
            # It's finals with complete rankings
            eliminated_name = first
            final_rankings = second
            is_finals = True
            print(f"\n*** FINALS MODE: Complete ranking constraint ***")
            print(f"Final Rankings: {final_rankings}")
        elif isinstance(second, list):
            # It's (eliminated, withdrawn list)
            eliminated_name = first
    else:
        eliminated_name = elimination_result

    print(f"\nEliminated contestant (from active list): {eliminated_name}")

    # NEW: Handle weeks with NO elimination (like Week 1, Week 5)
    if eliminated_name is None:
        print("*** NO ELIMINATION THIS WEEK ***")
        print("This is a non-elimination week (e.g., Week 1, team week, etc.)")
        print("Returning active contestants without simulation.")

        # For non-elimination weeks, we cannot estimate fan ranks
        # But we return the judge scores so the week appears in visualizations
        return None, None, judge_scores_active

    # Verify eliminated person is in active list
    if eliminated_name not in judge_scores_active['celebrity_name'].values:
        print(f"ERROR: Eliminated contestant {eliminated_name} not in active list!")
        print("This might be a data issue or the contestant withdrew.")
        return None, None, judge_scores_active

    # Step 5: Run appropriate simulation (only if there's elimination)
    if is_finals and final_rankings is not None and len(final_rankings) >= 4:
        # Use finals simulation with complete ranking constraint
        feasible_fan_ranks, contestants = monte_carlo_simulation_finals(
            judge_scores_active, final_rankings, n_simulations=n_simulations
        )
    else:
        # Use standard Judges' Save simulation
        feasible_fan_ranks, contestants = monte_carlo_simulation_judges_save(
            judge_scores_active, eliminated_name, n_simulations=n_simulations
        )

    if len(feasible_fan_ranks) == 0:
        return None, feasible_fan_ranks, judge_scores_active

    results_df = analyze_fan_ranks(feasible_fan_ranks, contestants)

    print("\nEstimated Fan Ranks (Active Contestants Only):")
    print(results_df.to_string())

    return results_df, feasible_fan_ranks, judge_scores_active


# ============================================================================
# SECTION 3: ZIPF'S LAW VOTE SHARE CONVERSION
# ============================================================================

def calculate_vote_share_zipf(all_results):
    """
    Calculate estimated vote share using Zipf's Law.
    Even though S28 uses rank sum, we convert to percentages for visualization.
    """
    print("\n" + "="*70)
    print("Calculating Vote Shares using Zipf's Law (for visualization)...")
    print("="*70)

    vote_share_data = []
    weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    for week in weeks:
        results_df = all_results[week]
        if results_df is None or results_df.empty:
            continue

        contestants = results_df['celebrity_name'].tolist()
        fan_ranks = results_df['estimated_fan_rank_mean'].values

        # Calculate Zipf scores
        zipf_scores = 1.0 / fan_ranks
        total_zipf = zipf_scores.sum()
        vote_shares = (zipf_scores / total_zipf) * 100

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
# SECTION 4: VISUALIZATIONS
# ============================================================================

def plot_trajectories_merged(all_results, all_judge_ranks, season, week_labels, output_dir):
    """
    Chart 1: Fan Rank Trajectories with Merged Weeks

    Args:
        week_labels: Dict mapping display_week to label string (e.g., {1: "1-2", 3: "3", 5: "5-6"})
    """
    print(f"\nCreating Chart 1: Season {season} Trajectories (Merged Weeks)...")

    if not all_results:
        print("No results to plot")
        return

    fig, ax = plt.subplots(1, 1, figsize=(16, 9))

    # Collect all celebrities
    all_celebrities = set()
    for week_num, results_df in all_results.items():
        if results_df is not None and not results_df.empty:
            all_celebrities.update(results_df['celebrity_name'].tolist())

    all_celebrities_sorted = sorted(list(all_celebrities))
    display_weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    print(f"Display weeks: {display_weeks}")
    print(f"Week labels: {week_labels}")

    # Create color palette
    n_celebs = len(all_celebrities_sorted)
    colors = plt.cm.Set3(np.linspace(0, 1, 12)) if n_celebs <= 12 else plt.cm.tab20(np.linspace(0, 1, 20))
    celeb_colors = {celeb: colors[i % len(colors)] for i, celeb in enumerate(all_celebrities_sorted)}

    # For each celebrity, plot their trajectory
    for celebrity in all_celebrities_sorted:
        trajectory_weeks = []
        trajectory_means = []
        trajectory_stds = []

        # Collect data for this celebrity
        for week in display_weeks:
            results_df = all_results[week]
            if results_df is not None and not results_df.empty:
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    trajectory_weeks.append(week)
                    trajectory_means.append(celeb_data['estimated_fan_rank_mean'].values[0])
                    trajectory_stds.append(celeb_data['estimated_fan_rank_std'].values[0])

        if len(trajectory_weeks) == 0:
            continue

        trajectory_means = np.array(trajectory_means)
        trajectory_stds = np.array(trajectory_stds)
        color = celeb_colors[celebrity]

        # Plot trajectory line
        ax.plot(trajectory_weeks, trajectory_means,
               label=celebrity, color=color, alpha=0.85, linewidth=3.2,
               marker='o', markersize=10, zorder=10, markeredgewidth=2.2,
               markeredgecolor='white')

        # Plot uncertainty band
        ax.fill_between(trajectory_weeks,
                       trajectory_means - trajectory_stds,
                       trajectory_means + trajectory_stds,
                       color=color, alpha=0.15, zorder=5)

        # Mark elimination at LAST week
        if len(trajectory_weeks) > 0:
            last_week = trajectory_weeks[-1]
            final_week = max(display_weeks)

            if last_week < final_week:
                elim_idx = len(trajectory_weeks) - 1
                ax.plot(trajectory_weeks[elim_idx], trajectory_means[elim_idx],
                       'X', color='darkred', markersize=22, markeredgewidth=3,
                       markeredgecolor='white', zorder=20)
                print(f"  Marking elimination: {celebrity} at Display Week {last_week} ({week_labels[last_week]})")

    ax.set_xlabel('Week Period', fontsize=22, fontweight='bold')
    ax.set_ylabel('Estimated Fan Rank', fontsize=22, fontweight='bold')
    ax.set_title(f'Season {season}: Fan Rank Evolution (Rank Sum + Judges\' Save)',
                fontsize=24, fontweight='bold', pad=25)
    ax.legend(loc='best', framealpha=0.95, fontsize=12, ncol=2,
             fancybox=True, shadow=True)
    ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
    ax.invert_yaxis()

    # Set custom X-axis labels
    ax.set_xticks(display_weeks)
    ax.set_xticklabels([week_labels.get(w, str(w)) for w in display_weeks])
    ax.set_xlim(min(display_weeks) - 0.5, max(display_weeks) + 0.5)

    plt.tight_layout()
    save_path = os.path.join(output_dir, f'S{season}_Trajectories.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


def plot_heatmap_merged(all_results, df, season, week_labels, output_dir):
    """Chart 2: Uncertainty Heatmap with Merged Weeks"""
    print(f"\nCreating Chart 2: Season {season} Uncertainty Heatmap (Merged)...")

    if not all_results:
        return

    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    all_celebrities = set()
    for week_num, results_df in all_results.items():
        if results_df is not None and not results_df.empty:
            all_celebrities.update(results_df['celebrity_name'].tolist())

    all_celebrities_sorted = sorted(list(all_celebrities))
    display_weeks = sorted([k for k in all_results.keys() if all_results[k] is not None])

    placement_dict = get_final_placement(df, season)
    all_celebrities_by_placement = sorted(
        all_celebrities_sorted,
        key=lambda x: placement_dict.get(x, 999)
    )

    heatmap_data = np.full((len(all_celebrities_by_placement), len(display_weeks)), np.nan)

    for week_idx, week_key in enumerate(display_weeks):
        results_df = all_results[week_key]
        if results_df is not None and not results_df.empty:
            for celeb_idx, celebrity in enumerate(all_celebrities_by_placement):
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    heatmap_data[celeb_idx, week_idx] = \
                        celeb_data['estimated_fan_rank_std'].values[0]

    # Custom X-axis labels
    x_labels = [week_labels.get(w, str(w)) for w in display_weeks]

    sns.heatmap(heatmap_data,
                xticklabels=x_labels,
                yticklabels=all_celebrities_by_placement,
                cmap='YlOrRd', annot=True, fmt='.2f',
                cbar_kws={'label': 'Uncertainty (Std Dev)', 'shrink': 0.85},
                ax=ax, linewidths=1.8, linecolor='white',
                mask=np.isnan(heatmap_data), vmin=0,
                annot_kws={'fontsize': 13, 'fontweight': 'bold', 'family': 'serif'})

    ax.set_xlabel('Week Period', fontsize=22, fontweight='bold')
    ax.set_ylabel('Celebrity (Sorted by Final Placement)', fontsize=22, fontweight='bold')
    ax.set_title(f'Season {season}: Estimation Uncertainty Heatmap',
                fontsize=26, fontweight='bold', pad=25)

    plt.tight_layout()
    save_path = os.path.join(output_dir, f'S{season}_Uncertainty_Heatmap.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


def plot_trajectories(all_results, all_judge_ranks, season, output_dir):
    """
    Chart 1: Fan Rank Trajectories

    NEW: Uses all_judge_ranks to determine which weeks exist (including non-elimination weeks)
    """
    print(f"\nCreating Chart 1: Season {season} Trajectories...")

    if not all_results and not all_judge_ranks:
        print("No results to plot")
        return

    fig, ax = plt.subplots(1, 1, figsize=(14, 9))

    # Collect all celebrities who appeared in any week
    all_celebrities = set()
    for week_num, results_df in all_results.items():
        if results_df is not None and not results_df.empty:
            all_celebrities.update(results_df['celebrity_name'].tolist())

    all_celebrities_sorted = sorted(list(all_celebrities))
    weeks_with_fan_data = sorted([k for k in all_results.keys() if all_results[k] is not None])

    # CRITICAL: Use judge_ranks to determine ALL weeks (including non-elimination)
    all_weeks_available = sorted([k for k in all_judge_ranks.keys() if all_judge_ranks[k] is not None])

    if not all_weeks_available:
        print("No weeks with data found")
        return

    min_week = min(all_weeks_available)
    max_week = max(all_weeks_available)
    all_weeks = list(range(min_week, max_week + 1))

    print(f"All weeks with judge data: {all_weeks_available}")
    print(f"Weeks with fan rank estimates: {weeks_with_fan_data}")
    print(f"Plotting X-axis: {all_weeks}")

    # Create color palette
    n_celebs = len(all_celebrities_sorted)
    colors = plt.cm.Set3(np.linspace(0, 1, 12)) if n_celebs <= 12 else plt.cm.tab20(np.linspace(0, 1, 20))
    celeb_colors = {celeb: colors[i % len(colors)] for i, celeb in enumerate(all_celebrities_sorted)}

    # For each celebrity, plot their trajectory
    for celebrity in all_celebrities_sorted:
        trajectory_weeks = []
        trajectory_means = []
        trajectory_stds = []

        # Only collect weeks with FAN RANK data
        for week in weeks_with_fan_data:
            results_df = all_results[week]
            if results_df is not None and not results_df.empty:
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    trajectory_weeks.append(week)
                    trajectory_means.append(celeb_data['estimated_fan_rank_mean'].values[0])
                    trajectory_stds.append(celeb_data['estimated_fan_rank_std'].values[0])

        if len(trajectory_weeks) == 0:
            continue

        trajectory_means = np.array(trajectory_means)
        trajectory_stds = np.array(trajectory_stds)
        color = celeb_colors[celebrity]

        # Plot trajectory line
        ax.plot(trajectory_weeks, trajectory_means,
               label=celebrity, color=color, alpha=0.85, linewidth=3.2,
               marker='o', markersize=10, zorder=10, markeredgewidth=2.2,
               markeredgecolor='white')

        # Plot uncertainty band
        ax.fill_between(trajectory_weeks,
                       trajectory_means - trajectory_stds,
                       trajectory_means + trajectory_stds,
                       color=color, alpha=0.15, zorder=5)

        # Mark elimination at LAST week this person appeared (in fan data)
        if len(trajectory_weeks) > 0:
            last_week_with_data = trajectory_weeks[-1]
            final_week = max(weeks_with_fan_data)

            # If last appearance < final week, they were eliminated
            if last_week_with_data < final_week:
                elim_idx = len(trajectory_weeks) - 1
                ax.plot(trajectory_weeks[elim_idx], trajectory_means[elim_idx],
                       'X', color='darkred', markersize=22, markeredgewidth=3,
                       markeredgecolor='white', zorder=20)
                print(f"  Marking elimination: {celebrity} at Week {last_week_with_data}")

    ax.set_xlabel('Week Number', fontsize=22, fontweight='bold')
    ax.set_ylabel('Estimated Fan Rank', fontsize=22, fontweight='bold')
    ax.set_title(f'Season {season}: Fan Rank Evolution (Rank Sum + Judges\' Save)',
                fontsize=24, fontweight='bold', pad=25)
    ax.legend(loc='best', framealpha=0.95, fontsize=13, ncol=2,
             fancybox=True, shadow=True)
    ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.8)
    ax.invert_yaxis()

    # Show ALL weeks on X-axis (including Week 1)
    ax.set_xlim(min_week - 0.5, max_week + 0.5)
    ax.set_xticks(all_weeks)

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
    """Chart 3: Vote Share Stacked Area"""
    print(f"\nCreating Chart 3: Season {season} Vote Share Distribution...")

    if vote_share_df is None or vote_share_df.empty:
        return

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))

    pivot_df = vote_share_df.pivot(index='week',
                                    columns='celebrity_name',
                                    values='vote_share_percent')

    col_order = pivot_df.mean().sort_values(ascending=False).index
    pivot_df = pivot_df[col_order]

    pivot_df.plot(kind='area', stacked=True, ax=ax,
                 alpha=0.7, linewidth=2.5,
                 color=plt.cm.Set3(np.linspace(0, 1, len(pivot_df.columns))))

    ax.set_xlabel('Week Number', fontsize=22, fontweight='bold')
    ax.set_ylabel('Vote Share (%)', fontsize=22, fontweight='bold')
    ax.set_title(f'Season {season}: Fan Vote Distribution (Zipf\'s Law)',
                fontsize=26, fontweight='bold', pad=25)
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
             framealpha=0.95, fontsize=13, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    ax.set_ylim([0, 100])

    plt.tight_layout()
    save_path = os.path.join(output_dir, f'S{season}_Vote_Share_Stacked.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


def plot_gap_analysis(all_results, all_judge_ranks, season, output_dir):
    """Chart 4: Gap Analysis"""
    print(f"\nCreating Chart 4: Season {season} Gap Analysis...")

    if not all_results or not all_judge_ranks:
        return

    # Get all contestants
    all_celebs = set()
    for results_df in all_results.values():
        if results_df is not None:
            all_celebs.update(results_df['celebrity_name'].tolist())

    # Select top 4 by final placement
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
            # Get judge rank
            judge_rank = None
            if week in all_judge_ranks and all_judge_ranks[week] is not None:
                judge_df = all_judge_ranks[week]
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


def plot_case_studies(all_results, all_judge_ranks, season, output_dir):
    """Chart 5: Case Studies for 4 key contestants"""
    print(f"\nCreating Chart 5: Season {season} Case Studies...")

    if not all_results or not all_judge_ranks:
        return

    # Get all contestants and select top 4
    all_celebs = set()
    for results_df in all_results.values():
        if results_df is not None:
            all_celebs.update(results_df['celebrity_name'].tolist())

    key_celebs = sorted(list(all_celebs))[:4] if len(all_celebs) >= 4 else list(all_celebs)

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
            # Fan ranks
            results_df = all_results[week]
            if results_df is not None and not results_df.empty:
                celeb_data = results_df[results_df['celebrity_name'] == celebrity]
                if not celeb_data.empty:
                    fan_weeks.append(week)
                    fan_means.append(celeb_data['estimated_fan_rank_mean'].values[0])
                    fan_stds.append(celeb_data['estimated_fan_rank_std'].values[0])

            # Judge ranks
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

        # Plot Judge Rank
        if len(judge_weeks) > 0:
            ax.plot(judge_weeks, judge_ranks,
                   color='#2E86AB', linestyle='--', label='Judge Rank',
                   linewidth=4.2, marker='s', markersize=11,
                   markeredgewidth=2.5, markeredgecolor='white', alpha=0.9)

        # Plot Fan Rank
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

    save_path = os.path.join(output_dir, f'S{season}_Case_Studies.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close()


# ============================================================================
# SECTION 5: Main Execution
# ============================================================================

def merge_weeks_for_analysis(df, season, week_mapping, n_simulations=10000):
    """
    Merge multiple weeks into one analysis period.

    Args:
        df: DataFrame with all data
        season: Season number
        week_mapping: Dict like {1: [1, 2], 3: [3], 4: [4], 5: [5, 6], ...}
        n_simulations: Number of simulations

    Returns:
        merged_results: Dict mapping display week to results
        merged_judge_ranks: Dict mapping display week to judge ranks
    """
    merged_results = {}
    merged_judge_ranks = {}

    for display_week, actual_weeks in week_mapping.items():
        print(f"\n{'='*70}")
        print(f"Processing Display Week {display_week} (Actual weeks: {actual_weeks})")
        print(f"{'='*70}")

        if len(actual_weeks) == 1:
            # Single week - analyze normally
            results_df, feasible_ranks, judge_ranks = analyze_season_week(
                df, season, actual_weeks[0], n_simulations=n_simulations
            )
            if results_df is not None:
                merged_results[display_week] = results_df
            if judge_ranks is not None:
                merged_judge_ranks[display_week] = judge_ranks
        else:
            # Multiple weeks - merge analysis
            # Use the LAST week's elimination as the target
            last_week = actual_weeks[-1]

            # Get judge scores from ALL weeks in the period
            all_judge_scores = []
            for week in actual_weeks:
                week_scores = extract_judge_scores_by_week(df, season, week)
                if not week_scores.empty:
                    week_scores['week'] = week
                    all_judge_scores.append(week_scores)

            if not all_judge_scores:
                print(f"No data for merged period")
                continue

            # Combine and aggregate scores
            combined = pd.concat(all_judge_scores, ignore_index=True)

            # Sum scores across weeks for each contestant
            aggregated = combined.groupby('celebrity_name').agg({
                'judge_score_sum': 'sum'  # Sum scores from both weeks
            }).reset_index()

            # Recalculate ranks based on aggregated scores
            aggregated['judge_rank'] = aggregated['judge_score_sum'].rank(
                ascending=False, method='min'
            )

            print(f"\nAggregated Judge Scores (weeks {actual_weeks}):")
            print(aggregated.to_string())

            # Get elimination from LAST week
            elimination_result = get_eliminated_contestant(df, season, last_week)

            eliminated_name = None
            if isinstance(elimination_result, tuple):
                eliminated_name, _ = elimination_result
            else:
                eliminated_name = elimination_result

            # Remove withdrawn contestants
            withdrawn = get_withdrawn_contestants(df, season, last_week)
            if withdrawn:
                aggregated = aggregated[~aggregated['celebrity_name'].isin(withdrawn)].copy()
                aggregated['judge_rank'] = aggregated['judge_score_sum'].rank(
                    ascending=False, method='min'
                )

            print(f"\nTarget eliminated contestant: {eliminated_name}")

            if eliminated_name is None:
                print("No elimination in this merged period")
                merged_judge_ranks[display_week] = aggregated
                continue

            if eliminated_name not in aggregated['celebrity_name'].values:
                print(f"ERROR: Eliminated contestant not in aggregated data")
                merged_judge_ranks[display_week] = aggregated
                continue

            # Run simulation with aggregated scores
            feasible_fan_ranks, contestants = monte_carlo_simulation_judges_save(
                aggregated, eliminated_name, n_simulations=n_simulations
            )

            if len(feasible_fan_ranks) > 0:
                results_df = analyze_fan_ranks(feasible_fan_ranks, contestants)
                merged_results[display_week] = results_df
                print("\nEstimated Fan Ranks (Merged Period):")
                print(results_df.to_string())

            merged_judge_ranks[display_week] = aggregated

    return merged_results, merged_judge_ranks


def main():
    """Main execution for Season 28 (Rank Sum + Judges' Save)"""
    print("="*70)
    print("DWTS Season 28 Analysis - Rank Sum with Judges' Save")
    print("With Week Merging: 1-2, 3-4, 5-6, 7, 8, 9, 10, 11")
    print("="*70)

    output_dir = './output_results_s28'
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {os.path.abspath(output_dir)}\n")

    filepath = r'C:\Users\tx\AppData\Roaming\Kingsoft\office6\templates\wps\zh_CN\2026_MCM_Problem_C_Data.csv'

    if not os.path.exists(filepath):
        print(f"ERROR: Data file not found at {filepath}")
        return

    season = 28
    df, max_week = load_and_preprocess_data(filepath, season=season)

    # ========================================================================
    # DEFINE WEEK MAPPING
    # Display Week → Actual Week(s)
    # New mapping: 1-2, 3-4, 5-6, 7, 8, 9, 10, 11
    # ========================================================================
    week_mapping = {
        1: [1, 2],      # Merge Week 1+2 → Display as "1-2"
        2: [3, 4],      # Merge Week 3+4 → Display as "3-4"
        3: [5, 6],      # Merge Week 5+6 → Display as "5-6"
        4: [7],         # Week 7
        5: [8],         # Week 8
        6: [9],         # Week 9
        7: [10],        # Week 10
        8: [11]         # Week 11 (Finals)
    }

    print("\n" + "="*70)
    print("Week Mapping (Display → Actual):")
    for display, actual in week_mapping.items():
        if len(actual) > 1:
            print(f"  Display Week {display}: Merged weeks {actual} → Label '{actual[0]}-{actual[-1]}'")
        else:
            print(f"  Display Week {display}: Week {actual[0]} → Label '{actual[0]}'")
    print("="*70)

    # ========================================================================
    # SEASON 28 ANALYSIS WITH MERGING
    # ========================================================================
    season_results, season_judge_ranks = merge_weeks_for_analysis(
        df, season, week_mapping, n_simulations=10000
    )

    # Print summary
    print("\n" + "="*70)
    print("Week Analysis Summary:")
    print("="*70)
    analyzed_weeks = sorted([k for k in season_results.keys() if season_results[k] is not None])
    print(f"Successfully analyzed display weeks: {analyzed_weeks}")
    print(f"Total weeks analyzed: {len(analyzed_weeks)}")

    # ========================================================================
    # CALCULATE VOTE SHARES
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
            results_df['display_week'] = week_id
            all_results.append(results_df)

    if all_results:
        final_results = pd.concat(all_results, ignore_index=True)
        final_results = final_results.sort_values(['display_week', 'celebrity_name']).reset_index(drop=True)

        csv_path = os.path.join(output_dir, f'S{season}_fan_rank_estimates.csv')
        final_results.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

    if not vote_share_df.empty:
        vote_csv_path = os.path.join(output_dir, f'S{season}_vote_share_estimates.csv')
        vote_share_df.to_csv(vote_csv_path, index=False)
        print(f"Vote share data saved to: {vote_csv_path}")

    # ========================================================================
    # CREATE VISUALIZATIONS WITH CUSTOM LABELS
    # ========================================================================

    # Create custom week labels for X-axis
    week_labels = {}
    for display, actual in week_mapping.items():
        if len(actual) > 1:
            week_labels[display] = f"{actual[0]}-{actual[-1]}"
        else:
            week_labels[display] = str(actual[0])

    if season_results:
        plot_trajectories_merged(season_results, season_judge_ranks, season, week_labels, output_dir)
        plot_heatmap_merged(season_results, df, season, week_labels, output_dir)
        plot_vote_share_stacked(vote_share_df, season, output_dir)
        plot_gap_analysis(season_results, season_judge_ranks, season, output_dir)
        plot_case_studies(season_results, season_judge_ranks, season, output_dir)

    print("\n" + "="*70)
    print(f"ANALYSIS COMPLETE - Season {season} (With Week Merging)")
    print(f"All outputs saved to: {os.path.abspath(output_dir)}")
    print("="*70)
    print("\nGenerated files:")
    print(f"  - S{season}_fan_rank_estimates.csv")
    print(f"  - S{season}_vote_share_estimates.csv")
    print(f"  - S{season}_Trajectories.png")
    print(f"  - S{season}_Uncertainty_Heatmap.png")
    print(f"  - S{season}_Vote_Share_Stacked.png")
    print(f"  - S{season}_Gap_Analysis.png")
    print(f"  - S{season}_Case_Studies.png")
    print("\n🎯 Model with Week Merging Complete! 🎯")


if __name__ == "__main__":
    main()
