"""
Factor Analysis: What Makes Contestants Successful?
====================================================

Research Question (MCM Problem 3):
"What factors affect judge scores and fan support?"

Approach:
1. Feature Engineering: Industry groups, top partners, demographics
2. Target Variables: Avg Judge Score & Fan Power Index
3. Dual Regression: OLS models for technical skill vs fan appeal
4. Visualization: Contrast plot showing different impact factors

Sample Size: 421 contestants across 28 seasons

Author: MCM 2026 Team
Date: January 31, 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality style
sns.set_style("whitegrid")
sns.set_context("talk")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 16
plt.rcParams['axes.titlesize'] = 22
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']

# ============================================================================
# Data Loading
# ============================================================================

def load_data(filepath):
    """Load DWTS data"""
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} contestants")
    return df


# ============================================================================
# Feature Engineering
# ============================================================================

def categorize_industry(industry):
    """
    Categorize celebrity industry into 4 groups.

    Args:
        industry: Original industry string

    Returns:
        category: One of ['Athlete', 'Performer', 'Media_Reality', 'Other']
    """
    if pd.isna(industry):
        return 'Other'

    industry = str(industry).strip()

    # Athlete group
    athlete_keywords = ['Athlete', 'Racing Driver', 'Sports Broadcaster',
                       'NBA', 'NFL', 'Olympian', 'Olympic', 'Baseball',
                       'Hockey', 'Soccer', 'Tennis', 'Golf', 'Boxing',
                       'Wrestling', 'Swimmer', 'Gymnast', 'Skater']

    # Performer group
    performer_keywords = ['Actor', 'Actress', 'Comedian', 'Singer',
                         'Rapper', 'Musician', 'Performer', 'Entertainer']

    # Media/Reality group
    media_keywords = ['TV Personality', 'Model', 'Social Media',
                     'Radio Personality', 'Beauty Pageant', 'Reality',
                     'Bachelor', 'Bachelorette', 'Host', 'Journalist']

    # Check categories
    for keyword in athlete_keywords:
        if keyword.lower() in industry.lower():
            return 'Athlete'

    for keyword in performer_keywords:
        if keyword.lower() in industry.lower():
            return 'Performer'

    for keyword in media_keywords:
        if keyword.lower() in industry.lower():
            return 'Media_Reality'

    return 'Other'


def create_top_partner_flag(partner):
    """
    Flag whether partner is a top professional (15+ appearances).

    Top Partners (15+ appearances):
    - Cheryl Burke
    - Mark Ballas
    - Tony Dovolani
    - Valentin Chmerkovskiy
    - Karina Smirnoff
    - Derek Hough
    - Maksim Chmerkovskiy (note: Chmerkoskiy in data)
    - Emma Slater
    - Peta Murgatroyd
    """
    if pd.isna(partner):
        return 0

    partner = str(partner).strip()

    top_partners = [
        'Cheryl Burke',
        'Mark Ballas',
        'Tony Dovolani',
        'Valentin Chmerkovskiy',
        'Karina Smirnoff',
        'Derek Hough',
        'Maksim Chmerkovskiy',
        'Maksim Chmerkoskiy',  # Alternative spelling
        'Emma Slater',
        'Peta Murgatroyd'
    ]

    for top_partner in top_partners:
        if top_partner.lower() in partner.lower():
            return 1

    return 0


def create_us_flag(country):
    """Flag whether contestant is from United States"""
    if pd.isna(country):
        return 0

    country = str(country).strip().lower()

    if 'united states' in country or 'usa' in country or 'u.s.' in country:
        return 1

    return 0


def engineer_features(df):
    """
    Apply all feature engineering transformations.

    Returns:
        df: DataFrame with new features
    """
    print("\n" + "="*70)
    print("FEATURE ENGINEERING")
    print("="*70)

    # A. Industry categorization
    print("\nA. Categorizing industries...")
    df['industry_category'] = df['celebrity_industry'].apply(categorize_industry)

    print("\nIndustry distribution:")
    print(df['industry_category'].value_counts())

    # Create dummy variables
    df['is_Athlete'] = (df['industry_category'] == 'Athlete').astype(int)
    df['is_Performer'] = (df['industry_category'] == 'Performer').astype(int)
    df['is_Media_Reality'] = (df['industry_category'] == 'Media_Reality').astype(int)
    # Note: 'Other' is the reference category

    # B. Top partner flag
    print("\nB. Identifying top partners...")
    df['is_top_partner'] = df['ballroom_partner'].apply(create_top_partner_flag)
    print(f"Contestants with top partners: {df['is_top_partner'].sum()} ({df['is_top_partner'].mean()*100:.1f}%)")

    # C. US flag
    print("\nC. Identifying US contestants...")
    df['is_US'] = df['celebrity_homecountry/region'].apply(create_us_flag)
    print(f"US contestants: {df['is_US'].sum()} ({df['is_US'].mean()*100:.1f}%)")

    # D. Age (already in data)
    print("\nD. Age statistics:")
    print(f"Mean age: {df['celebrity_age_during_season'].mean():.1f}")
    print(f"Age range: {df['celebrity_age_during_season'].min():.0f} - {df['celebrity_age_during_season'].max():.0f}")

    return df


# ============================================================================
# Target Variable Construction
# ============================================================================

def calculate_avg_judge_score(df):
    """
    Calculate average judge score across all weeks for each contestant.
    """
    print("\n" + "="*70)
    print("CALCULATING TARGET VARIABLES")
    print("="*70)

    print("\nCalculating average judge scores...")

    # Get all judge score columns
    judge_cols = [col for col in df.columns if 'judge' in col.lower() and 'score' in col.lower()]

    # Calculate mean across all weeks (ignoring NaN)
    df['Avg_Judge_Score'] = df[judge_cols].mean(axis=1, skipna=True)

    print(f"Average judge score: {df['Avg_Judge_Score'].mean():.2f} ± {df['Avg_Judge_Score'].std():.2f}")

    return df


def calculate_judge_rank_and_fan_power(df):
    """
    Calculate judge rank within season and fan power index.

    Fan Power Index = Judge Rank - Final Placement
    - Positive: Fan support exceeded technical performance
    - Negative: Technical performance exceeded final placement
    """
    print("\nCalculating judge ranks within seasons...")

    # Calculate judge rank within each season
    df['Judge_Rank'] = df.groupby('season')['Avg_Judge_Score'].rank(
        ascending=False, method='min'
    )

    print("\nCalculating Fan Power Index...")

    # Fan Power Index = Judge Rank - Placement
    # Positive = fans pushed them higher than judges would have
    # Negative = placed lower than judge scores suggest
    df['Fan_Power_Index'] = df['Judge_Rank'] - df['placement']

    print(f"Fan Power Index: {df['Fan_Power_Index'].mean():.2f} ± {df['Fan_Power_Index'].std():.2f}")
    print(f"Range: {df['Fan_Power_Index'].min():.1f} to {df['Fan_Power_Index'].max():.1f}")

    # Show examples
    print("\nTop 5 fan favorites (highest Fan Power Index):")
    top_fan = df.nlargest(5, 'Fan_Power_Index')[
        ['celebrity_name', 'season', 'Judge_Rank', 'placement', 'Fan_Power_Index']
    ]
    print(top_fan.to_string(index=False))

    print("\nTop 5 judge favorites (lowest Fan Power Index):")
    top_judge = df.nsmallest(5, 'Fan_Power_Index')[
        ['celebrity_name', 'season', 'Judge_Rank', 'placement', 'Fan_Power_Index']
    ]
    print(top_judge.to_string(index=False))

    return df


# ============================================================================
# Regression Models
# ============================================================================

def prepare_regression_data(df):
    """
    Prepare clean dataset for regression (drop NaN in key variables).
    """
    print("\n" + "="*70)
    print("PREPARING REGRESSION DATA")
    print("="*70)

    # Select relevant columns
    columns_needed = [
        'Avg_Judge_Score', 'Fan_Power_Index',
        'celebrity_age_during_season',
        'is_Athlete', 'is_Performer', 'is_Media_Reality',
        'is_top_partner', 'is_US'
    ]

    # Drop rows with NaN in these columns
    df_clean = df[columns_needed].dropna()

    print(f"\nSample size: {len(df)} → {len(df_clean)} (after removing missing values)")

    return df_clean


def run_regression_models(df_clean):
    """
    Run two OLS regression models:
    1. Judge Score Model: Technical factors
    2. Fan Power Model: Fan appeal factors
    """
    print("\n" + "="*70)
    print("REGRESSION ANALYSIS")
    print("="*70)

    # Rename age column for easier formula
    df_clean = df_clean.rename(columns={
        'celebrity_age_during_season': 'Age'
    })

    # Model 1: Judge Score (Technical Performance)
    print("\n" + "="*70)
    print("MODEL 1: JUDGE SCORE (Technical Performance)")
    print("="*70)

    formula_judge = 'Avg_Judge_Score ~ Age + is_Athlete + is_Performer + is_Media_Reality + is_top_partner + is_US'

    model_judge = ols(formula_judge, data=df_clean).fit()
    print(model_judge.summary())

    # Model 2: Fan Power Index (Fan Appeal)
    print("\n" + "="*70)
    print("MODEL 2: FAN POWER INDEX (Fan Appeal)")
    print("="*70)

    formula_fan = 'Fan_Power_Index ~ Age + is_Athlete + is_Performer + is_Media_Reality + is_top_partner + is_US'

    model_fan = ols(formula_fan, data=df_clean).fit()
    print(model_fan.summary())

    return model_judge, model_fan


# ============================================================================
# Standardized Coefficients
# ============================================================================

def calculate_standardized_coefficients(model, df, predictors):
    """
    Calculate standardized (beta) coefficients.

    Standardized coefficient = raw_coefficient * (SD_X / SD_Y)
    """
    # Get standard deviations
    y_std = df[model.model.endog_names].std()

    standardized_coefs = {}

    # Map predictor names to actual DataFrame column names
    predictor_map = {
        'Age': 'celebrity_age_during_season',
        'is_Athlete': 'is_Athlete',
        'is_Performer': 'is_Performer',
        'is_Media_Reality': 'is_Media_Reality',
        'is_top_partner': 'is_top_partner',
        'is_US': 'is_US'
    }

    for predictor in predictors:
        if predictor in model.params.index:
            # Get the actual column name in DataFrame
            actual_col = predictor_map.get(predictor, predictor)

            # Check if column exists in DataFrame
            if actual_col in df.columns:
                x_std = df[actual_col].std()
                raw_coef = model.params[predictor]

                standardized_coef = raw_coef * (x_std / y_std)
                standardized_coefs[predictor] = standardized_coef
            else:
                print(f"Warning: Column '{actual_col}' not found in DataFrame")
                standardized_coefs[predictor] = 0

    return standardized_coefs


# ============================================================================
# Sensitivity Analysis
# ============================================================================

def perform_sensitivity_analysis(df_clean):
    """
    Perform sensitivity analysis: How do model coefficients change
    when we vary the sample (bootstrap) or model specification?

    Tests:
    1. Bootstrap stability: Resample data 100 times, check coefficient variability
    2. Specification robustness: Test with different predictor combinations
    """
    print("\n" + "="*70)
    print("SENSITIVITY ANALYSIS")
    print("="*70)

    # Rename age column
    df_clean = df_clean.rename(columns={'celebrity_age_during_season': 'Age'})

    # 1. Bootstrap Analysis
    print("\n1. BOOTSTRAP STABILITY ANALYSIS (100 iterations)")
    print("   Testing coefficient stability with resampling...")

    n_bootstrap = 100
    bootstrap_results_judge = []
    bootstrap_results_fan = []

    formula_judge = 'Avg_Judge_Score ~ Age + is_Athlete + is_Performer + is_Media_Reality + is_top_partner + is_US'
    formula_fan = 'Fan_Power_Index ~ Age + is_Athlete + is_Performer + is_Media_Reality + is_top_partner + is_US'

    np.random.seed(42)

    for i in range(n_bootstrap):
        # Resample with replacement
        sample = df_clean.sample(n=len(df_clean), replace=True)

        # Fit models
        model_j = ols(formula_judge, data=sample).fit()
        model_f = ols(formula_fan, data=sample).fit()

        bootstrap_results_judge.append(model_j.params)
        bootstrap_results_fan.append(model_f.params)

    # Convert to DataFrame
    bootstrap_df_judge = pd.DataFrame(bootstrap_results_judge)
    bootstrap_df_fan = pd.DataFrame(bootstrap_results_fan)

    # Calculate statistics
    print("\n   Bootstrap Results (Judge Score Model):")
    print("   " + "-"*60)
    for param in ['is_Athlete', 'is_Performer', 'is_Media_Reality', 'is_top_partner']:
        if param in bootstrap_df_judge.columns:
            mean_coef = bootstrap_df_judge[param].mean()
            std_coef = bootstrap_df_judge[param].std()
            ci_low = bootstrap_df_judge[param].quantile(0.025)
            ci_high = bootstrap_df_judge[param].quantile(0.975)

            print(f"   {param:20s}: {mean_coef:+.3f} ± {std_coef:.3f}")
            print(f"                         95% CI: [{ci_low:+.3f}, {ci_high:+.3f}]")

    print("\n   Bootstrap Results (Fan Power Model):")
    print("   " + "-"*60)
    for param in ['is_Athlete', 'is_Performer', 'is_Media_Reality', 'is_top_partner']:
        if param in bootstrap_df_fan.columns:
            mean_coef = bootstrap_df_fan[param].mean()
            std_coef = bootstrap_df_fan[param].std()
            ci_low = bootstrap_df_fan[param].quantile(0.025)
            ci_high = bootstrap_df_fan[param].quantile(0.975)

            print(f"   {param:20s}: {mean_coef:+.3f} ± {std_coef:.3f}")
            print(f"                         95% CI: [{ci_low:+.3f}, {ci_high:+.3f}]")

    # 2. Model Specification Robustness
    print("\n2. MODEL SPECIFICATION ROBUSTNESS")
    print("   Testing how coefficients change with different predictors...")

    specifications = [
        ('Base', 'is_Athlete + is_Performer + is_Media_Reality'),
        ('+ Demographics', 'Age + is_Athlete + is_Performer + is_Media_Reality + is_US'),
        ('+ Partner', 'is_Athlete + is_Performer + is_Media_Reality + is_top_partner'),
        ('Full Model', 'Age + is_Athlete + is_Performer + is_Media_Reality + is_top_partner + is_US')
    ]

    print("\n   Athlete Coefficient Across Specifications:")
    print("   " + "-"*60)

    for spec_name, spec_formula in specifications:
        formula_j = f'Avg_Judge_Score ~ {spec_formula}'
        formula_f = f'Fan_Power_Index ~ {spec_formula}'

        model_j = ols(formula_j, data=df_clean).fit()
        model_f = ols(formula_f, data=df_clean).fit()

        athlete_coef_j = model_j.params.get('is_Athlete', np.nan)
        athlete_coef_f = model_f.params.get('is_Athlete', np.nan)

        print(f"   {spec_name:20s}: Judge={athlete_coef_j:+.3f}, Fan={athlete_coef_f:+.3f}")

    # 3. Create sensitivity visualization
    plot_sensitivity_results(bootstrap_df_judge, bootstrap_df_fan)

    return bootstrap_df_judge, bootstrap_df_fan


def plot_sensitivity_results(bootstrap_df_judge, bootstrap_df_fan,
                             output_path='Sensitivity_Analysis.png'):
    """
    Visualize bootstrap results showing coefficient stability.
    """
    print("\n   Creating sensitivity visualization...")

    # Select key predictors
    predictors = ['is_Athlete', 'is_Performer', 'is_Media_Reality', 'is_top_partner']
    labels = ['Athlete', 'Performer', 'Media/Reality', 'Top Partner']

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, (pred, label) in enumerate(zip(predictors, labels)):
        ax = axes[idx]

        if pred in bootstrap_df_judge.columns and pred in bootstrap_df_fan.columns:
            # Plot distributions
            ax.hist(bootstrap_df_judge[pred], bins=30, alpha=0.6,
                   color='#3498DB', label='Judge Score', density=True)
            ax.hist(bootstrap_df_fan[pred], bins=30, alpha=0.6,
                   color='#E74C3C', label='Fan Power', density=True)

            # Add mean lines
            mean_judge = bootstrap_df_judge[pred].mean()
            mean_fan = bootstrap_df_fan[pred].mean()

            ax.axvline(mean_judge, color='#3498DB', linestyle='--', linewidth=3,
                      label=f'Judge Mean: {mean_judge:.3f}')
            ax.axvline(mean_fan, color='#E74C3C', linestyle='--', linewidth=3,
                      label=f'Fan Mean: {mean_fan:.3f}')

            # Add zero line
            ax.axvline(0, color='black', linestyle='-', linewidth=2, alpha=0.5)

            ax.set_xlabel('Coefficient Value', fontsize=14, fontweight='bold')
            ax.set_ylabel('Density', fontsize=14, fontweight='bold')
            ax.set_title(f'{label}\nBootstrap Distribution (n=100)',
                        fontsize=16, fontweight='bold')
            ax.legend(fontsize=11, loc='best')
            ax.grid(alpha=0.3)

    plt.suptitle('Sensitivity Analysis: Bootstrap Coefficient Stability\n' +
                'Testing robustness of factor effects',
                fontsize=20, fontweight='bold', y=0.995)

    plt.tight_layout(rect=[0, 0, 1, 0.99])
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"   ✅ Saved: {output_path}")
    plt.close()


# ============================================================================
# Visualization
# ============================================================================

def plot_factor_contrast(model_judge, model_fan, df_clean, output_path='Factor_Impact_Contrast.png'):
    """
    Create contrast plot showing different impacts on judge scores vs fan appeal.
    """
    print("\n" + "="*70)
    print("CREATING FACTOR CONTRAST VISUALIZATION")
    print("="*70)

    # Define predictors (exclude intercept)
    predictors = ['Age', 'is_Athlete', 'is_Performer', 'is_Media_Reality',
                 'is_top_partner', 'is_US']

    # Calculate standardized coefficients
    std_coef_judge = calculate_standardized_coefficients(model_judge, df_clean, predictors)
    std_coef_fan = calculate_standardized_coefficients(model_fan, df_clean, predictors)

    # Create labels
    labels = {
        'Age': 'Age',
        'is_Athlete': 'Athlete',
        'is_Performer': 'Performer',
        'is_Media_Reality': 'Media/Reality',
        'is_top_partner': 'Top Partner',
        'is_US': 'US Contestant'
    }

    # Prepare data for plotting
    factor_names = [labels[p] for p in predictors]
    judge_impacts = [std_coef_judge.get(p, 0) for p in predictors]
    fan_impacts = [std_coef_fan.get(p, 0) for p in predictors]

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))

    y_pos = np.arange(len(factor_names))
    bar_height = 0.35

    # Plot bars
    bars1 = ax.barh(y_pos - bar_height/2, judge_impacts, bar_height,
                    label='Judge Score Impact', color='#3498DB', alpha=0.8,
                    edgecolor='black', linewidth=1.5)

    bars2 = ax.barh(y_pos + bar_height/2, fan_impacts, bar_height,
                    label='Fan Power Impact', color='#E74C3C', alpha=0.8,
                    edgecolor='black', linewidth=1.5)

    # Add value labels
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        # Judge impact label
        width1 = bar1.get_width()
        ax.text(width1 + 0.01 if width1 >= 0 else width1 - 0.01,
               bar1.get_y() + bar1.get_height()/2,
               f'{width1:.3f}', va='center',
               ha='left' if width1 >= 0 else 'right',
               fontsize=13, fontweight='bold')

        # Fan impact label
        width2 = bar2.get_width()
        ax.text(width2 + 0.01 if width2 >= 0 else width2 - 0.01,
               bar2.get_y() + bar2.get_height()/2,
               f'{width2:.3f}', va='center',
               ha='left' if width2 >= 0 else 'right',
               fontsize=13, fontweight='bold')

    # Highlight opposite effects
    for i, (j_impact, f_impact) in enumerate(zip(judge_impacts, fan_impacts)):
        if (j_impact > 0 and f_impact < 0) or (j_impact < 0 and f_impact > 0):
            # Draw a box around this factor
            ax.add_patch(plt.Rectangle((min(j_impact, f_impact) - 0.02, i - 0.5),
                                      abs(j_impact - f_impact) + 0.04, 1,
                                      fill=False, edgecolor='gold', linewidth=3,
                                      linestyle='--'))

            # Add annotation
            ax.text(0, i, '⚠️ OPPOSITE', fontsize=12, fontweight='bold',
                   color='darkgoldenrod', ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    # Add zero line
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2)

    # Styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(factor_names, fontsize=17, fontweight='bold')
    ax.set_xlabel('Standardized Coefficient (Effect Size)', fontsize=20, fontweight='bold')
    ax.set_title('Factor Impact Contrast: Judge Scores vs Fan Appeal\n' +
                'What drives technical performance vs popularity?',
                fontsize=22, fontweight='bold', pad=25)

    ax.legend(loc='lower right', fontsize=17, framealpha=0.95,
             fancybox=True, shadow=True)
    ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.8)

    # Add interpretation box
    interpretation = (
        "Interpretation:\n"
        "• Blue bars: Factors increasing judge scores\n"
        "• Red bars: Factors increasing fan support\n"
        "• ⚠️ OPPOSITE: Factor has conflicting effects\n"
        "• Magnitude shows relative importance"
    )
    ax.text(0.02, 0.98, interpretation,
           transform=ax.transAxes, fontsize=14,
           verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle='round', facecolor='lightyellow',
                    alpha=0.9, edgecolor='black', linewidth=2))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ Saved: {output_path}")
    plt.close()


# ============================================================================
# Summary Report
# ============================================================================

def create_summary_report(model_judge, model_fan):
    """Create summary report of key findings"""
    print("\n" + "="*70)
    print("SUMMARY OF KEY FINDINGS")
    print("="*70)

    print("\n📊 MODEL 1: JUDGE SCORE")
    print("   Significant factors:")

    for param, pval in model_judge.pvalues.items():
        if param != 'Intercept' and pval < 0.05:
            coef = model_judge.params[param]
            print(f"   • {param}: {coef:+.3f} (p={pval:.4f})")

    print(f"\n   R-squared: {model_judge.rsquared:.3f}")
    print(f"   Adjusted R-squared: {model_judge.rsquared_adj:.3f}")

    print("\n📊 MODEL 2: FAN POWER INDEX")
    print("   Significant factors:")

    for param, pval in model_fan.pvalues.items():
        if param != 'Intercept' and pval < 0.05:
            coef = model_fan.params[param]
            print(f"   • {param}: {coef:+.3f} (p={pval:.4f})")

    print(f"\n   R-squared: {model_fan.rsquared:.3f}")
    print(f"   Adjusted R-squared: {model_fan.rsquared_adj:.3f}")

    print("\n🎯 KEY INSIGHTS:")

    # Check for opposite effects
    for param in ['is_Athlete', 'is_Performer', 'is_Media_Reality', 'is_top_partner']:
        if param in model_judge.params.index and param in model_fan.params.index:
            judge_coef = model_judge.params[param]
            fan_coef = model_fan.params[param]

            if (judge_coef > 0 and fan_coef < 0) or (judge_coef < 0 and fan_coef > 0):
                print(f"\n   ⚠️ {param}: OPPOSITE EFFECTS")
                print(f"      Judge impact: {judge_coef:+.3f}")
                print(f"      Fan impact: {fan_coef:+.3f}")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Run complete factor analysis"""
    print("="*70)
    print("FACTOR ANALYSIS: WHAT MAKES CONTESTANTS SUCCESSFUL?")
    print("="*70)

    print("\nObjective:")
    print("  Identify factors that influence:")
    print("  1. Judge scores (technical performance)")
    print("  2. Fan support (popularity beyond skill)")

    # Load data
    filepath = '2026_MCM_Problem_C_Data.csv'
    df = load_data(filepath)

    # Feature engineering
    df = engineer_features(df)

    # Target variables
    df = calculate_avg_judge_score(df)
    df = calculate_judge_rank_and_fan_power(df)

    # Prepare data for regression
    df_clean = prepare_regression_data(df)

    # Run regression models
    model_judge, model_fan = run_regression_models(df_clean)

    # Sensitivity analysis
    bootstrap_judge, bootstrap_fan = perform_sensitivity_analysis(df_clean.copy())

    # Create visualizations
    plot_factor_contrast(model_judge, model_fan, df_clean)

    # Summary report
    create_summary_report(model_judge, model_fan)

    # Save processed data
    print("\n" + "="*70)
    print("SAVING PROCESSED DATA")
    print("="*70)

    output_cols = [
        'celebrity_name', 'season', 'placement',
        'Avg_Judge_Score', 'Judge_Rank', 'Fan_Power_Index',
        'celebrity_age_during_season', 'industry_category',
        'is_Athlete', 'is_Performer', 'is_Media_Reality',
        'is_top_partner', 'is_US'
    ]

    # Filter to only existing columns
    existing_cols = [col for col in output_cols if col in df.columns]
    missing_cols = [col for col in output_cols if col not in df.columns]

    if missing_cols:
        print(f"\n⚠️  Warning: {len(missing_cols)} columns not found in DataFrame:")
        for col in missing_cols:
            print(f"     - {col}")
        print(f"\n✓ Saving {len(existing_cols)} available columns instead")
    else:
        print(f"\n✓ All {len(existing_cols)} columns found")

    df[existing_cols].to_csv('Factor_Analysis_Data.csv', index=False)
    print("\n✅ Saved: Factor_Analysis_Data.csv")

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\n📊 FILES GENERATED:")
    print("   - Factor_Impact_Contrast.png (factor comparison)")
    print("   - Sensitivity_Analysis.png (bootstrap stability)")
    print("   - Factor_Analysis_Data.csv (processed data)")

    print("\n🎯 USE THESE RESULTS FOR MCM PROBLEM 3:")
    print("   Analyze how contestant characteristics affect success")


if __name__ == "__main__":
    main()