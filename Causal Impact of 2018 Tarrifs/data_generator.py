"""
Data Generator for Tariff Causal Analysis
Generates realistic synthetic data for Section 232 tariff analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class TariffDataGenerator:
    """Generate synthetic trade data for tariff impact analysis"""

    def __init__(self, seed=42):
        np.random.seed(seed)

        # Define countries and their characteristics
        self.countries = {
            'China': {'treated': True, 'treatment_date': '2018-03-23', 'base_volume': 1000, 'tariff_rate': 0.25},
            'South Korea': {'treated': True, 'treatment_date': '2018-03-23', 'base_volume': 600, 'tariff_rate': 0.25},
            'Brazil': {'treated': True, 'treatment_date': '2018-03-23', 'base_volume': 500, 'tariff_rate': 0.25},
            'Canada': {'treated': False, 'treatment_date': None, 'base_volume': 800, 'tariff_rate': 0.0},
            'Mexico': {'treated': False, 'treatment_date': None, 'base_volume': 700, 'tariff_rate': 0.0},
            'Germany': {'treated': True, 'treatment_date': '2018-06-01', 'base_volume': 400, 'tariff_rate': 0.25},
        }

        # Define products
        self.products = {
            'Steel-HotRolled': {'hs_code': '7208', 'treated': True, 'base_price': 600},
            'Steel-ColdRolled': {'hs_code': '7209', 'treated': True, 'base_price': 700},
            'Steel-Plate': {'hs_code': '7208.51', 'treated': True, 'base_price': 650},
            'Aluminum': {'hs_code': '7601', 'treated': True, 'base_price': 2200},
        }

    def generate_trade_data(self, start_date='2016-01-01', end_date='2020-12-31'):
        """Generate monthly trade data (import volumes and prices)"""

        # Create date range
        dates = pd.date_range(start=start_date, end=end_date, freq='MS')

        data = []

        for country, country_info in self.countries.items():
            for product, product_info in self.products.items():
                base_volume = country_info['base_volume']
                base_price = product_info['base_price']

                for date in dates:
                    # Determine if post-treatment
                    if country_info['treated'] and country_info['treatment_date']:
                        treatment_date = pd.to_datetime(country_info['treatment_date'])
                        post_treatment = date >= treatment_date
                    else:
                        post_treatment = False

                    # Generate volume with trend and seasonality
                    months_since_start = (date.year - 2016) * 12 + date.month
                    trend = 1 + 0.01 * months_since_start  # 1% monthly growth
                    seasonality = 1 + 0.1 * np.sin(2 * np.pi * date.month / 12)

                    # Treatment effect on volume (reduction)
                    if post_treatment:
                        treatment_effect_volume = -0.35  # 35% reduction
                    else:
                        treatment_effect_volume = 0

                    # Calculate volume
                    volume = base_volume * trend * seasonality * (1 + treatment_effect_volume)
                    volume += np.random.normal(0, base_volume * 0.15)  # Add noise
                    volume = max(0, volume)  # No negative volumes

                    # Generate price with treatment effect
                    if post_treatment:
                        treatment_effect_price = 0.20  # 20% price increase
                    else:
                        treatment_effect_price = 0

                    price = base_price * (1 + 0.005 * months_since_start)  # Slight trend
                    price *= (1 + treatment_effect_price)
                    price += np.random.normal(0, base_price * 0.08)  # Add noise

                    data.append({
                        'date': date,
                        'country': country,
                        'product': product,
                        'hs_code': product_info['hs_code'],
                        'import_volume_tons': volume,
                        'import_price_per_ton': price,
                        'treated': country_info['treated'],
                        'post_treatment': post_treatment,
                        'tariff_rate': country_info['tariff_rate'] if post_treatment else 0
                    })

        df = pd.DataFrame(data)
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['year_month'] = df['date'].dt.to_period('M')

        return df

    def generate_domestic_data(self, start_date='2016-01-01', end_date='2020-12-31'):
        """Generate domestic production and price data"""

        dates = pd.date_range(start=start_date, end=end_date, freq='MS')

        data = []

        for product, product_info in self.products.items():
            if 'Steel' in product:  # Only for steel products
                base_production = 5000  # thousand tons
                base_price = product_info['base_price'] * 1.1  # Domestic slightly higher

                for date in dates:
                    treatment_date = pd.to_datetime('2018-03-23')
                    post_treatment = date >= treatment_date

                    months_since_start = (date.year - 2016) * 12 + date.month
                    trend = 1 + 0.005 * months_since_start

                    # Treatment effect: increased domestic production
                    if post_treatment:
                        treatment_effect_production = 0.15  # 15% increase
                        treatment_effect_price = 0.12  # 12% price increase
                    else:
                        treatment_effect_production = 0
                        treatment_effect_price = 0

                    production = base_production * trend * (1 + treatment_effect_production)
                    production += np.random.normal(0, base_production * 0.10)

                    price = base_price * (1 + 0.003 * months_since_start)
                    price *= (1 + treatment_effect_price)
                    price += np.random.normal(0, base_price * 0.06)

                    data.append({
                        'date': date,
                        'product': product,
                        'domestic_production_tons': max(0, production),
                        'domestic_price_per_ton': price,
                        'post_treatment': post_treatment
                    })

        return pd.DataFrame(data)

    def save_data(self, output_dir='data'):
        """Generate and save all datasets"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Generate trade data
        trade_df = self.generate_trade_data()
        trade_df.to_csv(f'{output_dir}/trade_data.csv', index=False)
        print(f"Generated trade data: {len(trade_df)} rows")

        # Generate domestic data
        domestic_df = self.generate_domestic_data()
        domestic_df.to_csv(f'{output_dir}/domestic_data.csv', index=False)
        print(f"Generated domestic data: {len(domestic_df)} rows")

        return trade_df, domestic_df


if __name__ == '__main__':
    generator = TariffDataGenerator(seed=42)
    trade_df, domestic_df = generator.save_data()

    print("\nTrade Data Summary:")
    print(trade_df.groupby(['country', 'post_treatment'])['import_volume_tons'].mean())

    print("\nDomestic Data Summary:")
    print(domestic_df.groupby('post_treatment')['domestic_production_tons'].mean())
