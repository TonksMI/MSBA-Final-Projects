#!/usr/bin/env python3
"""
Example analysis script using the constructed panel.

Demonstrates basic analyses:
1. Difference-in-differences estimation
2. Event study
3. Descriptive statistics and visualization
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def load_panel(panel_path: str = "clean/steel_panel.parquet") -> pd.DataFrame:
    """Load the panel dataset."""
    print(f"Loading panel from {panel_path}")
    df = pd.read_parquet(panel_path)
    print(f"Loaded {len(df):,} observations")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Countries: {df['country'].nunique()}")
    print(f"HS6 codes: {df['hs6'].nunique()}")
    return df


def descriptive_statistics(df: pd.DataFrame):
    """Generate descriptive statistics."""
    print("\n" + "="*60)
    print("DESCRIPTIVE STATISTICS")
    print("="*60)

    # Summary by treatment status
    print("\n--- By Treatment Status ---")
    summary = df.groupby('exposure_indicator')[
        ['import_volume_mt', 'import_value_usd', 'tariff_rate', 'unit_value']
    ].mean()
    print(summary)

    # Summary by period
    print("\n--- By Period (Pre/Post Treatment) ---")
    summary = df.groupby('post_treat')[
        ['import_volume_mt', 'import_value_usd', 'tariff_rate', 'unit_value']
    ].mean()
    print(summary)

    # Top importing countries
    print("\n--- Top 10 Importing Countries (by volume) ---")
    top_countries = df.groupby('country')['import_volume_mt'].sum().sort_values(ascending=False).head(10)
    print(top_countries)


def difference_in_differences(df: pd.DataFrame):
    """
    Run basic difference-in-differences estimation.

    Model: Y_ict = α + β1*Treated_c + β2*Post_t + β3*(Treated_c × Post_t) + X_it + ε_ict

    Where:
    - Y_ict: outcome for country i, product c, time t
    - Treated_c: indicator for Section 232-affected products
    - Post_t: indicator for post-March 2018
    - X_it: controls (oil price, macro indicators)
    """
    print("\n" + "="*60)
    print("DIFFERENCE-IN-DIFFERENCES ESTIMATION")
    print("="*60)

    # Filter to complete cases
    df_reg = df.dropna(subset=['log_import_volume', 'treated_post', 'exposure_indicator', 'post_treat'])

    # Basic DiD specification
    print("\n--- Basic DiD (no controls) ---")
    formula = "log_import_volume ~ exposure_indicator + post_treat + treated_post"
    model1 = smf.ols(formula, data=df_reg).fit()
    print(model1.summary())

    # DiD with controls
    print("\n--- DiD with macro controls ---")
    formula = """log_import_volume ~ exposure_indicator + post_treat + treated_post +
                 oil_price + industrial_production"""
    model2 = smf.ols(formula, data=df_reg).fit()
    print(model2.summary())

    # DiD with fixed effects (country and HS6)
    print("\n--- DiD with fixed effects ---")
    # Add country and HS6 fixed effects
    df_reg_fe = pd.get_dummies(df_reg, columns=['country', 'hs6'], drop_first=True)
    fe_cols = [col for col in df_reg_fe.columns if col.startswith('country_') or col.startswith('hs6_')]

    formula = f"log_import_volume ~ treated_post + oil_price + {' + '.join(fe_cols[:20])}"  # Limit FE for display
    model3 = smf.ols(formula, data=df_reg_fe).fit()
    print(model3.summary().tables[1])  # Only coefficients table

    return model1, model2, model3


def event_study(df: pd.DataFrame, output_dir: str = "analysis"):
    """
    Run event study around Section 232 implementation.

    Plots treatment effect over time.
    """
    print("\n" + "="*60)
    print("EVENT STUDY")
    print("="*60)

    # Create event time (months relative to March 2018)
    treatment_date = pd.to_datetime('2018-03-01')
    df = df.copy()
    df['event_time'] = ((df['date'].dt.year - treatment_date.year) * 12 +
                        (df['date'].dt.month - treatment_date.month))

    # Limit to +/- 24 months around treatment
    df_event = df[(df['event_time'] >= -24) & (df['event_time'] <= 24)].copy()

    # Create event time dummies (omit t=-1 as reference)
    event_dummies = pd.get_dummies(df_event['event_time'], prefix='event_time')
    event_dummies = event_dummies.drop(columns=['event_time_-1'], errors='ignore')

    # Only include treated × event_time interactions
    for col in event_dummies.columns:
        df_event[col] = event_dummies[col] * df_event['exposure_indicator']

    # Run regression
    event_cols = [col for col in df_event.columns if col.startswith('event_time_')]
    formula = f"log_import_volume ~ {' + '.join(event_cols)}"

    model = smf.ols(formula, data=df_event.dropna(subset=['log_import_volume'])).fit()

    # Extract coefficients
    coeffs = {}
    for col in event_cols:
        if col in model.params:
            event_t = int(col.split('_')[-1])
            coeffs[event_t] = {
                'coef': model.params[col],
                'se': model.bse[col],
                'ci_lower': model.conf_int().loc[col, 0],
                'ci_upper': model.conf_int().loc[col, 1],
            }

    # Add reference period (t=-1)
    coeffs[-1] = {'coef': 0, 'se': 0, 'ci_lower': 0, 'ci_upper': 0}

    # Sort by event time
    event_times = sorted(coeffs.keys())
    coef_values = [coeffs[t]['coef'] for t in event_times]
    ci_lower = [coeffs[t]['ci_lower'] for t in event_times]
    ci_upper = [coeffs[t]['ci_upper'] for t in event_times]

    # Plot
    plt.figure(figsize=(14, 7))
    plt.plot(event_times, coef_values, 'o-', linewidth=2, markersize=6, label='Point Estimate')
    plt.fill_between(event_times, ci_lower, ci_upper, alpha=0.3, label='95% CI')
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    plt.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='Section 232 Implementation')
    plt.xlabel('Months Relative to Section 232 (March 2018)', fontsize=12)
    plt.ylabel('Treatment Effect on Log Import Volume', fontsize=12)
    plt.title('Event Study: Impact of Section 232 Tariffs on Steel Imports', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output_path = Path(output_dir) / 'event_study.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Event study plot saved to {output_path}")
    plt.close()

    return coeffs


def plot_import_trends(df: pd.DataFrame, output_dir: str = "analysis"):
    """Plot import trends over time."""
    print("\n" + "="*60)
    print("PLOTTING IMPORT TRENDS")
    print("="*60)

    # Aggregate to monthly level
    monthly = df.groupby(['date', 'exposure_indicator']).agg({
        'import_volume_mt': 'sum',
        'import_value_usd': 'sum'
    }).reset_index()

    # Create treatment labels
    monthly['group'] = monthly['exposure_indicator'].map({
        1: 'Treated (Steel Products)',
        0: 'Control (Non-Steel Products)'
    })

    # Plot volume
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    for group in monthly['group'].unique():
        data = monthly[monthly['group'] == group]
        ax1.plot(data['date'], data['import_volume_mt'], label=group, linewidth=2)

    ax1.axvline(pd.to_datetime('2018-03-01'), color='red', linestyle='--',
                linewidth=2, label='Section 232', alpha=0.7)
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Total Import Volume (Metric Tons)', fontsize=12)
    ax1.set_title('Import Volume Trends', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot value
    for group in monthly['group'].unique():
        data = monthly[monthly['group'] == group]
        ax2.plot(data['date'], data['import_value_usd'] / 1e9, label=group, linewidth=2)

    ax2.axvline(pd.to_datetime('2018-03-01'), color='red', linestyle='--',
                linewidth=2, label='Section 232', alpha=0.7)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Total Import Value (Billion USD)', fontsize=12)
    ax2.set_title('Import Value Trends', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = Path(output_dir) / 'import_trends.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Import trends plot saved to {output_path}")
    plt.close()


def main():
    """Run example analyses."""
    print("="*60)
    print("STEEL TARIFF ANALYSIS - EXAMPLE SCRIPT")
    print("="*60)

    # Load data
    df = load_panel()

    # Descriptive statistics
    descriptive_statistics(df)

    # Difference-in-differences
    difference_in_differences(df)

    # Event study
    event_study(df)

    # Visualizations
    plot_import_trends(df)

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("\nOutputs saved to 'analysis/' directory")


if __name__ == '__main__':
    main()
