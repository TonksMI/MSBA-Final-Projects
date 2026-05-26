"""
Data Acquisition Script for Steel Distribution Analysis
Downloads public data from Census, BLS, and other sources
"""

import pandas as pd
import requests
import os
from pathlib import Path
import time
from typing import Dict, List

# Set up paths
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw'
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

class DataDownloader:
    """Handles downloading data from various public sources"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.session = requests.Session()

    def download_census_cbp(self, years: List[int] = [2019, 2020, 2021, 2022]):
        """
        Download County Business Patterns data
        https://www.census.gov/programs-surveys/cbp/data/datasets.html
        """
        print("Downloading County Business Patterns data...")

        for year in years:
            url = f"https://www2.census.gov/programs-surveys/cbp/datasets/{year}/cbp{str(year)[2:]}co.zip"
            output_file = self.data_dir / f"cbp_{year}.zip"

            try:
                print(f"  Downloading CBP {year}...")
                response = self.session.get(url, timeout=300)
                response.raise_for_status()

                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"  ✓ Saved to {output_file}")

            except Exception as e:
                print(f"  ✗ Error downloading CBP {year}: {e}")

            time.sleep(1)  # Be respectful to servers

    def download_census_acs(self, years: List[int] = [2019, 2020, 2021, 2022]):
        """
        Download American Community Survey data
        Note: This is a placeholder - actual implementation requires Census API key
        """
        print("\nDownloading ACS data...")
        print("Note: For production use, implement Census API integration")
        print("  Required: Census API key from https://api.census.gov/data/key_signup.html")
        print("  Tables needed: B01003 (Population), B19013 (Income), B25001 (Housing)")

        # Create placeholder file with instructions
        instructions = """
        ACS Data Download Instructions:

        1. Get API key: https://api.census.gov/data/key_signup.html
        2. Use census Python package or direct API calls
        3. Key tables for steel demand analysis:
           - B01003: Total Population
           - B19013: Median Household Income
           - B25001: Housing Units
           - B08006: Transportation to Work
           - B25024: Units in Structure

        Example API call:
        https://api.census.gov/data/2021/acs/acs5?get=NAME,B01003_001E&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:*&key=YOUR_KEY
        """

        with open(self.data_dir / 'acs_download_instructions.txt', 'w') as f:
            f.write(instructions)

    def download_bls_employment(self):
        """
        Download BLS Regional Employment data
        https://www.bls.gov/cew/downloadable-data-files.htm
        """
        print("\nDownloading BLS employment data...")

        # Example: Download annual average employment by MSA
        # Note: BLS data is large - this is a sample approach

        print("Note: BLS data requires bulk download or API access")
        print("  Resource: https://www.bls.gov/developers/")
        print("  Key series: QCEW (Quarterly Census of Employment and Wages)")

        instructions = """
        BLS Data Download Instructions:

        1. Register at https://data.bls.gov/registrationEngine/
        2. Use BLS API for programmatic access
        3. Key data series:
           - QCEW: County/MSA employment by industry
           - NAICS codes for steel-intensive industries:
             * 23: Construction
             * 31-33: Manufacturing
             * 3312: Steel Product Manufacturing
             * 3315: Foundries
             * 42: Wholesale Trade

        Manual download: https://www.bls.gov/cew/downloadable-data-files.htm
        """

        with open(self.data_dir / 'bls_download_instructions.txt', 'w') as f:
            f.write(instructions)

    def download_building_permits(self):
        """
        Download Building Permits Survey data
        https://www.census.gov/construction/bps/
        """
        print("\nDownloading Building Permits data...")

        try:
            # Download annual building permits by MSA
            url = "https://www2.census.gov/econ/bps/Metro/ma2022a.txt"
            output_file = self.data_dir / "building_permits_2022.txt"

            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"  ✓ Downloaded 2022 building permits")

        except Exception as e:
            print(f"  ✗ Error downloading building permits: {e}")

    def create_sample_data(self):
        """
        Create sample/synthetic data for demonstration purposes
        """
        print("\nCreating sample data for demonstration...")

        # Sample MSA list
        metros = [
            ('New York-Newark-Jersey City, NY-NJ-PA', 'NY'),
            ('Los Angeles-Long Beach-Anaheim, CA', 'CA'),
            ('Chicago-Naperville-Elgin, IL-IN-WI', 'IL'),
            ('Dallas-Fort Worth-Arlington, TX', 'TX'),
            ('Houston-The Woodlands-Sugar Land, TX', 'TX'),
            ('Philadelphia-Camden-Wilmington, PA-NJ-DE-MD', 'PA'),
            ('Atlanta-Sandy Springs-Roswell, GA', 'GA'),
            ('Phoenix-Mesa-Scottsdale, AZ', 'AZ'),
            ('Boston-Cambridge-Newton, MA-NH', 'MA'),
            ('San Francisco-Oakland-Hayward, CA', 'CA'),
            ('Detroit-Warren-Dearborn, MI', 'MI'),
            ('Seattle-Tacoma-Bellevue, WA', 'WA'),
            ('Denver-Aurora-Lakewood, CO', 'CO'),
            ('Minneapolis-St. Paul-Bloomington, MN-WI', 'MN'),
            ('Tampa-St. Petersburg-Clearwater, FL', 'FL'),
        ]

        # Create sample MSA panel data
        import numpy as np
        np.random.seed(42)

        years = [2019, 2020, 2021, 2022, 2023]
        data = []

        for msa, state in metros:
            base_mfg = np.random.randint(50000, 500000)
            base_constr = np.random.randint(30000, 300000)
            base_pop = np.random.randint(1000000, 20000000)

            for year in years:
                growth_factor = 1 + (year - 2019) * np.random.uniform(0.01, 0.05)

                data.append({
                    'msa_name': msa,
                    'state': state,
                    'year': year,
                    'manufacturing_emp': int(base_mfg * growth_factor * np.random.uniform(0.95, 1.05)),
                    'construction_emp': int(base_constr * growth_factor * np.random.uniform(0.90, 1.10)),
                    'population': int(base_pop * growth_factor),
                    'median_income': int(50000 * growth_factor * np.random.uniform(0.9, 1.3)),
                    'building_permits': int(np.random.uniform(5000, 50000) * growth_factor),
                    'infra_spending_millions': np.random.uniform(100, 2000) * growth_factor,
                })

        df = pd.DataFrame(data)
        df.to_csv(self.data_dir / 'sample_msa_panel.csv', index=False)
        print(f"  ✓ Created sample MSA panel data: {len(df)} records")

        # Create sample competitor locations
        competitor_data = []
        for msa, state in metros[:10]:  # Competitors in top 10 metros
            num_facilities = np.random.randint(1, 5)
            for i in range(num_facilities):
                competitor_data.append({
                    'msa_name': msa,
                    'state': state,
                    'competitor_name': np.random.choice(['Steel Dist Co A', 'Steel Dist Co B', 'Steel Dist Co C']),
                    'facility_size': np.random.choice(['Small', 'Medium', 'Large']),
                })

        comp_df = pd.DataFrame(competitor_data)
        comp_df.to_csv(self.data_dir / 'sample_competitor_locations.csv', index=False)
        print(f"  ✓ Created sample competitor data: {len(comp_df)} facilities")

def main():
    """Main execution function"""
    print("=" * 70)
    print("Steel Distribution Analysis - Data Acquisition")
    print("=" * 70)

    downloader = DataDownloader(RAW_DATA_DIR)

    # Download real data where possible
    # downloader.download_census_cbp()  # Uncomment for real CBP data
    downloader.download_census_acs()
    downloader.download_bls_employment()
    # downloader.download_building_permits()  # Uncomment for real permits

    # Create sample data for demonstration
    downloader.create_sample_data()

    print("\n" + "=" * 70)
    print("Data acquisition complete!")
    print(f"Files saved to: {RAW_DATA_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
