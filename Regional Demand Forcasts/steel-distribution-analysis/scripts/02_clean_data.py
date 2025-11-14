"""
Data Cleaning and Transformation Pipeline
Processes raw data into analysis-ready MSA-level panel
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

# Set up paths
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw'
CLEAN_DATA_DIR = BASE_DIR / 'data' / 'clean'
CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)

class DataCleaner:
    """Handles data cleaning and transformation"""

    def __init__(self, raw_dir: Path, clean_dir: Path):
        self.raw_dir = raw_dir
        self.clean_dir = clean_dir

    def load_sample_data(self) -> pd.DataFrame:
        """Load the sample MSA panel data"""
        print("Loading sample MSA data...")
        df = pd.read_csv(self.raw_dir / 'sample_msa_panel.csv')
        print(f"  Loaded {len(df)} records across {df['year'].nunique()} years")
        return df

    def normalize_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize employment and spending metrics per capita"""
        print("\nNormalizing metrics per capita...")

        df = df.copy()

        # Per capita calculations
        df['mfg_emp_per_capita'] = (df['manufacturing_emp'] / df['population']) * 1000
        df['constr_emp_per_capita'] = (df['construction_emp'] / df['population']) * 1000
        df['permits_per_capita'] = (df['building_permits'] / df['population']) * 1000
        df['infra_spending_per_capita'] = (df['infra_spending_millions'] * 1e6) / df['population']

        print(f"  ✓ Created {4} per-capita metrics")
        return df

    def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate year-over-year growth rates"""
        print("\nCalculating growth rates...")

        df = df.copy()
        df = df.sort_values(['msa_name', 'year'])

        # Growth rate calculations
        for metric in ['manufacturing_emp', 'construction_emp', 'building_permits', 'population']:
            df[f'{metric}_growth'] = df.groupby('msa_name')[metric].pct_change()

        # Rolling averages for smoothing
        for metric in ['building_permits', 'infra_spending_millions']:
            df[f'{metric}_3yr_avg'] = (
                df.groupby('msa_name')[metric]
                .transform(lambda x: x.rolling(window=3, min_periods=1).mean())
            )

        print(f"  ✓ Created growth rates and rolling averages")
        return df

    def create_composite_indices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create composite demand intensity indices"""
        print("\nCreating composite indices...")

        df = df.copy()

        # Manufacturing Intensity Index
        # Normalize to 0-100 scale
        mfg_norm = (df['mfg_emp_per_capita'] - df['mfg_emp_per_capita'].min()) / \
                   (df['mfg_emp_per_capita'].max() - df['mfg_emp_per_capita'].min())
        df['manufacturing_intensity_index'] = mfg_norm * 100

        # Construction Momentum Index
        # Combines construction employment + building permits growth
        constr_norm = (df['constr_emp_per_capita'] - df['constr_emp_per_capita'].min()) / \
                      (df['constr_emp_per_capita'].max() - df['constr_emp_per_capita'].min())
        permits_norm = (df['permits_per_capita'] - df['permits_per_capita'].min()) / \
                       (df['permits_per_capita'].max() - df['permits_per_capita'].min())
        df['construction_momentum_index'] = ((constr_norm + permits_norm) / 2) * 100

        # Demographic Tailwind Index
        # Population growth + income level
        pop_growth_norm = df.groupby('year')['population_growth'].transform(
            lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0
        )
        income_norm = (df['median_income'] - df['median_income'].min()) / \
                      (df['median_income'].max() - df['median_income'].min())
        df['demographic_tailwind_index'] = ((pop_growth_norm + income_norm) / 2) * 100

        # Overall Demand Intensity Score
        # Weighted combination of all indices
        df['demand_intensity_score'] = (
            0.40 * df['manufacturing_intensity_index'] +
            0.35 * df['construction_momentum_index'] +
            0.25 * df['demographic_tailwind_index']
        )

        print(f"  ✓ Created 4 composite indices")
        return df

    def add_regional_classifications(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add regional and state-level classifications"""
        print("\nAdding regional classifications...")

        df = df.copy()

        # Define census regions (simplified)
        region_map = {
            'NY': 'Northeast', 'PA': 'Northeast', 'MA': 'Northeast',
            'IL': 'Midwest', 'MI': 'Midwest', 'MN': 'Midwest',
            'TX': 'South', 'FL': 'South', 'GA': 'South',
            'CA': 'West', 'WA': 'West', 'AZ': 'West', 'CO': 'West'
        }

        df['census_region'] = df['state'].map(region_map)

        # Define metro size categories based on population
        df['metro_size_category'] = pd.cut(
            df['population'],
            bins=[0, 2e6, 5e6, 10e6, float('inf')],
            labels=['Small', 'Medium', 'Large', 'Mega']
        )

        print(f"  ✓ Added regional classifications")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with appropriate strategies"""
        print("\nHandling missing values...")

        df = df.copy()
        missing_before = df.isnull().sum().sum()

        # Forward fill for time series gaps
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df.groupby('msa_name')[col].fillna(method='ffill')

        # Backward fill for remaining gaps
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df.groupby('msa_name')[col].fillna(method='bfill')

        # Fill remaining with median
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)

        missing_after = df.isnull().sum().sum()
        print(f"  ✓ Reduced missing values: {missing_before} → {missing_after}")
        return df

    def save_clean_data(self, df: pd.DataFrame, filename: str):
        """Save cleaned data in multiple formats"""
        print(f"\nSaving cleaned data...")

        # Save as CSV
        csv_path = self.clean_dir / f'{filename}.csv'
        df.to_csv(csv_path, index=False)
        print(f"  ✓ CSV: {csv_path}")

        # Save as Parquet (more efficient for large datasets)
        parquet_path = self.clean_dir / f'{filename}.parquet'
        df.to_parquet(parquet_path, index=False)
        print(f"  ✓ Parquet: {parquet_path}")

    def generate_summary_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate summary statistics for the cleaned data"""
        print("\nGenerating summary statistics...")

        summary = df.groupby('year').agg({
            'msa_name': 'count',
            'population': ['mean', 'median', 'sum'],
            'manufacturing_emp': ['mean', 'sum'],
            'construction_emp': ['mean', 'sum'],
            'building_permits': ['mean', 'sum'],
            'demand_intensity_score': ['mean', 'std', 'min', 'max']
        }).round(2)

        summary_path = self.clean_dir / 'summary_statistics.csv'
        summary.to_csv(summary_path)
        print(f"  ✓ Summary stats: {summary_path}")

        return summary

def main():
    """Main execution function"""
    print("=" * 70)
    print("Steel Distribution Analysis - Data Cleaning Pipeline")
    print("=" * 70)

    cleaner = DataCleaner(RAW_DATA_DIR, CLEAN_DATA_DIR)

    # Load sample data
    df = cleaner.load_sample_data()

    # Clean and transform
    df = cleaner.normalize_metrics(df)
    df = cleaner.calculate_growth_rates(df)
    df = cleaner.create_composite_indices(df)
    df = cleaner.add_regional_classifications(df)
    df = cleaner.handle_missing_values(df)

    # Save cleaned data
    cleaner.save_clean_data(df, 'msa_panel_clean')

    # Generate summary
    summary = cleaner.generate_summary_stats(df)
    print("\n" + "=" * 70)
    print("Summary Statistics by Year:")
    print(summary)

    print("\n" + "=" * 70)
    print("Data cleaning complete!")
    print(f"Clean data saved to: {CLEAN_DATA_DIR}")
    print(f"Total records: {len(df)}")
    print(f"MSAs: {df['msa_name'].nunique()}")
    print(f"Years: {df['year'].min()} - {df['year'].max()}")
    print("=" * 70)

if __name__ == "__main__":
    main()
