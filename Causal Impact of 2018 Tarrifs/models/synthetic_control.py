"""
Synthetic Control Method for Section 232 Tariff Analysis

This module implements the Synthetic Control Method (SCM) for analyzing the causal
impact of 2018 Section 232 tariffs on steel imports by product.

Pipeline Steps (per target product):
1. Define pre-treatment period (2010-2017)
2. Fit weights from donor pool
3. Generate synthetic counterfactual
4. Plot actual vs. synthetic
5. Compute post-treatment gaps
6. Run leave-one-out sensitivity analysis

References:
    - Abadie et al. (2010): "Synthetic Control Methods for Comparative Case Studies"
    - Abadie (2021): "Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects"
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings


@dataclass
class SyntheticControlConfig:
    """Configuration for Synthetic Control estimation."""
    pre_period_start: str = '2010-01-01'
    pre_period_end: str = '2017-12-31'
    post_period_start: str = '2018-03-01'
    post_period_end: str = '2020-12-31'
    target_country: str = 'USA'
    optimization_method: str = 'SLSQP'
    max_iterations: int = 1000


class SyntheticControl:
    """
    Synthetic Control estimator for tariff impact analysis.

    The synthetic control method creates a weighted combination of control units
    (donor countries) that best approximates the treated unit's pre-treatment
    characteristics. Post-treatment gaps between actual and synthetic represent
    the causal effect.

    Attributes:
        config: Configuration object
        data: Panel data
        weights: Optimal donor weights
        synthetic: Synthetic control time series
        results: Dictionary of estimation results
    """

    def __init__(self, config: Optional[SyntheticControlConfig] = None):
        """
        Initialize Synthetic Control model.

        Args:
            config: Configuration object (uses defaults if None)
        """
        self.config = config or SyntheticControlConfig()
        self.data = None
        self.weights = {}
        self.synthetic = {}
        self.results = {}

    def load_data(self, data_path: str, product: str) -> pd.DataFrame:
        """
        Load and prepare data for specific product.

        Args:
            data_path: Path to panel data
            product: Product code (e.g., 'HRC', 'CRC', 'plate')

        Returns:
            Filtered and prepared DataFrame
        """
        print(f"\nLoading data for product: {product}")

        if data_path.endswith('.parquet'):
            data = pd.read_parquet(data_path)
        else:
            data = pd.read_csv(data_path, parse_dates=['date'])

        # Filter to specific product
        self.data = data[data['product'] == product].copy()

        # Sort by country and date
        self.data = self.data.sort_values(['country', 'date'])

        print(f"Loaded {len(self.data):,} observations")
        print(f"Countries: {self.data['country'].nunique()}")
        print(f"Date range: {self.data['date'].min()} to {self.data['date'].max()}")

        return self.data

    def prepare_matrices(self,
                        outcome_var: str = 'import_value',
                        donor_countries: Optional[List[str]] = None,
                        predictors: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare outcome and predictor matrices for optimization.

        Args:
            outcome_var: Variable to match (e.g., 'import_value', 'import_quantity')
            donor_countries: List of donor pool countries
            predictors: Additional predictor variables for matching

        Returns:
            Tuple of (X1, X0) where:
                - X1: Treated unit pre-treatment characteristics
                - X0: Donor pool pre-treatment characteristics
        """
        print("\nPreparing matrices for optimization...")

        # Define time periods
        pre_start = pd.to_datetime(self.config.pre_period_start)
        pre_end = pd.to_datetime(self.config.pre_period_end)

        # Filter to pre-treatment period
        pre_data = self.data[
            (self.data['date'] >= pre_start) &
            (self.data['date'] <= pre_end)
        ].copy()

        # Get treated unit (e.g., USA)
        treated_data = pre_data[pre_data['country'] == self.config.target_country]

        # Get donor pool
        if donor_countries is None:
            # Exclude treated country
            donor_countries = [c for c in pre_data['country'].unique()
                             if c != self.config.target_country]

        donor_data = pre_data[pre_data['country'].isin(donor_countries)]

        # Build outcome matrix (time × countries)
        Y_treated = treated_data.pivot_table(
            values=outcome_var,
            index='date',
            aggfunc='sum'
        ).values.flatten()

        Y_donors = donor_data.pivot_table(
            values=outcome_var,
            index='date',
            columns='country',
            aggfunc='sum'
        )

        # Store for later use
        self.Y_treated = Y_treated
        self.Y_donors = Y_donors
        self.donor_countries = donor_countries
        self.outcome_var = outcome_var

        print(f"Treated unit: {self.config.target_country}")
        print(f"Donor pool: {len(donor_countries)} countries")
        print(f"Pre-treatment periods: {len(Y_treated)}")

        # Build predictor matrices
        if predictors is None:
            # Use lagged outcomes as predictors
            X1 = Y_treated.reshape(-1, 1)
            X0 = Y_donors.values
        else:
            # Build from additional predictors
            X1_list = [treated_data.groupby('date')[p].mean().values for p in predictors]
            X1 = np.column_stack(X1_list)

            X0_list = []
            for country in donor_countries:
                country_data = donor_data[donor_data['country'] == country]
                country_predictors = [country_data.groupby('date')[p].mean().values
                                     for p in predictors]
                X0_list.append(np.column_stack(country_predictors))
            X0 = np.stack(X0_list, axis=1)

        return X1, X0

    def fit_weights(self,
                   outcome_var: str = 'import_value',
                   donor_countries: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Fit optimal donor weights using constrained optimization.

        Solves:
            min ||X1 - X0·W||²
            s.t. W ≥ 0, Σw_i = 1

        Where:
            - X1: Treated unit pre-treatment outcomes
            - X0: Donor pool pre-treatment outcomes
            - W: Weight vector

        Args:
            outcome_var: Outcome variable to match
            donor_countries: Donor pool countries

        Returns:
            Dictionary mapping country -> weight
        """
        print(f"\nFitting synthetic control weights...")

        # Prepare data
        X1, X0 = self.prepare_matrices(outcome_var, donor_countries)

        # Objective: minimize RMSE
        def objective(W):
            """Compute RMSE between treated and synthetic."""
            synthetic = self.Y_donors.values @ W
            return np.sqrt(np.mean((self.Y_treated - synthetic) ** 2))

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda W: np.sum(W) - 1}  # Weights sum to 1
        ]

        # Bounds: each weight in [0, 1]
        bounds = [(0, 1) for _ in range(len(self.donor_countries))]

        # Initial guess: equal weights
        W0 = np.ones(len(self.donor_countries)) / len(self.donor_countries)

        # Optimize
        print("Running optimization...")
        result = minimize(
            objective,
            W0,
            method=self.config.optimization_method,
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': self.config.max_iterations}
        )

        if not result.success:
            warnings.warn(f"Optimization did not converge: {result.message}")

        # Extract weights
        optimal_weights = result.x
        self.weights = dict(zip(self.donor_countries, optimal_weights))

        # Filter to non-zero weights for display
        nonzero_weights = {k: v for k, v in self.weights.items() if v > 0.01}

        print(f"\nOptimization converged: {result.success}")
        print(f"Final RMSE: {result.fun:.2f}")
        print(f"\nNon-zero weights ({len(nonzero_weights)}):")
        for country, weight in sorted(nonzero_weights.items(), key=lambda x: -x[1])[:10]:
            print(f"  {country}: {weight:.4f}")

        self.results['weights'] = self.weights
        self.results['pre_rmse'] = result.fun

        return self.weights

    def generate_synthetic(self) -> pd.DataFrame:
        """
        Generate synthetic control time series using fitted weights.

        Returns:
            DataFrame with actual and synthetic values over full time period
        """
        print("\nGenerating synthetic control...")

        if not self.weights:
            raise ValueError("Must fit weights first using fit_weights()")

        # Create weight array
        weight_array = np.array([self.weights[c] for c in self.donor_countries])

        # Generate synthetic for full period
        full_donors = self.data[
            self.data['country'].isin(self.donor_countries)
        ].pivot_table(
            values=self.outcome_var,
            index='date',
            columns='country',
            aggfunc='sum'
        )

        # Ensure column order matches donor_countries
        full_donors = full_donors[self.donor_countries]

        # Compute synthetic
        synthetic_values = full_donors.values @ weight_array

        # Get actual values
        actual_values = self.data[
            self.data['country'] == self.config.target_country
        ].groupby('date')[self.outcome_var].sum()

        # Combine into DataFrame
        synthetic_df = pd.DataFrame({
            'date': full_donors.index,
            'actual': actual_values.values,
            'synthetic': synthetic_values
        })

        synthetic_df['gap'] = synthetic_df['actual'] - synthetic_df['synthetic']
        synthetic_df['gap_pct'] = (synthetic_df['gap'] / synthetic_df['synthetic']) * 100

        self.synthetic_df = synthetic_df
        self.results['synthetic_df'] = synthetic_df

        print(f"Generated synthetic for {len(synthetic_df)} time periods")

        return synthetic_df

    def plot_synthetic_vs_actual(self,
                                save_path: Optional[str] = None,
                                product_name: str = "Steel") -> plt.Figure:
        """
        Plot actual vs. synthetic time series.

        Args:
            save_path: Path to save figure
            product_name: Product name for title

        Returns:
            Matplotlib figure
        """
        if not hasattr(self, 'synthetic_df'):
            raise ValueError("Must generate_synthetic() first")

        print("\nPlotting actual vs. synthetic...")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        df = self.synthetic_df

        # Panel 1: Actual vs. Synthetic
        ax1.plot(df['date'], df['actual'], 'o-', label='Actual', linewidth=2, markersize=4)
        ax1.plot(df['date'], df['synthetic'], 's--', label='Synthetic', linewidth=2, markersize=4, alpha=0.7)

        # Add vertical line at treatment
        treatment_date = pd.to_datetime(self.config.post_period_start)
        ax1.axvline(treatment_date, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Tariff')

        ax1.set_ylabel(f'{self.outcome_var.replace("_", " ").title()}', fontsize=12)
        ax1.set_title(f'Synthetic Control: {product_name} Imports ({self.config.target_country})',
                     fontsize=14, fontweight='bold')
        ax1.legend(loc='best', fontsize=11)
        ax1.grid(True, alpha=0.3)

        # Panel 2: Gap (Treatment Effect)
        ax2.plot(df['date'], df['gap'], 'o-', color='darkgreen', linewidth=2, markersize=4)
        ax2.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax2.axvline(treatment_date, color='red', linestyle='--', linewidth=2, alpha=0.5)
        ax2.fill_between(df['date'], 0, df['gap'], alpha=0.3, color='darkgreen')

        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Gap (Actual - Synthetic)', fontsize=12)
        ax2.set_title('Treatment Effect Over Time', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}")

        return fig

    def compute_post_treatment_gaps(self) -> Dict:
        """
        Compute post-treatment gap statistics.

        Returns:
            Dictionary with gap statistics
        """
        print("\nComputing post-treatment gaps...")

        if not hasattr(self, 'synthetic_df'):
            raise ValueError("Must generate_synthetic() first")

        # Split pre and post
        post_start = pd.to_datetime(self.config.post_period_start)
        df = self.synthetic_df

        post_df = df[df['date'] >= post_start]
        pre_df = df[df['date'] < post_start]

        # Compute statistics
        gap_stats = {
            'mean_gap': post_df['gap'].mean(),
            'median_gap': post_df['gap'].median(),
            'mean_gap_pct': post_df['gap_pct'].mean(),
            'cumulative_gap': post_df['gap'].sum(),
            'mean_pre_gap': pre_df['gap'].mean(),
            'rmse_pre': np.sqrt(np.mean(pre_df['gap'] ** 2)),
            'rmse_post': np.sqrt(np.mean(post_df['gap'] ** 2)),
            'n_post_periods': len(post_df)
        }

        self.results['gap_statistics'] = gap_stats

        print(f"\nPost-Treatment Gap Statistics:")
        print(f"  Mean gap: {gap_stats['mean_gap']:,.2f}")
        print(f"  Mean gap (%): {gap_stats['mean_gap_pct']:.2f}%")
        print(f"  Cumulative gap: {gap_stats['cumulative_gap']:,.2f}")
        print(f"  RMSE (pre): {gap_stats['rmse_pre']:.2f}")
        print(f"  RMSE (post): {gap_stats['rmse_post']:.2f}")

        return gap_stats

    def leave_one_out_sensitivity(self, outcome_var: str = 'import_value') -> pd.DataFrame:
        """
        Run leave-one-out sensitivity analysis.

        For each donor country, re-estimate synthetic control excluding that donor
        and compute the gap. Large changes indicate sensitivity to that donor.

        Args:
            outcome_var: Outcome variable

        Returns:
            DataFrame with LOO results
        """
        print("\nRunning leave-one-out sensitivity analysis...")
        print("This may take a while...")

        if not self.weights:
            raise ValueError("Must fit_weights() first")

        # Get donors with non-trivial weight
        important_donors = [c for c, w in self.weights.items() if w > 0.01]

        loo_results = []

        for excluded_country in important_donors:
            print(f"  Excluding {excluded_country}...")

            # Create donor pool without this country
            loo_donors = [c for c in self.donor_countries if c != excluded_country]

            # Fit weights
            self.fit_weights(outcome_var=outcome_var, donor_countries=loo_donors)

            # Generate synthetic
            self.generate_synthetic()

            # Compute gap
            gap_stats = self.compute_post_treatment_gaps()

            loo_results.append({
                'excluded_country': excluded_country,
                'original_weight': self.weights.get(excluded_country, 0),
                'mean_gap': gap_stats['mean_gap'],
                'mean_gap_pct': gap_stats['mean_gap_pct'],
                'rmse_pre': gap_stats['rmse_pre']
            })

        # Re-fit with full donor pool
        print("\nRe-fitting with full donor pool...")
        self.fit_weights(outcome_var=outcome_var, donor_countries=self.donor_countries)
        self.generate_synthetic()

        # Create results DataFrame
        loo_df = pd.DataFrame(loo_results)
        loo_df = loo_df.sort_values('original_weight', ascending=False)

        self.results['loo_sensitivity'] = loo_df

        print("\nLeave-One-Out Sensitivity (Top 5):")
        print(loo_df.head().to_string(index=False))

        return loo_df

    def plot_donor_contributions(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot donor country weight contributions.

        Args:
            save_path: Path to save figure

        Returns:
            Matplotlib figure
        """
        if not self.weights:
            raise ValueError("Must fit_weights() first")

        print("\nPlotting donor contributions...")

        # Filter to non-zero weights
        nonzero = {k: v for k, v in self.weights.items() if v > 0.001}
        nonzero_sorted = dict(sorted(nonzero.items(), key=lambda x: -x[1]))

        # Take top 15
        top_n = 15
        plot_weights = dict(list(nonzero_sorted.items())[:top_n])

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        countries = list(plot_weights.keys())
        weights = list(plot_weights.values())

        bars = ax.barh(countries, weights, color='steelblue', alpha=0.7)

        # Add value labels
        for i, (country, weight) in enumerate(plot_weights.items()):
            ax.text(weight + 0.01, i, f'{weight:.3f}', va='center', fontsize=9)

        ax.set_xlabel('Weight', fontsize=12)
        ax.set_title(f'Donor Country Contributions (Top {len(plot_weights)})', fontsize=14, fontweight='bold')
        ax.set_xlim(0, max(weights) * 1.15)
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}")

        return fig

    def save_artifacts(self, output_dir: str, product: str):
        """
        Save all model artifacts.

        Args:
            output_dir: Directory to save artifacts
            product: Product identifier
        """
        output_path = Path(output_dir) / product
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\nSaving artifacts to {output_path}...")

        # 1. Save results pickle
        with open(output_path / f'{product}_synth_results.pkl', 'wb') as f:
            pickle.dump(self.results, f)
        print("✓ Saved results pickle")

        # 2. Save weights as JSON
        weights_export = {
            'product': product,
            'target_country': self.config.target_country,
            'weights': self.weights,
            'n_donors': len(self.donor_countries),
            'n_nonzero_weights': sum(1 for w in self.weights.values() if w > 0.001)
        }
        with open(output_path / f'{product}_weights.json', 'w') as f:
            json.dump(weights_export, f, indent=2)
        print("✓ Saved weights")

        # 3. Save synthetic time series
        if hasattr(self, 'synthetic_df'):
            self.synthetic_df.to_csv(output_path / f'{product}_synthetic_timeseries.csv', index=False)
            print("✓ Saved synthetic time series")

        # 4. Save gap statistics
        if 'gap_statistics' in self.results:
            with open(output_path / f'{product}_gap_stats.json', 'w') as f:
                json.dump(self.results['gap_statistics'], f, indent=2)
            print("✓ Saved gap statistics")

        # 5. Save plots
        if hasattr(self, 'synthetic_df'):
            self.plot_synthetic_vs_actual(save_path=str(output_path / f'{product}_synth_vs_actual.png'),
                                         product_name=product)
            self.plot_donor_contributions(save_path=str(output_path / f'{product}_donor_weights.png'))
            print("✓ Saved plots")

        # 6. Save LOO sensitivity
        if 'loo_sensitivity' in self.results:
            self.results['loo_sensitivity'].to_csv(
                output_path / f'{product}_loo_sensitivity.csv', index=False)
            print("✓ Saved LOO sensitivity")

        print(f"\n✓ All artifacts saved successfully")


def run_synth_pipeline(data_path: str,
                      product: str,
                      output_dir: str,
                      donor_countries: Optional[List[str]] = None,
                      config: Optional[SyntheticControlConfig] = None):
    """
    Run full synthetic control pipeline for a single product.

    Args:
        data_path: Path to panel data
        product: Product code
        output_dir: Directory for outputs
        donor_countries: Donor pool (optional)
        config: Configuration (optional)
    """
    print(f"\n{'='*60}")
    print(f"SYNTHETIC CONTROL PIPELINE: {product}")
    print(f"{'='*60}")

    # Initialize model
    sc = SyntheticControl(config=config)

    # Load data
    sc.load_data(data_path, product)

    # Fit weights
    sc.fit_weights(outcome_var='import_value', donor_countries=donor_countries)

    # Generate synthetic
    sc.generate_synthetic()

    # Plot
    sc.plot_synthetic_vs_actual(product_name=product)

    # Compute gaps
    sc.compute_post_treatment_gaps()

    # Sensitivity analysis
    # sc.leave_one_out_sensitivity()  # Uncomment to run (computationally intensive)

    # Save artifacts
    sc.save_artifacts(output_dir, product)

    print(f"\n{'='*60}")
    print(f"Pipeline completed for {product}")
    print(f"{'='*60}\n")

    return sc


def main():
    """
    Example usage: Run synthetic control for multiple products.
    """
    # Define products to analyze
    products = ['HRC', 'CRC', 'plate']

    # Configuration
    config = SyntheticControlConfig(
        pre_period_start='2010-01-01',
        pre_period_end='2017-12-31',
        post_period_start='2018-03-01',
        target_country='USA'
    )

    # Run for each product
    # for product in products:
    #     run_synth_pipeline(
    #         data_path='data/clean/steel_panel.parquet',
    #         product=product,
    #         output_dir='models/artifacts/synthetic_control',
    #         config=config
    #     )

    print("\nSynthetic Control pipeline template created successfully!")
    print("Uncomment the loop above and provide your data path to run for multiple products.")


if __name__ == "__main__":
    main()
