"""
Synthetic Control Visualization

This script creates visualizations comparing actual outcomes to synthetic
counterfactuals for the Synthetic Control Method analysis.

Visualizations:
1. Actual vs. synthetic time series
2. Treatment effect gaps over time
3. Pre-treatment fit quality
4. Donor weights contribution
5. Placebo tests
6. Leave-one-out sensitivity
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import json
import warnings
warnings.filterwarnings('ignore')


class SyntheticControlVisualizer:
    """
    Visualize synthetic control results.

    Attributes:
        output_dir: Directory for saving plots
        results: Dictionary of synthetic control results
    """

    def __init__(self, output_dir: str = '../viz/output'):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}

        # Set style
        sns.set_style('whitegrid')
        plt.rcParams['figure.dpi'] = 100

    def load_results(self, results_dir: str, product: str):
        """
        Load synthetic control results for a product.

        Args:
            results_dir: Directory with saved results
            product: Product identifier
        """
        print(f"Loading results for {product}...")

        results_path = Path(results_dir) / product

        # Load time series
        ts_file = results_path / f'{product}_synthetic_timeseries.csv'
        if ts_file.exists():
            self.results['timeseries'] = pd.read_csv(ts_file, parse_dates=['date'])
        else:
            print(f"Warning: {ts_file} not found")

        # Load weights
        weights_file = results_path / f'{product}_weights.json'
        if weights_file.exists():
            with open(weights_file, 'r') as f:
                self.results['weights'] = json.load(f)
        else:
            print(f"Warning: {weights_file} not found")

        # Load gap statistics
        gap_file = results_path / f'{product}_gap_stats.json'
        if gap_file.exists():
            with open(gap_file, 'r') as f:
                self.results['gap_stats'] = json.load(f)
        else:
            print(f"Warning: {gap_file} not found")

        # Load LOO sensitivity
        loo_file = results_path / f'{product}_loo_sensitivity.csv'
        if loo_file.exists():
            self.results['loo_sensitivity'] = pd.read_csv(loo_file)
        else:
            print(f"Note: LOO sensitivity analysis not available")

        print(f"✓ Loaded results for {product}")

    def plot_synth_vs_actual(self,
                            treatment_date: str = '2018-03-01',
                            product_name: str = "Steel",
                            save: bool = True) -> plt.Figure:
        """
        Plot actual vs. synthetic time series with gap.

        Args:
            treatment_date: Date of treatment
            product_name: Product name for title
            save: Whether to save figure

        Returns:
            Matplotlib figure
        """
        print("\nPlotting actual vs. synthetic...")

        if 'timeseries' not in self.results:
            raise ValueError("Must load results first")

        df = self.results['timeseries']
        treatment = pd.to_datetime(treatment_date)

        # Create figure with 3 panels
        fig = plt.figure(figsize=(14, 12))
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.3)

        # Panel 1: Actual vs. Synthetic
        ax1 = fig.add_subplot(gs[0])

        ax1.plot(df['date'], df['actual'], 'o-', label='Actual',
                linewidth=2.5, markersize=4, color='navy')
        ax1.plot(df['date'], df['synthetic'], 's--', label='Synthetic',
                linewidth=2.5, markersize=4, alpha=0.7, color='darkred')
        ax1.axvline(treatment, color='red', linestyle='--',
                   linewidth=2, alpha=0.6, label='Tariff')

        # Shade pre and post periods
        pre_dates = df[df['date'] < treatment]['date']
        post_dates = df[df['date'] >= treatment]['date']

        if len(pre_dates) > 0:
            ax1.axvspan(pre_dates.min(), pre_dates.max(),
                       alpha=0.1, color='blue', label='Pre-treatment')
        if len(post_dates) > 0:
            ax1.axvspan(post_dates.min(), post_dates.max(),
                       alpha=0.1, color='orange', label='Post-treatment')

        ax1.set_ylabel('Import Value', fontsize=12)
        ax1.set_title(f'Synthetic Control: {product_name} Imports',
                     fontsize=14, fontweight='bold')
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Panel 2: Gap (Treatment Effect)
        ax2 = fig.add_subplot(gs[1])

        ax2.plot(df['date'], df['gap'], 'o-', color='darkgreen',
                linewidth=2.5, markersize=4)
        ax2.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax2.axvline(treatment, color='red', linestyle='--',
                   linewidth=2, alpha=0.6)
        ax2.fill_between(df['date'], 0, df['gap'], alpha=0.3, color='darkgreen')

        ax2.set_ylabel('Gap (Actual - Synthetic)', fontsize=12)
        ax2.set_title('Treatment Effect Over Time', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Panel 3: Gap as percentage
        ax3 = fig.add_subplot(gs[2])

        ax3.plot(df['date'], df['gap_pct'], 'o-', color='purple',
                linewidth=2.5, markersize=4)
        ax3.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax3.axvline(treatment, color='red', linestyle='--',
                   linewidth=2, alpha=0.6)
        ax3.fill_between(df['date'], 0, df['gap_pct'], alpha=0.3, color='purple')

        ax3.set_xlabel('Date', fontsize=12)
        ax3.set_ylabel('Gap (%)', fontsize=12)
        ax3.set_title('Treatment Effect (% of Synthetic)', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            save_path = self.output_dir / f'{product_name}_synth_comparison.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        return fig

    def plot_pre_treatment_fit(self,
                               treatment_date: str = '2018-03-01',
                               save: bool = True) -> plt.Figure:
        """
        Assess quality of pre-treatment fit.

        Args:
            treatment_date: Date of treatment
            save: Whether to save figure

        Returns:
            Matplotlib figure
        """
        print("\nPlotting pre-treatment fit quality...")

        if 'timeseries' not in self.results:
            raise ValueError("Must load results first")

        df = self.results['timeseries']
        treatment = pd.to_datetime(treatment_date)

        # Filter to pre-treatment
        pre_df = df[df['date'] < treatment].copy()

        # Calculate metrics
        rmse = np.sqrt(np.mean(pre_df['gap'] ** 2))
        mae = np.mean(np.abs(pre_df['gap']))
        mape = np.mean(np.abs(pre_df['gap_pct']))

        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Panel A: Actual vs. Synthetic (pre-period only)
        axes[0, 0].plot(pre_df['date'], pre_df['actual'], 'o-',
                       label='Actual', linewidth=2, markersize=4)
        axes[0, 0].plot(pre_df['date'], pre_df['synthetic'], 's--',
                       label='Synthetic', linewidth=2, markersize=4, alpha=0.7)
        axes[0, 0].set_ylabel('Import Value', fontsize=11)
        axes[0, 0].set_title('Pre-Treatment Fit', fontsize=12, fontweight='bold')
        axes[0, 0].legend(loc='best')
        axes[0, 0].grid(True, alpha=0.3)

        # Panel B: Residuals over time
        axes[0, 1].plot(pre_df['date'], pre_df['gap'], 'o-',
                       color='darkred', linewidth=2, markersize=4)
        axes[0, 1].axhline(0, color='black', linestyle='--', linewidth=1.5)
        axes[0, 1].set_ylabel('Gap (Actual - Synthetic)', fontsize=11)
        axes[0, 1].set_title('Pre-Treatment Residuals', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)

        # Panel C: Scatter plot
        axes[1, 0].scatter(pre_df['synthetic'], pre_df['actual'],
                          alpha=0.6, s=50, edgecolors='black', linewidth=0.5)

        # Add 45-degree line
        min_val = min(pre_df['synthetic'].min(), pre_df['actual'].min())
        max_val = max(pre_df['synthetic'].max(), pre_df['actual'].max())
        axes[1, 0].plot([min_val, max_val], [min_val, max_val],
                       'r--', linewidth=2, alpha=0.7, label='Perfect fit')

        axes[1, 0].set_xlabel('Synthetic', fontsize=11)
        axes[1, 0].set_ylabel('Actual', fontsize=11)
        axes[1, 0].set_title('Actual vs. Synthetic (Scatter)', fontsize=12, fontweight='bold')
        axes[1, 0].legend(loc='best')
        axes[1, 0].grid(True, alpha=0.3)

        # Panel D: Distribution of gaps
        axes[1, 1].hist(pre_df['gap'], bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        axes[1, 1].axvline(0, color='red', linestyle='--', linewidth=2)
        axes[1, 1].set_xlabel('Gap (Actual - Synthetic)', fontsize=11)
        axes[1, 1].set_ylabel('Frequency', fontsize=11)
        axes[1, 1].set_title('Distribution of Pre-Treatment Gaps', fontsize=12, fontweight='bold')

        # Add text with fit statistics
        textstr = f'RMSE: {rmse:.2f}\\nMAE: {mae:.2f}\\nMAPE: {mape:.2f}%'
        axes[1, 1].text(0.65, 0.95, textstr, transform=axes[1, 1].transAxes,
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.suptitle('Pre-Treatment Fit Quality Assessment',
                    fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()

        if save:
            save_path = self.output_dir / 'pre_treatment_fit.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        return fig

    def plot_donor_weights(self,
                          top_n: int = 15,
                          save: bool = True) -> plt.Figure:
        """
        Plot donor country weight contributions.

        Args:
            top_n: Number of top donors to display
            save: Whether to save figure

        Returns:
            Matplotlib figure
        """
        print("\nPlotting donor weights...")

        if 'weights' not in self.results:
            raise ValueError("Must load results with weights")

        weights_dict = self.results['weights']['weights']

        # Filter to non-zero and sort
        nonzero_weights = {k: v for k, v in weights_dict.items() if v > 0.001}
        sorted_weights = dict(sorted(nonzero_weights.items(), key=lambda x: -x[1]))

        # Take top N
        plot_weights = dict(list(sorted_weights.items())[:top_n])

        # Create figure
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Panel A: Horizontal bar chart
        countries = list(plot_weights.keys())
        weights = list(plot_weights.values())

        bars = axes[0].barh(countries, weights, color='steelblue', alpha=0.7, edgecolor='black')

        # Color top 3 differently
        for i in range(min(3, len(bars))):
            bars[i].set_color('darkred')
            bars[i].set_alpha(0.8)

        # Add value labels
        for i, (country, weight) in enumerate(plot_weights.items()):
            axes[0].text(weight + 0.01, i, f'{weight:.3f}',
                        va='center', fontsize=9)

        axes[0].set_xlabel('Weight', fontsize=12)
        axes[0].set_title(f'Donor Country Contributions (Top {len(plot_weights)})',
                         fontsize=13, fontweight='bold')
        axes[0].set_xlim(0, max(weights) * 1.15)
        axes[0].grid(True, alpha=0.3, axis='x')

        # Panel B: Pie chart for top donors
        top_5 = dict(list(sorted_weights.items())[:5])
        other_weight = sum(sorted_weights.values()) - sum(top_5.values())

        if other_weight > 0.001:
            pie_data = list(top_5.values()) + [other_weight]
            pie_labels = list(top_5.keys()) + ['Other']
        else:
            pie_data = list(top_5.values())
            pie_labels = list(top_5.keys())

        axes[1].pie(pie_data, labels=pie_labels, autopct='%1.1f%%',
                   startangle=90, textprops={'fontsize': 10})
        axes[1].set_title('Weight Distribution (Top 5 + Other)',
                         fontsize=13, fontweight='bold')

        plt.tight_layout()

        if save:
            save_path = self.output_dir / 'donor_weights.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        return fig

    def plot_loo_sensitivity(self, save: bool = True) -> plt.Figure:
        """
        Plot leave-one-out sensitivity analysis results.

        Args:
            save: Whether to save figure

        Returns:
            Matplotlib figure
        """
        print("\nPlotting LOO sensitivity...")

        if 'loo_sensitivity' not in self.results:
            print("LOO sensitivity analysis not available")
            return None

        loo_df = self.results['loo_sensitivity']

        # Create figure
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))

        # Panel A: Effect of excluding each donor
        x = np.arange(len(loo_df))
        axes[0].scatter(x, loo_df['mean_gap'], s=100 * loo_df['original_weight'],
                       alpha=0.6, c=loo_df['original_weight'],
                       cmap='viridis', edgecolors='black', linewidth=0.5)

        axes[0].set_xticks(x)
        axes[0].set_xticklabels(loo_df['excluded_country'], rotation=45, ha='right')
        axes[0].set_ylabel('Mean Gap (with country excluded)', fontsize=11)
        axes[0].set_title('Leave-One-Out Sensitivity: Mean Treatment Effect',
                         fontsize=13, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')

        # Add colorbar
        cbar = plt.colorbar(axes[0].collections[0], ax=axes[0])
        cbar.set_label('Original Weight', fontsize=10)

        # Panel B: Pre-treatment RMSE
        axes[1].bar(x, loo_df['rmse_pre'], alpha=0.7, color='coral', edgecolor='black')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(loo_df['excluded_country'], rotation=45, ha='right')
        axes[1].set_ylabel('Pre-treatment RMSE', fontsize=11)
        axes[1].set_title('Leave-One-Out: Pre-Treatment Fit Quality',
                         fontsize=13, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save:
            save_path = self.output_dir / 'loo_sensitivity.png'
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        return fig

    def create_summary_report(self,
                             treatment_date: str = '2018-03-01',
                             product_name: str = "Steel",
                             save: bool = True):
        """
        Create comprehensive summary visualization report.

        Args:
            treatment_date: Treatment date
            product_name: Product name
            save: Whether to save figures
        """
        print(f"\nCreating summary report for {product_name}...")

        self.plot_synth_vs_actual(treatment_date, product_name, save)
        self.plot_pre_treatment_fit(treatment_date, save)
        self.plot_donor_weights(save=save)

        if 'loo_sensitivity' in self.results:
            self.plot_loo_sensitivity(save)

        # Print summary statistics
        if 'gap_stats' in self.results:
            print("\n" + "="*60)
            print("SUMMARY STATISTICS")
            print("="*60)
            stats = self.results['gap_stats']
            print(f"Mean post-treatment gap:     {stats['mean_gap']:,.2f}")
            print(f"Mean gap (%):                {stats['mean_gap_pct']:.2f}%")
            print(f"Cumulative gap:              {stats['cumulative_gap']:,.2f}")
            print(f"Pre-treatment RMSE:          {stats['rmse_pre']:.2f}")
            print(f"Post-treatment RMSE:         {stats['rmse_post']:.2f}")
            print("="*60)

        print(f"\n✓ Summary report complete for {product_name}")


def compare_products(results_dir: str,
                    products: List[str],
                    treatment_date: str = '2018-03-01',
                    output_dir: str = '../viz/output'):
    """
    Compare synthetic control results across multiple products.

    Args:
        results_dir: Directory with saved results
        products: List of product names
        treatment_date: Treatment date
        output_dir: Output directory
    """
    print(f"\nComparing {len(products)} products...")

    treatment = pd.to_datetime(treatment_date)
    fig, axes = plt.subplots(len(products), 2, figsize=(16, 5*len(products)))

    if len(products) == 1:
        axes = axes.reshape(1, -1)

    for i, product in enumerate(products):
        # Load results
        ts_file = Path(results_dir) / product / f'{product}_synthetic_timeseries.csv'
        if not ts_file.exists():
            print(f"Warning: {ts_file} not found")
            continue

        df = pd.read_csv(ts_file, parse_dates=['date'])

        # Plot actual vs. synthetic
        axes[i, 0].plot(df['date'], df['actual'], 'o-', label='Actual', linewidth=2)
        axes[i, 0].plot(df['date'], df['synthetic'], 's--', label='Synthetic',
                       linewidth=2, alpha=0.7)
        axes[i, 0].axvline(treatment, color='red', linestyle='--', linewidth=2, alpha=0.6)
        axes[i, 0].set_ylabel('Import Value', fontsize=11)
        axes[i, 0].set_title(f'{product}: Actual vs. Synthetic', fontsize=12, fontweight='bold')
        axes[i, 0].legend(loc='best')
        axes[i, 0].grid(True, alpha=0.3)

        # Plot gap
        axes[i, 1].plot(df['date'], df['gap'], 'o-', color='darkgreen', linewidth=2)
        axes[i, 1].axhline(0, color='black', linestyle='-', linewidth=1)
        axes[i, 1].axvline(treatment, color='red', linestyle='--', linewidth=2, alpha=0.6)
        axes[i, 1].fill_between(df['date'], 0, df['gap'], alpha=0.3, color='darkgreen')
        axes[i, 1].set_ylabel('Gap', fontsize=11)
        axes[i, 1].set_title(f'{product}: Treatment Effect', fontsize=12, fontweight='bold')
        axes[i, 1].grid(True, alpha=0.3)

    plt.tight_layout()

    save_path = Path(output_dir) / 'product_comparison.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved comparison to {save_path}")

    return fig


def main():
    """
    Example usage of SyntheticControlVisualizer.
    """
    # Initialize visualizer
    viz = SyntheticControlVisualizer(output_dir='../viz/output')

    # Load results for a product
    # viz.load_results('../models/artifacts/synthetic_control', 'HRC')

    # Create summary report
    # viz.create_summary_report(treatment_date='2018-03-01', product_name='HRC', save=True)

    # Compare multiple products
    # compare_products(
    #     results_dir='../models/artifacts/synthetic_control',
    #     products=['HRC', 'CRC', 'plate'],
    #     treatment_date='2018-03-01'
    # )

    print("\nSynthetic control visualization script ready!")
    print("Uncomment the lines above and provide results path to generate visualizations.")


if __name__ == "__main__":
    main()
