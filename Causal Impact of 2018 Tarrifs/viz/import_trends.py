"""
Import Trends Visualization

This script creates comprehensive visualizations of steel import trends
before and after Section 232 tariff implementation.

Visualizations:
1. Overall import value/quantity trends by treatment group
2. Country-level import trajectories
3. Product-level decomposition
4. Price vs. volume effects
5. Market share shifts
6. Geographic heatmaps
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Dict
import warnings
warnings.filterwarnings('ignore')


class ImportTrendsVisualizer:
    """
    Create visualizations of steel import trends.

    Attributes:
        data: Panel data
        treatment_date: Date of tariff implementation
        output_dir: Directory for saving plots
    """

    def __init__(self, treatment_date: str = '2018-03-23', output_dir: str = '../viz/output'):
        """
        Initialize visualizer.

        Args:
            treatment_date: Date of tariff implementation
            output_dir: Directory to save plots
        """
        self.treatment_date = pd.to_datetime(treatment_date)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data = None

        # Set style
        sns.set_style('whitegrid')
        sns.set_palette('colorblind')

    def load_data(self, data_path: str) -> pd.DataFrame:
        """
        Load panel data.

        Args:
            data_path: Path to data file

        Returns:
            Loaded DataFrame
        """
        print(f"Loading data from {data_path}...")

        if data_path.endswith('.parquet'):
            self.data = pd.read_parquet(data_path)
        else:
            self.data = pd.read_csv(data_path, parse_dates=['date'])

        print(f"Loaded {len(self.data):,} observations")
        return self.data

    def plot_aggregate_trends(self,
                             treated_countries: Optional[List[str]] = None,
                             save: bool = True) -> plt.Figure:
        """
        Plot aggregate import trends for treated vs. control groups.

        Args:
            treated_countries: List of treated countries
            save: Whether to save figure

        Returns:
            Matplotlib figure
        """
        print("\nPlotting aggregate trends...")

        # Create treatment indicator
        if treated_countries is None:
            exempt = ['Canada', 'Mexico']
            treated_countries = [c for c in self.data['country'].unique() if c not in exempt]

        self.data['treated'] = self.data['country'].isin(treated_countries).astype(int)

        # Aggregate by month and treatment status
        agg = self.data.groupby(['date', 'treated']).agg({
            'import_value': 'sum',
            'import_quantity': 'sum'
        }).reset_index()

        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))

        # Panel A: Import Value (levels)
        for treat in [0, 1]:
            subset = agg[agg['treated'] == treat]
            label = 'Treated' if treat == 1 else 'Control'
            axes[0, 0].plot(subset['date'], subset['import_value'] / 1e6,
                          'o-', label=label, linewidth=2, markersize=3, alpha=0.7)

        axes[0, 0].axvline(self.treatment_date, color='red', linestyle='--',
                          linewidth=2, alpha=0.6, label='Tariff')
        axes[0, 0].set_ylabel('Import Value ($ Millions)', fontsize=11)
        axes[0, 0].set_title('Import Value Over Time', fontsize=12, fontweight='bold')
        axes[0, 0].legend(loc='best')
        axes[0, 0].grid(True, alpha=0.3)

        # Panel B: Import Value (log)
        agg['log_value'] = np.log(agg['import_value'] + 1)
        for treat in [0, 1]:
            subset = agg[agg['treated'] == treat]
            label = 'Treated' if treat == 1 else 'Control'
            axes[0, 1].plot(subset['date'], subset['log_value'],
                          'o-', label=label, linewidth=2, markersize=3, alpha=0.7)

        axes[0, 1].axvline(self.treatment_date, color='red', linestyle='--',
                          linewidth=2, alpha=0.6, label='Tariff')
        axes[0, 1].set_ylabel('Log Import Value', fontsize=11)
        axes[0, 1].set_title('Log Import Value Over Time', fontsize=12, fontweight='bold')
        axes[0, 1].legend(loc='best')
        axes[0, 1].grid(True, alpha=0.3)

        # Panel C: Import Quantity
        for treat in [0, 1]:
            subset = agg[agg['treated'] == treat]
            label = 'Treated' if treat == 1 else 'Control'
            axes[1, 0].plot(subset['date'], subset['import_quantity'] / 1e3,
                          'o-', label=label, linewidth=2, markersize=3, alpha=0.7)

        axes[1, 0].axvline(self.treatment_date, color='red', linestyle='--',
                          linewidth=2, alpha=0.6, label='Tariff')
        axes[1, 0].set_xlabel('Date', fontsize=11)
        axes[1, 0].set_ylabel('Import Quantity (000s tons)', fontsize=11)
        axes[1, 0].set_title('Import Quantity Over Time', fontsize=12, fontweight='bold')
        axes[1, 0].legend(loc='best')
        axes[1, 0].grid(True, alpha=0.3)

        # Panel D: Implied Unit Price
        agg['unit_price'] = agg['import_value'] / (agg['import_quantity'] + 1)
        for treat in [0, 1]:
            subset = agg[agg['treated'] == treat]
            label = 'Treated' if treat == 1 else 'Control'
            axes[1, 1].plot(subset['date'], subset['unit_price'],
                          'o-', label=label, linewidth=2, markersize=3, alpha=0.7)

        axes[1, 1].axvline(self.treatment_date, color='red', linestyle='--',
                          linewidth=2, alpha=0.6, label='Tariff')
        axes[1, 1].set_xlabel('Date', fontsize=11)
        axes[1, 1].set_ylabel('Unit Price ($/ton)', fontsize=11)
        axes[1, 1].set_title('Implied Unit Price Over Time', fontsize=12, fontweight='bold')
        axes[1, 1].legend(loc='best')
        axes[1, 1].grid(True, alpha=0.3)

        plt.suptitle('Steel Import Trends: Treated vs. Control Countries',
                    fontsize=15, fontweight='bold', y=1.00)
        plt.tight_layout()

        if save:
            save_path = self.output_dir / 'aggregate_trends.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        return fig

    def plot_country_trajectories(self,
                                 top_n: int = 10,
                                 save: bool = True) -> plt.Figure:
        """
        Plot individual country import trajectories.

        Args:
            top_n: Number of top countries to show
            save: Whether to save figure

        Returns:
            Matplotlib figure
        """
        print(f"\nPlotting top {top_n} country trajectories...")

        # Get top countries by total import value
        country_totals = self.data.groupby('country')['import_value'].sum().sort_values(ascending=False)
        top_countries = country_totals.head(top_n).index.tolist()

        # Filter data
        country_data = self.data[self.data['country'].isin(top_countries)]

        # Aggregate by country and date
        country_agg = country_data.groupby(['date', 'country'])['import_value'].sum().reset_index()

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot each country
        for country in top_countries:
            subset = country_agg[country_agg['country'] == country]
            ax.plot(subset['date'], subset['import_value'] / 1e6,
                   'o-', label=country, linewidth=1.5, markersize=3, alpha=0.7)

        ax.axvline(self.treatment_date, color='red', linestyle='--',
                  linewidth=2.5, alpha=0.6, label='Tariff', zorder=100)

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Import Value ($ Millions)', fontsize=12)
        ax.set_title(f'Import Trajectories: Top {top_n} Countries', fontsize=14, fontweight='bold')
        ax.legend(loc='best', ncol=2, fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            save_path = self.output_dir / 'country_trajectories.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        return fig

    def plot_product_decomposition(self, save: bool = True) -> plt.Figure:
        """
        Plot import trends decomposed by product type.

        Args:
            save: Whether to save figure

        Returns:
            Matplotlib figure
        """
        print("\nPlotting product decomposition...")

        # Aggregate by product and date
        product_agg = self.data.groupby(['date', 'product'])['import_value'].sum().reset_index()

        # Create figure
        fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        # Panel A: Stacked area chart
        pivot = product_agg.pivot(index='date', columns='product', values='import_value')
        pivot = pivot.fillna(0) / 1e6  # Convert to millions

        axes[0].stackplot(pivot.index, *[pivot[col] for col in pivot.columns],
                         labels=pivot.columns, alpha=0.7)
        axes[0].axvline(self.treatment_date, color='red', linestyle='--',
                       linewidth=2, alpha=0.6, label='Tariff')
        axes[0].set_ylabel('Import Value ($ Millions)', fontsize=12)
        axes[0].set_title('Import Value by Product (Stacked)', fontsize=14, fontweight='bold')
        axes[0].legend(loc='upper left', fontsize=9)
        axes[0].grid(True, alpha=0.3)

        # Panel B: Individual lines
        for product in pivot.columns:
            axes[1].plot(pivot.index, pivot[product],
                       'o-', label=product, linewidth=2, markersize=3, alpha=0.7)

        axes[1].axvline(self.treatment_date, color='red', linestyle='--',
                       linewidth=2, alpha=0.6, label='Tariff')
        axes[1].set_xlabel('Date', fontsize=12)
        axes[1].set_ylabel('Import Value ($ Millions)', fontsize=12)
        axes[1].set_title('Import Value by Product (Lines)', fontsize=14, fontweight='bold')
        axes[1].legend(loc='best', fontsize=9)
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            save_path = self.output_dir / 'product_decomposition.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        return fig

    def plot_market_share_shifts(self,
                                top_n: int = 8,
                                save: bool = True) -> plt.Figure:
        """
        Plot market share shifts before and after tariff.

        Args:
            top_n: Number of top countries to show
            save: Whether to save figure

        Returns:
            Matplotlib figure
        """
        print("\nPlotting market share shifts...")

        # Split pre and post periods
        pre_data = self.data[self.data['date'] < self.treatment_date]
        post_data = self.data[self.data['date'] >= self.treatment_date]

        # Calculate market shares
        pre_shares = pre_data.groupby('country')['import_value'].sum()
        post_shares = post_data.groupby('country')['import_value'].sum()

        pre_shares = pre_shares / pre_shares.sum() * 100
        post_shares = post_shares / post_shares.sum() * 100

        # Combine and get top countries
        shares_df = pd.DataFrame({
            'pre': pre_shares,
            'post': post_shares
        }).fillna(0)
        shares_df['change'] = shares_df['post'] - shares_df['pre']
        shares_df = shares_df.sort_values('pre', ascending=False).head(top_n)

        # Create figure
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Panel A: Pre vs. Post shares
        x = np.arange(len(shares_df))
        width = 0.35

        axes[0].bar(x - width/2, shares_df['pre'], width, label='Pre-Tariff', alpha=0.8)
        axes[0].bar(x + width/2, shares_df['post'], width, label='Post-Tariff', alpha=0.8)

        axes[0].set_xlabel('Country', fontsize=12)
        axes[0].set_ylabel('Market Share (%)', fontsize=12)
        axes[0].set_title('Market Share: Pre vs. Post Tariff', fontsize=14, fontweight='bold')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(shares_df.index, rotation=45, ha='right')
        axes[0].legend(loc='best')
        axes[0].grid(True, alpha=0.3, axis='y')

        # Panel B: Change in market share
        colors = ['green' if x > 0 else 'red' for x in shares_df['change']]
        axes[1].barh(shares_df.index, shares_df['change'], color=colors, alpha=0.7)
        axes[1].axvline(0, color='black', linestyle='-', linewidth=1)

        axes[1].set_xlabel('Change in Market Share (ppt)', fontsize=12)
        axes[1].set_title('Market Share Change (Post - Pre)', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if save:
            save_path = self.output_dir / 'market_share_shifts.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        return fig

    def create_summary_dashboard(self, save: bool = True):
        """
        Create comprehensive summary dashboard.

        Args:
            save: Whether to save figure
        """
        print("\nCreating summary dashboard...")

        self.plot_aggregate_trends(save=save)
        self.plot_country_trajectories(save=save)
        self.plot_product_decomposition(save=save)
        self.plot_market_share_shifts(save=save)

        print("\n✓ Dashboard creation complete")


def main():
    """
    Example usage of ImportTrendsVisualizer.
    """
    # Initialize visualizer
    viz = ImportTrendsVisualizer(
        treatment_date='2018-03-23',
        output_dir='../viz/output'
    )

    # Load data
    # viz.load_data('../data/clean/steel_panel.parquet')

    # Create all visualizations
    # viz.create_summary_dashboard(save=True)

    print("\nImport trends visualization script ready!")
    print("Uncomment the lines above and provide data path to generate plots.")


if __name__ == "__main__":
    main()
