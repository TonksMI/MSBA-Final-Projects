"""
Feature Engineering Pipeline
Creates advanced features for modeling and analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple
from sklearn.preprocessing import StandardScaler

# Set up paths
BASE_DIR = Path(__file__).parent.parent
CLEAN_DATA_DIR = BASE_DIR / 'data' / 'clean'
FEATURES_DIR = BASE_DIR / 'features'
FEATURES_DIR.mkdir(parents=True, exist_ok=True)

class FeatureEngineer:
    """Handles feature engineering for steel demand analysis"""

    def __init__(self, clean_dir: Path, features_dir: Path):
        self.clean_dir = clean_dir
        self.features_dir = features_dir

    def load_clean_data(self) -> pd.DataFrame:
        """Load the cleaned MSA panel data"""
        print("Loading cleaned data...")
        df = pd.read_parquet(self.clean_dir / 'msa_panel_clean.parquet')
        print(f"  Loaded {len(df)} records")
        return df

    def create_lagged_features(self, df: pd.DataFrame, lags: List[int] = [1, 2]) -> pd.DataFrame:
        """Create lagged features for time-series predictive models"""
        print("\nCreating lagged features...")

        df = df.copy()
        df = df.sort_values(['msa_name', 'year'])

        # Features to lag
        lag_vars = [
            'building_permits',
            'construction_emp',
            'manufacturing_emp',
            'median_income',
            'infra_spending_millions'
        ]

        for var in lag_vars:
            for lag in lags:
                df[f'{var}_lag{lag}'] = df.groupby('msa_name')[var].shift(lag)

        print(f"  ✓ Created {len(lag_vars) * len(lags)} lagged features")
        return df

    def create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create rolling window statistics"""
        print("\nCreating rolling window features...")

        df = df.copy()
        df = df.sort_values(['msa_name', 'year'])

        # Rolling metrics
        rolling_vars = {
            'building_permits': [2, 3],
            'construction_emp': [2, 3],
            'manufacturing_emp': [3],
            'population': [3]
        }

        for var, windows in rolling_vars.items():
            for window in windows:
                # Rolling mean
                df[f'{var}_rolling_mean_{window}yr'] = (
                    df.groupby('msa_name')[var]
                    .transform(lambda x: x.rolling(window=window, min_periods=1).mean())
                )

                # Rolling std
                df[f'{var}_rolling_std_{window}yr'] = (
                    df.groupby('msa_name')[var]
                    .transform(lambda x: x.rolling(window=window, min_periods=1).std())
                )

        print(f"  ✓ Created rolling window features")
        return df

    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction terms between key variables"""
        print("\nCreating interaction features...")

        df = df.copy()

        # Manufacturing × Construction (industrial synergy)
        df['mfg_constr_interaction'] = (
            df['mfg_emp_per_capita'] * df['constr_emp_per_capita']
        )

        # Income × Building Permits (affluence × growth)
        df['income_permits_interaction'] = (
            df['median_income'] * df['permits_per_capita']
        )

        # Population × Manufacturing (market size × industrial base)
        df['pop_mfg_interaction'] = (
            df['population'] * df['mfg_emp_per_capita']
        )

        # Infrastructure × Construction (public investment synergy)
        df['infra_constr_interaction'] = (
            df['infra_spending_per_capita'] * df['constr_emp_per_capita']
        )

        print(f"  ✓ Created 4 interaction features")
        return df

    def create_industry_concentration_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create Herfindahl-Hirschman Index style metric for industrial diversity
        Higher values = more concentrated (specialized) economy
        """
        print("\nCreating industry concentration index...")

        df = df.copy()

        # Approximate industry shares (in real scenario, use detailed NAICS data)
        df['total_employment'] = df['manufacturing_emp'] + df['construction_emp']

        df['mfg_share'] = df['manufacturing_emp'] / df['total_employment']
        df['constr_share'] = df['construction_emp'] / df['total_employment']

        # HHI-style calculation (simplified)
        df['industry_concentration_index'] = (
            df['mfg_share']**2 + df['constr_share']**2
        )

        # Diversity index (inverse of concentration)
        df['industry_diversity_index'] = 1 - df['industry_concentration_index']

        print(f"  ✓ Created industry concentration metrics")
        return df

    def create_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create momentum indicators for trend identification"""
        print("\nCreating momentum indicators...")

        df = df.copy()
        df = df.sort_values(['msa_name', 'year'])

        # Acceleration (2nd derivative) of key metrics
        for metric in ['building_permits', 'construction_emp']:
            growth_col = f'{metric}_growth'
            df[f'{metric}_acceleration'] = (
                df.groupby('msa_name')[growth_col].diff()
            )

        # Cumulative growth since base year
        df['years_since_base'] = df['year'] - df['year'].min()
        for metric in ['population', 'median_income']:
            df[f'{metric}_cumulative_growth'] = (
                df.groupby('msa_name')[metric]
                .transform(lambda x: (x / x.iloc[0] - 1) if len(x) > 0 else 0)
            )

        # Volatility indicators
        for metric in ['building_permits', 'construction_emp']:
            df[f'{metric}_volatility'] = (
                df.groupby('msa_name')[f'{metric}_growth']
                .transform(lambda x: x.rolling(window=3, min_periods=1).std())
            )

        print(f"  ✓ Created momentum and volatility indicators")
        return df

    def create_relative_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create metrics relative to national/regional benchmarks"""
        print("\nCreating relative benchmark metrics...")

        df = df.copy()

        # National benchmarks (by year)
        national_benchmarks = df.groupby('year').agg({
            'mfg_emp_per_capita': 'mean',
            'constr_emp_per_capita': 'mean',
            'permits_per_capita': 'mean',
            'median_income': 'mean'
        }).add_suffix('_national')

        df = df.merge(national_benchmarks, on='year', how='left')

        # Calculate relative ratios
        df['mfg_vs_national'] = (
            df['mfg_emp_per_capita'] / df['mfg_emp_per_capita_national']
        )
        df['constr_vs_national'] = (
            df['constr_emp_per_capita'] / df['constr_emp_per_capita_national']
        )
        df['permits_vs_national'] = (
            df['permits_per_capita'] / df['permits_per_capita_national']
        )
        df['income_vs_national'] = (
            df['median_income'] / df['median_income_national']
        )

        # Regional benchmarks
        regional_benchmarks = df.groupby(['year', 'census_region']).agg({
            'demand_intensity_score': 'mean'
        }).rename(columns={'demand_intensity_score': 'demand_intensity_regional'})

        df = df.merge(regional_benchmarks, on=['year', 'census_region'], how='left')
        df['demand_vs_regional'] = (
            df['demand_intensity_score'] / df['demand_intensity_regional']
        )

        print(f"  ✓ Created national and regional benchmark metrics")
        return df

    def create_steel_demand_proxy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create proxy measure for actual steel demand
        This serves as target variable for predictive models
        """
        print("\nCreating steel demand proxy...")

        df = df.copy()

        # Weighted combination of steel-intensive activities
        # Weights based on typical steel consumption patterns
        df['steel_demand_proxy'] = (
            0.25 * df['manufacturing_emp'] +          # Manufacturing plants
            0.20 * df['construction_emp'] +           # Construction projects
            0.30 * df['building_permits'] +           # Future construction
            0.15 * df['infra_spending_millions'] +    # Infrastructure
            0.10 * df['population'] / 1000            # General market size
        )

        # Normalize to 0-100 scale per year (accounts for inflation/growth)
        df['steel_demand_index'] = df.groupby('year')['steel_demand_proxy'].transform(
            lambda x: ((x - x.min()) / (x.max() - x.min()) * 100) if x.max() > x.min() else 50
        )

        print(f"  ✓ Created steel demand proxy and index")
        return df

    def select_modeling_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Select and organize features for modeling"""
        print("\nSelecting modeling features...")

        # Core demographic features
        demographic_features = [
            'population',
            'median_income',
            'population_growth',
        ]

        # Employment features
        employment_features = [
            'manufacturing_emp',
            'construction_emp',
            'mfg_emp_per_capita',
            'constr_emp_per_capita',
        ]

        # Construction activity features
        construction_features = [
            'building_permits',
            'permits_per_capita',
            'building_permits_growth',
        ]

        # Infrastructure features
        infra_features = [
            'infra_spending_millions',
            'infra_spending_per_capita',
        ]

        # Composite indices
        index_features = [
            'manufacturing_intensity_index',
            'construction_momentum_index',
            'demographic_tailwind_index',
            'demand_intensity_score',
        ]

        # Interaction features
        interaction_features = [
            'mfg_constr_interaction',
            'income_permits_interaction',
            'pop_mfg_interaction',
        ]

        # All modeling features
        modeling_features = (
            demographic_features +
            employment_features +
            construction_features +
            infra_features +
            index_features +
            interaction_features
        )

        # Add available lagged features
        lagged_features = [col for col in df.columns if 'lag' in col and 'lag1' in col]
        modeling_features.extend(lagged_features[:5])  # Limit to avoid multicollinearity

        # Remove any missing features
        modeling_features = [f for f in modeling_features if f in df.columns]

        print(f"  ✓ Selected {len(modeling_features)} features for modeling")
        return df, modeling_features

    def save_feature_data(self, df: pd.DataFrame, feature_list: List[str]):
        """Save engineered features"""
        print("\nSaving feature data...")

        # Save full feature set
        df.to_parquet(self.features_dir / 'msa_features_full.parquet', index=False)
        df.to_csv(self.features_dir / 'msa_features_full.csv', index=False)
        print(f"  ✓ Saved full feature set: {len(df.columns)} columns")

        # Save feature metadata
        feature_metadata = pd.DataFrame({
            'feature_name': feature_list,
            'feature_type': ['modeling'] * len(feature_list)
        })
        feature_metadata.to_csv(self.features_dir / 'feature_list.csv', index=False)
        print(f"  ✓ Saved feature metadata: {len(feature_list)} modeling features")

        # Save latest year data for clustering
        latest_year = df['year'].max()
        df_latest = df[df['year'] == latest_year].copy()
        df_latest.to_csv(self.features_dir / 'msa_features_latest.csv', index=False)
        print(f"  ✓ Saved latest year ({latest_year}) data for clustering")

def main():
    """Main execution function"""
    print("=" * 70)
    print("Steel Distribution Analysis - Feature Engineering")
    print("=" * 70)

    engineer = FeatureEngineer(CLEAN_DATA_DIR, FEATURES_DIR)

    # Load data
    df = engineer.load_clean_data()

    # Engineer features
    df = engineer.create_lagged_features(df)
    df = engineer.create_rolling_features(df)
    df = engineer.create_interaction_features(df)
    df = engineer.create_industry_concentration_index(df)
    df = engineer.create_momentum_indicators(df)
    df = engineer.create_relative_metrics(df)
    df = engineer.create_steel_demand_proxy(df)

    # Select modeling features
    df, feature_list = engineer.select_modeling_features(df)

    # Save
    engineer.save_feature_data(df, feature_list)

    print("\n" + "=" * 70)
    print("Feature engineering complete!")
    print(f"Total features: {len(df.columns)}")
    print(f"Modeling features: {len(feature_list)}")
    print(f"Records: {len(df)}")
    print(f"Features saved to: {FEATURES_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
