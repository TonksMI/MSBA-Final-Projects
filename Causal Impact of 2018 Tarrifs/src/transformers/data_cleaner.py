"""
Data cleaning and standardization module.

Transforms raw data from various sources into standardized format.
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional
import sys
sys.path.append('..')
from utils.helpers import (
    parse_hs_code,
    normalize_country_names,
    convert_to_metric_tons,
)

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and standardize raw data."""

    def __init__(self):
        """Initialize data cleaner."""
        pass

    def clean_census_data(self,
                         raw_path: str,
                         output_path: str,
                         hs_level: int = 6) -> pd.DataFrame:
        """
        Clean Census import data.

        Args:
            raw_path: Path to raw Census data
            output_path: Path to save cleaned data
            hs_level: HS code level (default 6)

        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Cleaning Census data from {raw_path}")

        try:
            df = pd.read_csv(raw_path)
        except FileNotFoundError:
            logger.error(f"File not found: {raw_path}")
            return pd.DataFrame()

        # Standardize column names
        df = df.rename(columns={
            'GEN_VAL_MO': 'import_value_usd',
            'GEN_QY1_MO': 'import_quantity_kg',
            'CTY_NAME': 'country',
            'COMM_LVL': 'hs_code',
        })

        # Parse dates
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()
        elif 'time' in df.columns:
            df['date'] = pd.to_datetime(df['time']).dt.to_period('M').dt.to_timestamp()

        # Standardize HS codes
        if 'hs_code' in df.columns:
            df['hs6'] = df['hs_code'].apply(lambda x: parse_hs_code(x, level=hs_level))
        elif 'hs6' in df.columns:
            df['hs6'] = df['hs6'].apply(lambda x: parse_hs_code(x, level=hs_level))

        # Standardize country names
        if 'country' in df.columns:
            df['country'] = df['country'].apply(normalize_country_names)

        # Convert quantities to metric tons
        if 'import_quantity_kg' in df.columns:
            df['import_volume_mt'] = df['import_quantity_kg'].apply(
                lambda x: convert_to_metric_tons(x, 'kg')
            )

        # Select and order columns
        columns = [
            'date', 'country', 'hs6', 'import_value_usd',
            'import_volume_mt'
        ]
        df = df[[col for col in columns if col in df.columns]]

        # Remove duplicates
        df = df.drop_duplicates(subset=['date', 'country', 'hs6'])

        # Remove null values in key columns
        df = df.dropna(subset=['date', 'country', 'hs6'])

        # Sort
        df = df.sort_values(['date', 'country', 'hs6']).reset_index(drop=True)

        # Save
        df.to_csv(output_path, index=False)
        logger.info(f"Cleaned {len(df)} records saved to {output_path}")

        return df

    def clean_bls_data(self,
                      raw_path: str,
                      output_path: str) -> pd.DataFrame:
        """
        Clean BLS price index data.

        Args:
            raw_path: Path to raw BLS data
            output_path: Path to save cleaned data

        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Cleaning BLS data from {raw_path}")

        try:
            df = pd.read_csv(raw_path)
        except FileNotFoundError:
            logger.error(f"File not found: {raw_path}")
            return pd.DataFrame()

        # Parse dates
        df['date'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()

        # Pivot series into columns
        if 'series_id' in df.columns:
            df_pivot = df.pivot(index='date', columns='series_id', values='value')
            df_pivot = df_pivot.reset_index()

            # Rename columns to meaningful names
            series_mapping = {
                'IR33112': 'import_price_index',
                'PCU33110033110': 'ppi_steel',
                'WPU101': 'ppi_steel_mill',
            }

            df_pivot = df_pivot.rename(columns=series_mapping)
            df = df_pivot

        # Forward fill missing values (price indexes often have gaps)
        price_cols = [col for col in df.columns if 'price' in col.lower() or 'ppi' in col.lower()]
        df[price_cols] = df[price_cols].fillna(method='ffill')

        # Sort
        df = df.sort_values('date').reset_index(drop=True)

        # Save
        df.to_csv(output_path, index=False)
        logger.info(f"Cleaned {len(df)} records saved to {output_path}")

        return df

    def clean_fred_data(self,
                       raw_path: str,
                       output_path: str) -> pd.DataFrame:
        """
        Clean FRED macro data.

        Args:
            raw_path: Path to raw FRED data
            output_path: Path to save cleaned data

        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Cleaning FRED data from {raw_path}")

        try:
            df = pd.read_csv(raw_path)
        except FileNotFoundError:
            logger.error(f"File not found: {raw_path}")
            return pd.DataFrame()

        # Parse dates
        df['date'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()

        # Forward fill missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(method='ffill')

        # Sort
        df = df.sort_values('date').reset_index(drop=True)

        # Save
        df.to_csv(output_path, index=False)
        logger.info(f"Cleaned {len(df)} records saved to {output_path}")

        return df

    def clean_tariff_data(self,
                         raw_path: str,
                         output_path: str,
                         exemptions_path: Optional[str] = None) -> pd.DataFrame:
        """
        Clean USITC tariff schedule data.

        Args:
            raw_path: Path to raw tariff data
            output_path: Path to save cleaned data
            exemptions_path: Optional path to country exemptions

        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Cleaning tariff data from {raw_path}")

        try:
            df = pd.read_csv(raw_path)
        except FileNotFoundError:
            logger.error(f"File not found: {raw_path}")
            return pd.DataFrame()

        # Parse dates
        df['date'] = pd.to_datetime(df['date']).dt.to_period('M').dt.to_timestamp()

        # Standardize HS codes
        if 'hs6' in df.columns:
            df['hs6'] = df['hs6'].apply(lambda x: parse_hs_code(x, level=6))

        # Ensure tariff rates are numeric
        rate_cols = [col for col in df.columns if 'rate' in col.lower()]
        for col in rate_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Apply country exemptions if provided
        if exemptions_path:
            exemptions = pd.read_csv(exemptions_path)
            # This would require country dimension in tariff data
            # Placeholder for exemption logic
            logger.info("Exemption data loaded but not applied (requires country-level tariffs)")

        # Sort
        df = df.sort_values(['date', 'hs6']).reset_index(drop=True)

        # Save
        df.to_csv(output_path, index=False)
        logger.info(f"Cleaned {len(df)} records saved to {output_path}")

        return df

    def validate_data_quality(self, df: pd.DataFrame, dataset_name: str) -> Dict:
        """
        Validate data quality and return report.

        Args:
            df: DataFrame to validate
            dataset_name: Name of dataset

        Returns:
            Dictionary with validation results
        """
        report = {
            'dataset': dataset_name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'date_range': (df['date'].min(), df['date'].max()) if 'date' in df.columns else None,
        }

        # Log issues
        if report['duplicates'] > 0:
            logger.warning(f"{dataset_name}: {report['duplicates']} duplicate rows found")

        missing_pct = {k: v / len(df) * 100 for k, v in report['missing_values'].items() if v > 0}
        if missing_pct:
            logger.warning(f"{dataset_name}: Missing values: {missing_pct}")

        return report
