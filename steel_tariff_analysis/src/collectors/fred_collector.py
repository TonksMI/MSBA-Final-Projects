"""
FRED (Federal Reserve Economic Data) collector.

Collects macro control variables:
- Oil prices (WTI)
- Global PMI
- Industrial production
- Other macro indicators
"""
import pandas as pd
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FREDCollector:
    """Collector for FRED macro data."""

    def __init__(self, api_key: str):
        """
        Initialize FRED collector.

        Args:
            api_key: FRED API key
        """
        self.api_key = api_key
        try:
            from fredapi import Fred
            self.fred = Fred(api_key=api_key)
        except ImportError:
            logger.warning("fredapi not installed. Install with: pip install fredapi")
            self.fred = None

    def collect_macro_indicators(self,
                                 series_dict: Dict[str, str],
                                 start_date: str,
                                 end_date: str,
                                 output_path: str) -> pd.DataFrame:
        """
        Collect macro indicator data from FRED.

        Args:
            series_dict: Dictionary mapping variable names to FRED series IDs
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_path: Path to save raw data

        Returns:
            DataFrame with macro indicators
        """
        if self.fred is None:
            logger.error("FRED API not available")
            return self._create_synthetic_macro_data(start_date, end_date, output_path)

        logger.info(f"Collecting FRED data for {len(series_dict)} series")

        all_series = {}

        for var_name, series_id in series_dict.items():
            try:
                logger.info(f"Fetching {var_name} ({series_id})")
                data = self.fred.get_series(series_id, start_date, end_date)
                all_series[var_name] = data
            except Exception as e:
                logger.error(f"Error fetching {var_name}: {e}")
                continue

        if all_series:
            # Combine all series into single DataFrame
            df = pd.DataFrame(all_series)
            df.index.name = 'date'
            df = df.reset_index()

            # Convert to monthly frequency if needed
            df['date'] = pd.to_datetime(df['date'])
            df = df.groupby(pd.Grouper(key='date', freq='MS')).mean().reset_index()

            df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(df)} records to {output_path}")
            return df
        else:
            logger.warning("No FRED data collected, using synthetic data")
            return self._create_synthetic_macro_data(start_date, end_date, output_path)

    def _create_synthetic_macro_data(self,
                                    start_date: str,
                                    end_date: str,
                                    output_path: str) -> pd.DataFrame:
        """
        Create synthetic macro data for testing.

        Args:
            start_date: Start date
            end_date: End date
            output_path: Output path

        Returns:
            Synthetic macro DataFrame
        """
        logger.warning("Creating synthetic macro data - replace with actual FRED data")

        dates = pd.date_range(start=start_date, end=end_date, freq='MS')

        df = pd.DataFrame({
            'date': dates,
            'oil_price': 50 + pd.Series(range(len(dates))) * 0.1,  # Trending oil price
            'global_pmi': 50 + pd.Series([i % 10 for i in range(len(dates))]),  # Cyclical PMI
            'industrial_production': 100 + pd.Series(range(len(dates))) * 0.05,
        })

        df.to_csv(output_path, index=False)
        return df

    def get_steel_production_series(self) -> List[str]:
        """
        Get FRED series IDs for steel production.

        Returns:
            List of series IDs
        """
        return [
            "IPG3311A2N",  # Industrial Production: Steel
            "IPN3311A2SQ",  # Industrial Production: Iron and Steel Mills
        ]

    def get_macro_control_series(self) -> Dict[str, str]:
        """
        Get macro control series.

        Returns:
            Dictionary of variable names and series IDs
        """
        return {
            'oil_price': 'DCOILWTICO',  # WTI Crude Oil Price
            'usd_index': 'DTWEXBGS',  # Trade Weighted U.S. Dollar Index
            'industrial_production': 'INDPRO',  # Industrial Production Index
            'capacity_utilization': 'TCU',  # Capacity Utilization
        }
