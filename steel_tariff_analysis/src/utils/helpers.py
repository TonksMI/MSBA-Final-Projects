"""
Helper functions for data processing and transformation.
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_directories(dirs: List[str]) -> None:
    """Create necessary directories if they don't exist."""
    from pathlib import Path
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    logger.info(f"Directories created/verified: {dirs}")


def convert_to_metric_tons(value: float, unit: str = "kg") -> float:
    """
    Convert various weight units to metric tons.

    Args:
        value: Numeric value
        unit: Unit of measurement (kg, lbs, short_tons)

    Returns:
        Value in metric tons
    """
    conversions = {
        "kg": 0.001,
        "lbs": 0.000453592,
        "short_tons": 0.907185,
        "metric_tons": 1.0,
    }
    return value * conversions.get(unit.lower(), 1.0)


def parse_hs_code(hs_code: str, level: int = 6) -> str:
    """
    Parse and standardize HS codes to specified level.

    Args:
        hs_code: Raw HS code string
        level: Desired HS level (2, 4, 6, 8, 10)

    Returns:
        Standardized HS code
    """
    # Remove any non-numeric characters
    clean_code = ''.join(filter(str.isdigit, str(hs_code)))

    # Pad or truncate to desired level
    if len(clean_code) < level:
        clean_code = clean_code.ljust(level, '0')
    else:
        clean_code = clean_code[:level]

    return clean_code


def create_treatment_indicator(df: pd.DataFrame,
                               hs_code_col: str,
                               treated_codes: List[str]) -> pd.DataFrame:
    """
    Add treatment indicator for Section 232-affected products.

    Args:
        df: DataFrame with HS codes
        hs_code_col: Name of HS code column
        treated_codes: List of HS6 codes subject to Section 232

    Returns:
        DataFrame with exposure_indicator column
    """
    df['exposure_indicator'] = df[hs_code_col].isin(treated_codes).astype(int)
    return df


def create_post_treatment_indicator(df: pd.DataFrame,
                                    date_col: str,
                                    treatment_date: str) -> pd.DataFrame:
    """
    Add post-treatment indicator.

    Args:
        df: DataFrame with dates
        date_col: Name of date column
        treatment_date: Treatment start date (YYYY-MM format)

    Returns:
        DataFrame with post_treat column
    """
    treatment_dt = pd.to_datetime(treatment_date)
    df['post_treat'] = (pd.to_datetime(df[date_col]) >= treatment_dt).astype(int)
    return df


def calculate_import_volume_change(df: pd.DataFrame,
                                   group_cols: List[str],
                                   volume_col: str,
                                   periods: int = 12) -> pd.DataFrame:
    """
    Calculate year-over-year import volume change.

    Args:
        df: Panel DataFrame
        group_cols: Grouping columns (e.g., ['country', 'hs6'])
        volume_col: Import volume column name
        periods: Number of periods for comparison (12 for YoY)

    Returns:
        DataFrame with volume change columns
    """
    df = df.sort_values(group_cols + ['date'])
    df['import_volume_change'] = df.groupby(group_cols)[volume_col].pct_change(periods=periods)
    df['import_volume_diff'] = df.groupby(group_cols)[volume_col].diff(periods=periods)
    return df


def normalize_country_names(country: str) -> str:
    """
    Standardize country names across datasets.

    Args:
        country: Raw country name

    Returns:
        Standardized country name
    """
    country_mapping = {
        "korea, south": "South Korea",
        "korea, republic of": "South Korea",
        "taiwan": "Taiwan",
        "china, peoples republic of": "China",
        "china": "China",
        "germany, federal republic of": "Germany",
        "united kingdom": "United Kingdom",
        "u.k.": "United Kingdom",
    }

    country_lower = country.lower().strip()
    return country_mapping.get(country_lower, country.title())


def merge_with_lag(df1: pd.DataFrame,
                   df2: pd.DataFrame,
                   on: List[str],
                   how: str = 'left',
                   lag_months: int = 0) -> pd.DataFrame:
    """
    Merge two DataFrames with optional time lag.

    Args:
        df1: Left DataFrame
        df2: Right DataFrame
        on: Columns to merge on
        how: Type of merge
        lag_months: Number of months to lag df2

    Returns:
        Merged DataFrame
    """
    if lag_months > 0 and 'date' in df2.columns:
        df2 = df2.copy()
        df2['date'] = pd.to_datetime(df2['date']) + pd.DateOffset(months=lag_months)

    return pd.merge(df1, df2, on=on, how=how)


def winsorize_outliers(df: pd.DataFrame,
                      columns: List[str],
                      lower_percentile: float = 0.01,
                      upper_percentile: float = 0.99) -> pd.DataFrame:
    """
    Winsorize outliers in specified columns.

    Args:
        df: Input DataFrame
        columns: Columns to winsorize
        lower_percentile: Lower percentile threshold
        upper_percentile: Upper percentile threshold

    Returns:
        DataFrame with winsorized values
    """
    df = df.copy()
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            lower = df[col].quantile(lower_percentile)
            upper = df[col].quantile(upper_percentile)
            df[col] = df[col].clip(lower=lower, upper=upper)

    return df
