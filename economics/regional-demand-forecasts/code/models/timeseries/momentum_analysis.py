"""
Time-Series Momentum Analysis
Analyzes construction and demand momentum across metros
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')

# Set up paths
BASE_DIR = Path(__file__).parent.parent.parent
FEATURES_DIR = BASE_DIR / 'features'
MODELS_DIR = BASE_DIR / 'models' / 'timeseries'
VIZ_DIR = BASE_DIR / 'viz'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class MomentumAnalyzer:
    """Analyzes market momentum and growth acceleration"""

    def __init__(self):
        self.momentum_scores = None

    def load_data(self) -> pd.DataFrame:
        """Load feature data"""
        print("Loading feature data...")
        df = pd.read_parquet(FEATURES_DIR / 'msa_features_full.parquet')
        df = df.sort_values(['msa_name', 'year'])
        print(f"  Loaded {len(df)} records")
        return df

    def calculate_momentum_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive momentum scores for each MSA"""
        print("\nCalculating momentum scores...")

        df_momentum = df.copy()

        # 1. Construction Momentum
        # Combines building permits growth + construction employment growth
        df_momentum['construction_momentum'] = (
            (df_momentum['building_permits_growth'].fillna(0) * 0.6) +
            (df_momentum['construction_emp_growth'].fillna(0) * 0.4)
        ) * 100

        # 2. Manufacturing Momentum
        df_momentum['manufacturing_momentum'] = (
            df_momentum['manufacturing_emp_growth'].fillna(0) * 100
        )

        # 3. Demographic Momentum
        df_momentum['demographic_momentum'] = (
            df_momentum['population_growth'].fillna(0) * 100
        )

        # 4. Overall Market Momentum (weighted composite)
        df_momentum['overall_momentum'] = (
            0.40 * df_momentum['construction_momentum'] +
            0.30 * df_momentum['manufacturing_momentum'] +
            0.30 * df_momentum['demographic_momentum']
        )

        # 5. Acceleration (change in momentum)
        for col in ['construction_momentum', 'manufacturing_momentum', 'overall_momentum']:
            df_momentum[f'{col}_acceleration'] = (
                df_momentum.groupby('msa_name')[col].diff()
            )

        print(f"  ✓ Calculated momentum scores")
        return df_momentum

    def classify_momentum_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify metros into momentum regimes"""
        print("\nClassifying momentum regimes...")

        df_classified = df.copy()

        # Get latest year data
        latest_year = df_classified['year'].max()
        df_latest = df_classified[df_classified['year'] == latest_year].copy()

        # Define thresholds (percentiles)
        momentum_33 = df_latest['overall_momentum'].quantile(0.33)
        momentum_67 = df_latest['overall_momentum'].quantile(0.67)

        accel_33 = df_latest['overall_momentum_acceleration'].quantile(0.33)
        accel_67 = df_latest['overall_momentum_acceleration'].quantile(0.67)

        def classify_regime(row):
            momentum = row['overall_momentum']
            accel = row['overall_momentum_acceleration']

            # High momentum, accelerating
            if momentum > momentum_67 and accel > accel_67:
                return 'High Growth - Accelerating'

            # High momentum, stable
            elif momentum > momentum_67:
                return 'High Growth - Stable'

            # Medium momentum, accelerating
            elif momentum > momentum_33 and accel > accel_67:
                return 'Moderate Growth - Accelerating'

            # Medium momentum
            elif momentum > momentum_33:
                return 'Moderate Growth - Stable'

            # Low momentum, declining
            elif accel < accel_33:
                return 'Low Growth - Declining'

            # Low momentum
            else:
                return 'Low Growth - Stable'

        df_latest['momentum_regime'] = df_latest.apply(classify_regime, axis=1)

        # Merge back to full dataset
        df_classified = df_classified.merge(
            df_latest[['msa_name', 'momentum_regime']],
            on='msa_name',
            how='left'
        )

        print(f"  ✓ Classified metros into momentum regimes")
        print("\n  Regime distribution:")
        print(df_latest['momentum_regime'].value_counts())

        return df_classified, df_latest

    def identify_structural_breaks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify structural breaks in growth patterns"""
        print("\nIdentifying structural breaks...")

        structural_breaks = []

        for msa in df['msa_name'].unique():
            msa_data = df[df['msa_name'] == msa].sort_values('year')

            if len(msa_data) < 4:
                continue

            # Check for significant changes in growth trajectory
            permits_growth = msa_data['building_permits_growth'].values

            # Simple break detection: look for sign changes and large shifts
            for i in range(1, len(permits_growth) - 1):
                if pd.notna(permits_growth[i]) and pd.notna(permits_growth[i-1]):
                    # Detect reversal from growth to decline or vice versa
                    if (permits_growth[i-1] > 0.05 and permits_growth[i] < -0.05) or \
                       (permits_growth[i-1] < -0.05 and permits_growth[i] > 0.05):

                        structural_breaks.append({
                            'msa_name': msa,
                            'year': msa_data.iloc[i]['year'],
                            'break_type': 'Growth Reversal',
                            'metric': 'building_permits'
                        })

        df_breaks = pd.DataFrame(structural_breaks)
        print(f"  ✓ Identified {len(df_breaks)} structural breaks")

        return df_breaks

    def create_momentum_map(self, df_latest: pd.DataFrame):
        """Create momentum visualization"""
        print("\nCreating momentum visualizations...")

        # 1. Scatter plot: Momentum vs. Acceleration
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Overall Momentum vs Acceleration
        ax1 = axes[0, 0]
        scatter = ax1.scatter(
            df_latest['overall_momentum'],
            df_latest['overall_momentum_acceleration'],
            c=df_latest['demand_intensity_score'],
            s=df_latest['population'] / 100000,
            alpha=0.6,
            cmap='RdYlGn'
        )
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax1.axvline(x=0, color='k', linestyle='--', alpha=0.3)
        ax1.set_xlabel('Overall Momentum')
        ax1.set_ylabel('Momentum Acceleration')
        ax1.set_title('Market Momentum Map')
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1, label='Demand Intensity Score')

        # Add quadrant labels
        ax1.text(0.95, 0.95, 'Accelerating\nGrowth', transform=ax1.transAxes,
                ha='right', va='top', fontsize=10, alpha=0.5)
        ax1.text(0.05, 0.05, 'Declining\nMarkets', transform=ax1.transAxes,
                ha='left', va='bottom', fontsize=10, alpha=0.5)

        # Plot 2: Construction vs Manufacturing Momentum
        ax2 = axes[0, 1]
        ax2.scatter(
            df_latest['construction_momentum'],
            df_latest['manufacturing_momentum'],
            c=df_latest['demand_intensity_score'],
            s=100,
            alpha=0.6,
            cmap='RdYlGn'
        )
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax2.axvline(x=0, color='k', linestyle='--', alpha=0.3)
        ax2.set_xlabel('Construction Momentum')
        ax2.set_ylabel('Manufacturing Momentum')
        ax2.set_title('Sector Momentum Comparison')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Momentum Regime Distribution
        ax3 = axes[1, 0]
        regime_counts = df_latest['momentum_regime'].value_counts()
        ax3.barh(range(len(regime_counts)), regime_counts.values, color='steelblue', alpha=0.7)
        ax3.set_yticks(range(len(regime_counts)))
        ax3.set_yticklabels(regime_counts.index)
        ax3.set_xlabel('Number of MSAs')
        ax3.set_title('Momentum Regime Distribution')
        ax3.grid(True, alpha=0.3, axis='x')

        # Plot 4: Top 10 Metros by Momentum
        ax4 = axes[1, 1]
        top_momentum = df_latest.nlargest(10, 'overall_momentum')[['msa_name', 'overall_momentum']]
        ax4.barh(range(len(top_momentum)), top_momentum['overall_momentum'].values,
                color='forestgreen', alpha=0.7)
        ax4.set_yticks(range(len(top_momentum)))
        ax4.set_yticklabels([name[:30] for name in top_momentum['msa_name'].values])
        ax4.set_xlabel('Overall Momentum Score')
        ax4.set_title('Top 10 Metros by Momentum')
        ax4.grid(True, alpha=0.3, axis='x')
        ax4.invert_yaxis()

        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'momentum_analysis.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved momentum map: {VIZ_DIR / 'momentum_analysis.png'}")
        plt.close()

    def create_time_series_plots(self, df: pd.DataFrame):
        """Create time series plots for selected metros"""
        print("\nCreating time series plots...")

        # Select top 6 metros by latest demand intensity
        latest_year = df['year'].max()
        top_metros = (df[df['year'] == latest_year]
                      .nlargest(6, 'demand_intensity_score')['msa_name'].values)

        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        axes = axes.flatten()

        for idx, msa in enumerate(top_metros):
            ax = axes[idx]
            msa_data = df[df['msa_name'] == msa].sort_values('year')

            # Plot multiple metrics
            ax2 = ax.twinx()

            line1 = ax.plot(msa_data['year'], msa_data['building_permits_growth'] * 100,
                           'o-', color='steelblue', label='Permits Growth %', linewidth=2)
            line2 = ax2.plot(msa_data['year'], msa_data['demand_intensity_score'],
                            's-', color='coral', label='Demand Intensity', linewidth=2)

            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
            ax.set_xlabel('Year')
            ax.set_ylabel('Building Permits Growth (%)', color='steelblue')
            ax2.set_ylabel('Demand Intensity Score', color='coral')
            ax.tick_params(axis='y', labelcolor='steelblue')
            ax2.tick_params(axis='y', labelcolor='coral')
            ax.set_title(msa[:40], fontsize=10, weight='bold')
            ax.grid(True, alpha=0.3)

            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax.legend(lines, labels, loc='upper left', fontsize=8)

        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'timeseries_top_metros.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved time series plots: {VIZ_DIR / 'timeseries_top_metros.png'}")
        plt.close()

    def save_results(self, df_momentum: pd.DataFrame, df_latest: pd.DataFrame, df_breaks: pd.DataFrame):
        """Save momentum analysis results"""
        print("\nSaving results...")

        # Save momentum scores
        df_momentum.to_csv(MODELS_DIR / 'momentum_scores_timeseries.csv', index=False)

        # Save latest year with classifications
        df_latest[['msa_name', 'state', 'year', 'overall_momentum',
                   'construction_momentum', 'manufacturing_momentum',
                   'momentum_regime']].to_csv(
            MODELS_DIR / 'momentum_classification_latest.csv', index=False
        )

        # Save structural breaks
        if len(df_breaks) > 0:
            df_breaks.to_csv(MODELS_DIR / 'structural_breaks.csv', index=False)

        # Create ranking by momentum
        df_ranked = df_latest.sort_values('overall_momentum', ascending=False)
        df_ranked[['msa_name', 'state', 'overall_momentum', 'momentum_regime',
                   'demand_intensity_score']].to_csv(
            MODELS_DIR / 'msa_momentum_ranking.csv', index=False
        )

        print(f"  ✓ Saved to {MODELS_DIR}")

def main():
    """Main execution function"""
    print("=" * 70)
    print("Time-Series Momentum Analysis")
    print("=" * 70)

    analyzer = MomentumAnalyzer()

    # Load data
    df = analyzer.load_data()

    # Calculate momentum scores
    df_momentum = analyzer.calculate_momentum_scores(df)

    # Classify regimes
    df_momentum, df_latest = analyzer.classify_momentum_regimes(df_momentum)

    # Identify structural breaks
    df_breaks = analyzer.identify_structural_breaks(df_momentum)

    # Create visualizations
    analyzer.create_momentum_map(df_latest)
    analyzer.create_time_series_plots(df_momentum)

    # Save results
    analyzer.save_results(df_momentum, df_latest, df_breaks)

    print("\n" + "=" * 70)
    print("Momentum analysis complete!")
    print(f"Results saved to: {MODELS_DIR}")
    print(f"Visualizations saved to: {VIZ_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
