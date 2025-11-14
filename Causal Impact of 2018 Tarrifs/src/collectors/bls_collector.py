"""
BLS (Bureau of Labor Statistics) data collector.

Collects:
- Import Price Indexes (country-of-origin steel prices)
- Producer Price Indexes (domestic steel prices, downstream effects)
"""
import pandas as pd
import requests
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class BLSCollector:
    """Collector for BLS price index data."""

    def __init__(self, api_key: str = ""):
        """
        Initialize BLS collector.

        Args:
            api_key: BLS API key (optional, but increases rate limits)
        """
        self.api_key = api_key
        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def collect_price_indexes(self,
                             series_ids: List[str],
                             start_year: int,
                             end_year: int,
                             output_path: str) -> pd.DataFrame:
        """
        Collect price index data from BLS.

        Args:
            series_ids: List of BLS series IDs
            start_year: Starting year
            end_year: Ending year
            output_path: Path to save raw data

        Returns:
            DataFrame with price index data
        """
        logger.info(f"Collecting BLS data for {len(series_ids)} series")

        all_data = []

        # BLS API allows max 50 series per request, 20 years per request
        for i in range(0, len(series_ids), 50):
            batch = series_ids[i:i + 50]

            for year_start in range(start_year, end_year + 1, 20):
                year_end = min(year_start + 19, end_year)

                try:
                    data = self._fetch_bls_data(batch, year_start, year_end)
                    if data is not None:
                        all_data.append(data)
                except Exception as e:
                    logger.error(f"Error collecting BLS data: {e}")
                    continue

        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {len(df)} records to {output_path}")
            return df
        else:
            logger.warning("No BLS data collected")
            return pd.DataFrame()

    def _fetch_bls_data(self,
                       series_ids: List[str],
                       start_year: int,
                       end_year: int) -> pd.DataFrame:
        """
        Fetch data from BLS API.

        Args:
            series_ids: BLS series IDs
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with BLS data
        """
        headers = {'Content-type': 'application/json'}
        payload = {
            "seriesid": series_ids,
            "startyear": str(start_year),
            "endyear": str(end_year),
        }

        if self.api_key:
            payload["registrationkey"] = self.api_key

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            json_data = response.json()

            if json_data['status'] == 'REQUEST_SUCCEEDED':
                records = []

                for series in json_data['Results']['series']:
                    series_id = series['seriesID']

                    for item in series['data']:
                        records.append({
                            'series_id': series_id,
                            'year': int(item['year']),
                            'period': item['period'],
                            'value': float(item['value']) if item['value'] != '-' else None,
                            'date': self._parse_bls_date(item['year'], item['period'])
                        })

                return pd.DataFrame(records)
            else:
                logger.error(f"BLS API error: {json_data.get('message', 'Unknown error')}")
                return None

        except Exception as e:
            logger.error(f"Error fetching BLS data: {e}")
            return None

    @staticmethod
    def _parse_bls_date(year: str, period: str) -> str:
        """
        Parse BLS date format to YYYY-MM.

        Args:
            year: Year string
            period: Period string (M01-M12 or Q01-Q04)

        Returns:
            Date string in YYYY-MM format
        """
        if period.startswith('M'):
            month = period[1:]
            return f"{year}-{month}"
        elif period.startswith('Q'):
            quarter = int(period[1])
            month = (quarter - 1) * 3 + 1
            return f"{year}-{month:02d}"
        else:
            return f"{year}-01"

    def get_import_price_series(self) -> List[str]:
        """
        Get relevant import price index series IDs.

        Returns:
            List of BLS series IDs
        """
        # Import Price Indexes for steel products
        # Note: These are example series IDs - verify with actual BLS database
        return [
            "IR33112",  # Import price index - Steel mill products
            "IR33111",  # Import price index - Iron and steel
            # Add more specific series as needed
        ]

    def get_ppi_series(self) -> List[str]:
        """
        Get relevant PPI series IDs.

        Returns:
            List of BLS series IDs
        """
        # Producer Price Indexes for steel and downstream products
        return [
            "PCU33110033110",  # PPI - Steel mill products
            "PCU331111331111",  # PPI - Iron and steel mills
            "PCU332",  # PPI - Fabricated metal products (downstream)
            "WPU101",  # PPI - Steel mill products
            # Add more series as needed
        ]
