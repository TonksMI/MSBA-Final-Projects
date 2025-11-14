#!/usr/bin/env python3
"""
Main orchestration script for steel tariff analysis pipeline.

This script coordinates data collection, cleaning, and panel construction.
"""
import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from config.config import (
    RAW_DATA_DIR,
    CLEAN_DATA_DIR,
    ANALYSIS_DIR,
    START_YEAR,
    END_YEAR,
    STEEL_HS6_CODES,
    CONTROL_HS6_CODES,
    SECTION_232_START,
    CENSUS_API_KEY,
    FRED_API_KEY,
    BLS_API_KEY,
    FRED_SERIES,
)
from collectors.census_collector import CensusTradeCollector
from collectors.bls_collector import BLSCollector
from collectors.fred_collector import FREDCollector
from collectors.usitc_collector import USITCCollector
from transformers.data_cleaner import DataCleaner
from transformers.panel_constructor import PanelConstructor
from utils.helpers import setup_directories

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SteelTariffPipeline:
    """Main pipeline orchestrator."""

    def __init__(self, skip_collection: bool = False):
        """
        Initialize pipeline.

        Args:
            skip_collection: Skip data collection step (use existing raw data)
        """
        self.skip_collection = skip_collection
        self.setup_environment()

    def setup_environment(self):
        """Set up directories and environment."""
        logger.info("Setting up environment")

        # Create directories
        setup_directories([
            RAW_DATA_DIR,
            CLEAN_DATA_DIR,
            ANALYSIS_DIR,
        ])

        # Validate API keys
        if not self.skip_collection:
            self._validate_api_keys()

    def _validate_api_keys(self):
        """Validate that necessary API keys are set."""
        keys = {
            'CENSUS_API_KEY': CENSUS_API_KEY,
            'FRED_API_KEY': FRED_API_KEY,
            'BLS_API_KEY': BLS_API_KEY,
        }

        missing = [k for k, v in keys.items() if not v]

        if missing:
            logger.warning(f"Missing API keys: {missing}")
            logger.warning("Some data sources may use placeholder data")
            logger.info("Set API keys via environment variables or .env file")

    def run_collection(self):
        """Run data collection from all sources."""
        if self.skip_collection:
            logger.info("Skipping data collection")
            return

        logger.info("=" * 60)
        logger.info("STEP 1: DATA COLLECTION")
        logger.info("=" * 60)

        # Census data
        logger.info("Collecting Census import data")
        census_collector = CensusTradeCollector(api_key=CENSUS_API_KEY)
        census_collector.collect_import_data(
            hs_codes=STEEL_HS6_CODES + CONTROL_HS6_CODES,
            start_year=START_YEAR,
            end_year=END_YEAR,
            output_path=RAW_DATA_DIR / "census_imports.csv"
        )

        # BLS data
        logger.info("Collecting BLS price indexes")
        bls_collector = BLSCollector(api_key=BLS_API_KEY)

        import_series = bls_collector.get_import_price_series()
        ppi_series = bls_collector.get_ppi_series()
        all_series = import_series + ppi_series

        bls_collector.collect_price_indexes(
            series_ids=all_series,
            start_year=START_YEAR,
            end_year=END_YEAR,
            output_path=RAW_DATA_DIR / "bls_prices.csv"
        )

        # FRED data
        logger.info("Collecting FRED macro indicators")
        fred_collector = FREDCollector(api_key=FRED_API_KEY)
        fred_collector.collect_macro_indicators(
            series_dict=fred_collector.get_macro_control_series(),
            start_date=f"{START_YEAR}-01-01",
            end_date=f"{END_YEAR}-12-31",
            output_path=RAW_DATA_DIR / "fred_macro.csv"
        )

        # USITC data
        logger.info("Collecting USITC tariff schedules")
        usitc_collector = USITCCollector()

        usitc_collector.collect_tariff_schedules(
            hs_codes=STEEL_HS6_CODES + CONTROL_HS6_CODES,
            years=list(range(START_YEAR, END_YEAR + 1)),
            output_path=RAW_DATA_DIR / "usitc_tariffs.csv"
        )

        usitc_collector.collect_country_exemptions(
            output_path=RAW_DATA_DIR / "country_exemptions.csv"
        )

        usitc_collector.download_hs_descriptions(
            output_path=RAW_DATA_DIR / "hs_descriptions.csv"
        )

        logger.info("Data collection complete")

    def run_cleaning(self):
        """Run data cleaning and standardization."""
        logger.info("=" * 60)
        logger.info("STEP 2: DATA CLEANING")
        logger.info("=" * 60)

        cleaner = DataCleaner()

        # Clean Census data
        logger.info("Cleaning Census data")
        census_clean = cleaner.clean_census_data(
            raw_path=RAW_DATA_DIR / "census_imports.csv",
            output_path=CLEAN_DATA_DIR / "census_clean.csv"
        )
        cleaner.validate_data_quality(census_clean, "Census Imports")

        # Clean BLS data
        logger.info("Cleaning BLS data")
        bls_clean = cleaner.clean_bls_data(
            raw_path=RAW_DATA_DIR / "bls_prices.csv",
            output_path=CLEAN_DATA_DIR / "bls_clean.csv"
        )
        cleaner.validate_data_quality(bls_clean, "BLS Prices")

        # Clean FRED data
        logger.info("Cleaning FRED data")
        fred_clean = cleaner.clean_fred_data(
            raw_path=RAW_DATA_DIR / "fred_macro.csv",
            output_path=CLEAN_DATA_DIR / "fred_clean.csv"
        )
        cleaner.validate_data_quality(fred_clean, "FRED Macro")

        # Clean tariff data
        logger.info("Cleaning tariff data")
        tariff_clean = cleaner.clean_tariff_data(
            raw_path=RAW_DATA_DIR / "usitc_tariffs.csv",
            output_path=CLEAN_DATA_DIR / "tariffs_clean.csv",
            exemptions_path=RAW_DATA_DIR / "country_exemptions.csv"
        )
        cleaner.validate_data_quality(tariff_clean, "USITC Tariffs")

        logger.info("Data cleaning complete")

    def run_panel_construction(self):
        """Run panel construction."""
        logger.info("=" * 60)
        logger.info("STEP 3: PANEL CONSTRUCTION")
        logger.info("=" * 60)

        constructor = PanelConstructor(
            steel_hs_codes=STEEL_HS6_CODES,
            control_hs_codes=CONTROL_HS6_CODES,
            treatment_date=SECTION_232_START
        )

        # Build panel
        panel = constructor.build_panel(
            census_path=CLEAN_DATA_DIR / "census_clean.csv",
            tariff_path=CLEAN_DATA_DIR / "tariffs_clean.csv",
            bls_path=CLEAN_DATA_DIR / "bls_clean.csv",
            fred_path=CLEAN_DATA_DIR / "fred_clean.csv",
            output_path=CLEAN_DATA_DIR / "steel_panel.parquet",
            start_date=f"{START_YEAR}-01",
            end_date=f"{END_YEAR}-12"
        )

        # Generate summary statistics
        logger.info("Generating summary statistics")
        constructor.generate_summary_statistics(
            panel=panel,
            output_path=ANALYSIS_DIR / "summary_statistics.txt"
        )

        logger.info("Panel construction complete")

    def run_full_pipeline(self):
        """Run complete pipeline."""
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("STARTING STEEL TARIFF ANALYSIS PIPELINE")
        logger.info("=" * 60)

        try:
            self.run_collection()
            self.run_cleaning()
            self.run_panel_construction()

            logger.info("=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"Total time: {datetime.now() - start_time}")
            logger.info("=" * 60)

            logger.info(f"\nOutputs:")
            logger.info(f"  - Raw data: {RAW_DATA_DIR}")
            logger.info(f"  - Clean data: {CLEAN_DATA_DIR}")
            logger.info(f"  - Panel: {CLEAN_DATA_DIR / 'steel_panel.parquet'}")
            logger.info(f"  - Analysis: {ANALYSIS_DIR}")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Steel Tariff Analysis Pipeline'
    )
    parser.add_argument(
        '--skip-collection',
        action='store_true',
        help='Skip data collection step (use existing raw data)'
    )
    parser.add_argument(
        '--collection-only',
        action='store_true',
        help='Run only data collection'
    )
    parser.add_argument(
        '--cleaning-only',
        action='store_true',
        help='Run only data cleaning'
    )
    parser.add_argument(
        '--panel-only',
        action='store_true',
        help='Run only panel construction'
    )

    args = parser.parse_args()

    pipeline = SteelTariffPipeline(skip_collection=args.skip_collection)

    if args.collection_only:
        pipeline.run_collection()
    elif args.cleaning_only:
        pipeline.run_cleaning()
    elif args.panel_only:
        pipeline.run_panel_construction()
    else:
        pipeline.run_full_pipeline()


if __name__ == '__main__':
    main()
