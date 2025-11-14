"""
Panel construction module.

Merges cleaned data sources into final panel structure:
panel: (country × HS code × month), 2000–2025
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional
import sys
sys.path.append('..')
from utils.helpers import (
    create_treatment_indicator,
    create_post_treatment_indicator,
    calculate_import_volume_change,
    merge_with_lag,
    winsorize_outliers,
)

logger = logging.getLogger(__name__)


class PanelConstructor:
    """Construct panel dataset from cleaned data sources."""

    def __init__(self,
                 steel_hs_codes: List[str],
                 control_hs_codes: List[str],
                 treatment_date: str = "2018-03"):
        """
        Initialize panel constructor.

        Args:
            steel_hs_codes: List of Section 232-affected HS6 codes
            control_hs_codes: List of control HS6 codes
            treatment_date: Section 232 treatment start date (YYYY-MM)
        """
        self.steel_hs_codes = steel_hs_codes
        self.control_hs_codes = control_hs_codes
        self.treatment_date = treatment_date

    def build_panel(self,
                   census_path: str,
                   tariff_path: str,
                   bls_path: str,
                   fred_path: str,
                   output_path: str,
                   start_date: str = "2000-01",
                   end_date: str = "2025-12") -> pd.DataFrame:
        """
        Build complete panel dataset.

        Args:
            census_path: Path to cleaned Census data
            tariff_path: Path to cleaned tariff data
            bls_path: Path to cleaned BLS data
            fred_path: Path to cleaned FRED data
            output_path: Path to save final panel
            start_date: Panel start date
            end_date: Panel end date

        Returns:
            Panel DataFrame
        """
        logger.info("Building panel dataset")

        # Load cleaned data
        logger.info("Loading cleaned datasets")
        census_df = pd.read_csv(census_path, parse_dates=['date'])
        tariff_df = pd.read_csv(tariff_path, parse_dates=['date'])
        bls_df = pd.read_csv(bls_path, parse_dates=['date'])
        fred_df = pd.read_csv(fred_path, parse_dates=['date'])

        # Filter date range
        census_df = self._filter_date_range(census_df, start_date, end_date)

        # Create base panel structure
        logger.info("Creating panel structure")
        panel = self._create_panel_structure(census_df)

        # Merge tariff data
        logger.info("Merging tariff data")
        panel = self._merge_tariff_data(panel, tariff_df)

        # Merge price indexes
        logger.info("Merging price indexes")
        panel = self._merge_price_data(panel, bls_df)

        # Merge macro controls
        logger.info("Merging macro controls")
        panel = self._merge_macro_data(panel, fred_df)

        # Create treatment indicators
        logger.info("Creating treatment indicators")
        panel = self._create_indicators(panel)

        # Calculate derived variables
        logger.info("Calculating derived variables")
        panel = self._calculate_derived_variables(panel)

        # Clean and validate
        logger.info("Final cleaning and validation")
        panel = self._final_cleaning(panel)

        # Save panel
        logger.info(f"Saving panel to {output_path}")
        panel.to_parquet(output_path, index=False, compression='snappy')

        # Also save as CSV for inspection
        csv_path = output_path.replace('.parquet', '.csv')
        panel.head(10000).to_csv(csv_path, index=False)
        logger.info(f"Sample saved to {csv_path}")

        logger.info(f"Panel construction complete: {len(panel)} rows, {len(panel.columns)} columns")

        return panel

    def _filter_date_range(self,
                          df: pd.DataFrame,
                          start_date: str,
                          end_date: str) -> pd.DataFrame:
        """Filter DataFrame to date range."""
        df['date'] = pd.to_datetime(df['date'])
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        return df[mask].copy()

    def _create_panel_structure(self, census_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create base panel structure from import data.

        Args:
            census_df: Cleaned Census import data

        Returns:
            Base panel DataFrame
        """
        # Start with import data (country × HS6 × month)
        panel = census_df.copy()

        # Ensure complete panel (fill in missing combinations)
        # Create all combinations of date × country × hs6
        dates = panel['date'].unique()
        countries = panel['country'].unique()
        hs_codes = panel['hs6'].unique()

        # This can create a very large panel, so we limit to observed combinations
        # Uncomment below to create complete panel:
        # from itertools import product
        # full_index = pd.DataFrame(
        #     list(product(dates, countries, hs_codes)),
        #     columns=['date', 'country', 'hs6']
        # )
        # panel = pd.merge(full_index, panel, on=['date', 'country', 'hs6'], how='left')

        # Fill zeros for missing import values
        panel['import_value_usd'] = panel['import_value_usd'].fillna(0)
        panel['import_volume_mt'] = panel['import_volume_mt'].fillna(0)

        return panel

    def _merge_tariff_data(self,
                          panel: pd.DataFrame,
                          tariff_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge tariff rate data.

        Args:
            panel: Base panel
            tariff_df: Tariff data

        Returns:
            Panel with tariff rates
        """
        # Merge on date × hs6
        panel = pd.merge(
            panel,
            tariff_df[['date', 'hs6', 'effective_rate']],
            on=['date', 'hs6'],
            how='left'
        )

        # Rename and fill missing
        panel = panel.rename(columns={'effective_rate': 'tariff_rate'})
        panel['tariff_rate'] = panel['tariff_rate'].fillna(0)

        return panel

    def _merge_price_data(self,
                         panel: pd.DataFrame,
                         bls_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge price index data.

        Args:
            panel: Panel with tariffs
            bls_df: BLS price data

        Returns:
            Panel with price indexes
        """
        # Merge on date (price indexes are aggregate, not country/HS specific)
        price_cols = [col for col in bls_df.columns if col != 'date']

        panel = pd.merge(
            panel,
            bls_df,
            on='date',
            how='left'
        )

        # Forward fill price indexes
        panel[price_cols] = panel.groupby(['country', 'hs6'])[price_cols].fillna(method='ffill')

        return panel

    def _merge_macro_data(self,
                         panel: pd.DataFrame,
                         fred_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge macro control variables.

        Args:
            panel: Panel with prices
            fred_df: FRED macro data

        Returns:
            Panel with macro controls
        """
        # Merge on date
        macro_cols = [col for col in fred_df.columns if col != 'date']

        panel = pd.merge(
            panel,
            fred_df,
            on='date',
            how='left'
        )

        # Forward fill macro variables
        panel[macro_cols] = panel.groupby(['country', 'hs6'])[macro_cols].fillna(method='ffill')

        return panel

    def _create_indicators(self, panel: pd.DataFrame) -> pd.DataFrame:
        """
        Create treatment and exposure indicators.

        Args:
            panel: Panel with all data

        Returns:
            Panel with indicators
        """
        # Exposure indicator (treated vs control)
        all_treated_codes = self.steel_hs_codes
        panel = create_treatment_indicator(panel, 'hs6', all_treated_codes)

        # Post-treatment indicator
        panel = create_post_treatment_indicator(panel, 'date', self.treatment_date)

        # Interaction term
        panel['treated_post'] = panel['exposure_indicator'] * panel['post_treat']

        return panel

    def _calculate_derived_variables(self, panel: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived variables.

        Args:
            panel: Panel with indicators

        Returns:
            Panel with derived variables
        """
        # Sort panel
        panel = panel.sort_values(['country', 'hs6', 'date'])

        # Import volume changes (YoY)
        panel = calculate_import_volume_change(
            panel,
            group_cols=['country', 'hs6'],
            volume_col='import_volume_mt',
            periods=12
        )

        # Unit values (price per ton)
        panel['unit_value'] = np.where(
            panel['import_volume_mt'] > 0,
            panel['import_value_usd'] / panel['import_volume_mt'],
            np.nan
        )

        # Log transformations for regression
        panel['log_import_volume'] = np.log(panel['import_volume_mt'] + 1)
        panel['log_import_value'] = np.log(panel['import_value_usd'] + 1)
        panel['log_unit_value'] = np.log(panel['unit_value'] + 1)

        # Market share by country (within HS6 × month)
        panel['total_imports_hs6'] = panel.groupby(['date', 'hs6'])['import_volume_mt'].transform('sum')
        panel['country_market_share'] = np.where(
            panel['total_imports_hs6'] > 0,
            panel['import_volume_mt'] / panel['total_imports_hs6'],
            0
        )

        # Lagged variables (for IV and robustness)
        for lag in [1, 3, 6, 12]:
            panel[f'import_volume_lag{lag}'] = panel.groupby(['country', 'hs6'])['import_volume_mt'].shift(lag)
            panel[f'tariff_rate_lag{lag}'] = panel.groupby(['country', 'hs6'])['tariff_rate'].shift(lag)

        return panel

    def _final_cleaning(self, panel: pd.DataFrame) -> pd.DataFrame:
        """
        Final cleaning and validation.

        Args:
            panel: Complete panel

        Returns:
            Cleaned panel
        """
        # Winsorize continuous variables to handle outliers
        continuous_vars = [
            'import_volume_mt', 'import_value_usd', 'unit_value',
            'import_volume_change', 'country_market_share'
        ]

        existing_vars = [var for var in continuous_vars if var in panel.columns]
        panel = winsorize_outliers(panel, existing_vars, lower_percentile=0.01, upper_percentile=0.99)

        # Order columns logically
        id_cols = ['date', 'country', 'hs6']
        treatment_cols = ['exposure_indicator', 'post_treat', 'treated_post']
        outcome_cols = [
            'import_volume_mt', 'import_value_usd', 'unit_value',
            'import_volume_change', 'country_market_share'
        ]
        log_cols = [col for col in panel.columns if col.startswith('log_')]
        lag_cols = [col for col in panel.columns if 'lag' in col]
        control_cols = ['tariff_rate', 'import_price_index', 'ppi_steel', 'oil_price']

        # Get all other columns
        all_specified = set(id_cols + treatment_cols + outcome_cols + log_cols + lag_cols + control_cols)
        other_cols = [col for col in panel.columns if col not in all_specified]

        # Reorder
        ordered_cols = (
            id_cols + treatment_cols + outcome_cols +
            [col for col in control_cols if col in panel.columns] +
            log_cols + lag_cols + other_cols
        )

        panel = panel[[col for col in ordered_cols if col in panel.columns]]

        # Sort
        panel = panel.sort_values(['date', 'country', 'hs6']).reset_index(drop=True)

        return panel

    def generate_summary_statistics(self,
                                   panel: pd.DataFrame,
                                   output_path: str) -> pd.DataFrame:
        """
        Generate summary statistics.

        Args:
            panel: Complete panel
            output_path: Path to save summary stats

        Returns:
            Summary statistics DataFrame
        """
        # Overall summary
        summary = panel.describe()

        # Summary by treatment status
        treated_summary = panel[panel['exposure_indicator'] == 1].describe()
        control_summary = panel[panel['exposure_indicator'] == 0].describe()

        # Summary by period
        pre_summary = panel[panel['post_treat'] == 0].describe()
        post_summary = panel[panel['post_treat'] == 1].describe()

        # Combine summaries
        summary_dict = {
            'overall': summary,
            'treated': treated_summary,
            'control': control_summary,
            'pre_period': pre_summary,
            'post_period': post_summary,
        }

        # Save to CSV
        with open(output_path, 'w') as f:
            for name, df_summary in summary_dict.items():
                f.write(f"\n\n{'='*50}\n{name.upper()}\n{'='*50}\n")
                df_summary.to_csv(f)

        logger.info(f"Summary statistics saved to {output_path}")

        return summary
