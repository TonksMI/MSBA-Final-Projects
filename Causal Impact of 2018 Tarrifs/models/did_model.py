"""
Difference-in-Differences Model for Section 232 Tariff Analysis

This module implements the DID estimation pipeline for analyzing the causal
impact of 2018 Section 232 tariffs on steel imports.

Pipeline Steps:
1. Load cleaned panel
2. Create treatment indicators
3. Run base DID
4. Cluster SEs
5. Fit event-study model
6. Export coefficient plots
7. Save model artifacts
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class DIDModel:
    """
    Difference-in-Differences estimator for tariff impact analysis.

    Attributes:
        data: Panel data with treatment and control groups
        treatment_date: Date when tariff was implemented (2018-03-23)
        results: Dictionary storing estimation results
        config: Model configuration parameters
    """

    def __init__(self, treatment_date: str = "2018-03-23"):
        """
        Initialize DID model.

        Args:
            treatment_date: Date of tariff implementation (default: March 23, 2018)
        """
        self.treatment_date = pd.to_datetime(treatment_date)
        self.data = None
        self.results = {}
        self.config = {
            'pre_period_start': '2010-01-01',
            'pre_period_end': '2018-03-22',
            'post_period_start': '2018-03-23',
            'post_period_end': '2020-12-31',
            'cluster_var': 'country',
            'time_var': 'month',
            'unit_var': 'product_country',
        }

    def load_panel(self, data_path: str) -> pd.DataFrame:
        """
        Load cleaned panel data.

        Args:
            data_path: Path to cleaned panel data (parquet or csv)

        Returns:
            Loaded and validated panel DataFrame
        """
        print(f"Loading panel data from {data_path}...")

        if data_path.endswith('.parquet'):
            self.data = pd.read_parquet(data_path)
        elif data_path.endswith('.csv'):
            self.data = pd.read_csv(data_path, parse_dates=['date'])
        else:
            raise ValueError("Data must be .parquet or .csv format")

        # Validate required columns
        required_cols = ['date', 'country', 'product', 'import_value', 'import_quantity']
        missing_cols = set(required_cols) - set(self.data.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        print(f"Loaded {len(self.data):,} observations")
        print(f"Time range: {self.data['date'].min()} to {self.data['date'].max()}")
        print(f"Countries: {self.data['country'].nunique()}")
        print(f"Products: {self.data['product'].nunique()}")

        return self.data

    def create_treatment_indicators(self,
                                    treated_countries: Optional[List[str]] = None,
                                    treated_products: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create treatment indicators for DID estimation.

        Creates:
            - treated: Binary indicator for treatment group
            - post: Binary indicator for post-treatment period
            - did: Interaction term (treated × post)

        Args:
            treated_countries: List of countries subject to tariff (e.g., ['China', 'South Korea'])
            treated_products: List of products subject to tariff (e.g., ['HRC', 'CRC', 'plate'])

        Returns:
            Data with treatment indicators
        """
        print("\nCreating treatment indicators...")

        # Default: all countries except Canada and Mexico (initially exempt)
        if treated_countries is None:
            exempt_countries = ['Canada', 'Mexico']
            treated_countries = [c for c in self.data['country'].unique()
                               if c not in exempt_countries]

        # Create indicators
        self.data['treated'] = self.data['country'].isin(treated_countries).astype(int)
        self.data['post'] = (self.data['date'] >= self.treatment_date).astype(int)
        self.data['did'] = self.data['treated'] * self.data['post']

        # Create product-country identifier for clustering
        self.data['product_country'] = (self.data['product'].astype(str) + '_' +
                                        self.data['country'].astype(str))

        # Create time period identifier
        self.data['year_month'] = self.data['date'].dt.to_period('M')

        print(f"Treated countries ({len(treated_countries)}): {', '.join(treated_countries[:5])}...")
        print(f"Control countries: {self.data[self.data['treated']==0]['country'].nunique()}")
        print(f"Pre-treatment obs: {(self.data['post']==0).sum():,}")
        print(f"Post-treatment obs: {(self.data['post']==1).sum():,}")

        return self.data

    def run_base_did(self,
                     outcome_var: str = 'log_import_value',
                     controls: Optional[List[str]] = None) -> sm.regression.linear_model.RegressionResultsWrapper:
        """
        Run base DID regression with two-way fixed effects.

        Specification:
            Y_ict = α + β·DID_ict + γ_i + δ_t + X'_ict·θ + ε_ict

        Where:
            - γ_i: Unit (product-country) fixed effects
            - δ_t: Time (year-month) fixed effects
            - X: Control variables

        Args:
            outcome_var: Dependent variable (default: log_import_value)
            controls: List of control variable names

        Returns:
            Regression results object
        """
        print(f"\nRunning base DID regression...")

        # Create log outcome if needed
        if outcome_var.startswith('log_') and outcome_var not in self.data.columns:
            base_var = outcome_var.replace('log_', '')
            self.data[outcome_var] = np.log(self.data[base_var] + 1)

        # Build formula
        formula_parts = [f"{outcome_var} ~ did"]

        # Add controls
        if controls:
            formula_parts[0] += ' + ' + ' + '.join(controls)

        # Add fixed effects
        formula_parts.append("C(product_country)")
        formula_parts.append("C(year_month)")

        formula = ' + '.join(formula_parts)
        print(f"Formula: {formula}")

        # Fit model (without clustering first)
        model = smf.ols(formula, data=self.data)
        results_basic = model.fit()

        self.results['base_did'] = results_basic

        print("\nBase DID Results (without clustered SEs):")
        print(f"DID coefficient: {results_basic.params['did']:.4f}")
        print(f"Standard error: {results_basic.bse['did']:.4f}")
        print(f"P-value: {results_basic.pvalues['did']:.4f}")
        print(f"R-squared: {results_basic.rsquared:.4f}")
        print(f"N: {results_basic.nobs:,.0f}")

        return results_basic

    def cluster_standard_errors(self,
                                cluster_var: str = 'country') -> sm.regression.linear_model.RegressionResultsWrapper:
        """
        Re-estimate with clustered standard errors.

        Clustering accounts for correlation of errors within groups (typically countries).

        Args:
            cluster_var: Variable to cluster on (default: 'country')

        Returns:
            Results with clustered standard errors
        """
        print(f"\nClustering standard errors by {cluster_var}...")

        if 'base_did' not in self.results:
            raise ValueError("Must run base_did() first")

        # Get the model from base results
        model = self.results['base_did'].model

        # Refit with clustered SEs
        results_clustered = model.fit(cov_type='cluster',
                                      cov_kwds={'groups': self.data[cluster_var]})

        self.results['base_did_clustered'] = results_clustered

        print("\nDID Results with Clustered SEs:")
        print(f"DID coefficient: {results_clustered.params['did']:.4f}")
        print(f"Clustered SE: {results_clustered.bse['did']:.4f}")
        print(f"P-value: {results_clustered.pvalues['did']:.4f}")
        print(f"Number of clusters: {self.data[cluster_var].nunique()}")

        # Compare to non-clustered
        se_ratio = results_clustered.bse['did'] / self.results['base_did'].bse['did']
        print(f"SE inflation factor: {se_ratio:.2f}x")

        return results_clustered

    def fit_event_study(self,
                       outcome_var: str = 'log_import_value',
                       leads: int = 12,
                       lags: int = 24,
                       cluster_var: str = 'country') -> sm.regression.linear_model.RegressionResultsWrapper:
        """
        Fit event-study specification with dynamic treatment effects.

        Estimates separate coefficients for each time period relative to treatment:
            Y_ict = α + Σ β_τ·(Treated_i × 1[t=τ]) + γ_i + δ_t + ε_ict

        This tests:
            - Pre-trends: β_τ should be ~0 for τ < 0
            - Dynamic effects: How β_τ evolves for τ ≥ 0

        Args:
            outcome_var: Dependent variable
            leads: Number of pre-treatment periods to include
            lags: Number of post-treatment periods to include
            cluster_var: Variable for clustering SEs

        Returns:
            Event-study regression results
        """
        print(f"\nFitting event-study specification...")
        print(f"Leads: {leads}, Lags: {lags}")

        # Create log outcome if needed
        if outcome_var.startswith('log_') and outcome_var not in self.data.columns:
            base_var = outcome_var.replace('log_', '')
            self.data[outcome_var] = np.log(self.data[base_var] + 1)

        # Create relative time variable (months relative to treatment)
        self.data['rel_month'] = ((self.data['date'].dt.year - self.treatment_date.year) * 12 +
                                  (self.data['date'].dt.month - self.treatment_date.month))

        # Create event-time indicators (exclude -1 as reference period)
        event_dummies = []
        for tau in range(-leads, lags + 1):
            if tau == -1:  # Reference period
                continue
            dummy_name = f'event_{tau:+d}'
            self.data[dummy_name] = ((self.data['rel_month'] == tau) &
                                     (self.data['treated'] == 1)).astype(int)
            event_dummies.append(dummy_name)

        # Build formula
        formula = f"{outcome_var} ~ " + ' + '.join(event_dummies)
        formula += " + C(product_country) + C(year_month)"

        # Fit model
        model = smf.ols(formula, data=self.data)
        results = model.fit(cov_type='cluster',
                          cov_kwds={'groups': self.data[cluster_var]})

        self.results['event_study'] = results

        # Extract coefficients
        event_coefs = {tau: results.params.get(f'event_{tau:+d}', 0.0)
                      for tau in range(-leads, lags + 1) if tau != -1}
        event_ses = {tau: results.bse.get(f'event_{tau:+d}', 0.0)
                    for tau in range(-leads, lags + 1) if tau != -1}

        self.results['event_study_coefs'] = event_coefs
        self.results['event_study_ses'] = event_ses

        print(f"Event-study R²: {results.rsquared:.4f}")
        print(f"Average pre-treatment effect: {np.mean([v for k, v in event_coefs.items() if k < 0]):.4f}")
        print(f"Average post-treatment effect: {np.mean([v for k, v in event_coefs.items() if k >= 0]):.4f}")

        return results

    def plot_event_study(self,
                        save_path: Optional[str] = None,
                        title: str = "Event Study: Tariff Impact on Steel Imports") -> plt.Figure:
        """
        Plot event-study coefficients with confidence intervals.

        Args:
            save_path: Path to save figure (optional)
            title: Plot title

        Returns:
            Matplotlib figure object
        """
        if 'event_study_coefs' not in self.results:
            raise ValueError("Must run fit_event_study() first")

        print("\nGenerating event-study plot...")

        coefs = self.results['event_study_coefs']
        ses = self.results['event_study_ses']

        # Create arrays for plotting
        periods = sorted(coefs.keys())
        coefficients = [coefs[t] for t in periods]
        conf_lower = [coefs[t] - 1.96 * ses[t] for t in periods]
        conf_upper = [coefs[t] + 1.96 * ses[t] for t in periods]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot coefficients
        ax.plot(periods, coefficients, 'o-', color='navy', linewidth=2, markersize=6, label='Point estimate')
        ax.fill_between(periods, conf_lower, conf_upper, alpha=0.2, color='navy', label='95% CI')

        # Add reference lines
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax.axvline(x=0, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Tariff implementation')

        # Styling
        ax.set_xlabel('Months Relative to Tariff Implementation', fontsize=12)
        ax.set_ylabel('Coefficient Estimate (Log Points)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}")

        return fig

    def test_parallel_trends(self, pre_period_months: int = 24) -> Dict:
        """
        Test parallel trends assumption using pre-treatment data.

        Tests whether treated and control groups had parallel trends before treatment
        by regressing outcome on treated×time interaction in pre-period.

        Args:
            pre_period_months: Number of pre-treatment months to test

        Returns:
            Dictionary with test statistics
        """
        print("\nTesting parallel trends assumption...")

        # Filter to pre-treatment period
        pre_data = self.data[self.data['post'] == 0].copy()

        # Create time trend variable (months from start)
        pre_data['time_trend'] = (pre_data['date'] - pre_data['date'].min()).dt.days / 30

        # Interaction of treated with time trend
        pre_data['treated_x_trend'] = pre_data['treated'] * pre_data['time_trend']

        # Run regression
        formula = "log_import_value ~ treated + time_trend + treated_x_trend + C(product_country)"
        model = smf.ols(formula, data=pre_data)
        results = model.fit(cov_type='cluster', cov_kwds={'groups': pre_data['country']})

        # Extract test statistics
        test_results = {
            'coefficient': results.params['treated_x_trend'],
            'std_error': results.bse['treated_x_trend'],
            'p_value': results.pvalues['treated_x_trend'],
            't_stat': results.tvalues['treated_x_trend'],
            'reject_parallel_trends': results.pvalues['treated_x_trend'] < 0.05
        }

        self.results['parallel_trends_test'] = test_results

        print(f"Treated×Trend coefficient: {test_results['coefficient']:.4f}")
        print(f"P-value: {test_results['p_value']:.4f}")
        print(f"Parallel trends assumption: {'VIOLATED' if test_results['reject_parallel_trends'] else 'SATISFIED'}")

        return test_results

    def save_artifacts(self, output_dir: str):
        """
        Save model artifacts including results, plots, and summary tables.

        Args:
            output_dir: Directory to save artifacts
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\nSaving model artifacts to {output_dir}...")

        # 1. Save results as pickle
        with open(output_path / 'did_results.pkl', 'wb') as f:
            pickle.dump(self.results, f)
        print("✓ Saved results pickle")

        # 2. Save summary statistics as JSON
        summary_stats = {
            'treatment_date': self.treatment_date.strftime('%Y-%m-%d'),
            'n_observations': len(self.data),
            'n_countries': self.data['country'].nunique(),
            'n_products': self.data['product'].nunique(),
            'n_treated_units': self.data[self.data['treated']==1]['product_country'].nunique(),
            'n_control_units': self.data[self.data['treated']==0]['product_country'].nunique(),
        }

        if 'base_did_clustered' in self.results:
            summary_stats['did_coefficient'] = float(self.results['base_did_clustered'].params['did'])
            summary_stats['did_se'] = float(self.results['base_did_clustered'].bse['did'])
            summary_stats['did_pvalue'] = float(self.results['base_did_clustered'].pvalues['did'])

        with open(output_path / 'summary_stats.json', 'w') as f:
            json.dump(summary_stats, f, indent=2)
        print("✓ Saved summary statistics")

        # 3. Save regression table
        if 'base_did_clustered' in self.results:
            with open(output_path / 'regression_table.txt', 'w') as f:
                f.write(self.results['base_did_clustered'].summary().as_text())
            print("✓ Saved regression table")

        # 4. Save event-study plot
        if 'event_study' in self.results:
            self.plot_event_study(save_path=str(output_path / 'event_study_plot.png'))
            print("✓ Saved event-study plot")

            # Save coefficients as CSV
            coefs_df = pd.DataFrame({
                'rel_month': list(self.results['event_study_coefs'].keys()),
                'coefficient': list(self.results['event_study_coefs'].values()),
                'std_error': list(self.results['event_study_ses'].values()),
            })
            coefs_df['ci_lower'] = coefs_df['coefficient'] - 1.96 * coefs_df['std_error']
            coefs_df['ci_upper'] = coefs_df['coefficient'] + 1.96 * coefs_df['std_error']
            coefs_df.to_csv(output_path / 'event_study_coefficients.csv', index=False)
            print("✓ Saved event-study coefficients")

        # 5. Save configuration
        with open(output_path / 'model_config.json', 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
        print("✓ Saved model configuration")

        print(f"\n✓ All artifacts saved successfully")


def main():
    """
    Example usage of DIDModel pipeline.
    """
    # Initialize model
    model = DIDModel(treatment_date="2018-03-23")

    # Load data
    # model.load_panel('data/clean/steel_panel.parquet')

    # Create treatment indicators
    # treated_countries = ['China', 'South Korea', 'Japan', 'Germany', 'Taiwan']
    # model.create_treatment_indicators(treated_countries=treated_countries)

    # Test parallel trends
    # model.test_parallel_trends()

    # Run base DID
    # model.run_base_did(outcome_var='log_import_value')

    # Cluster standard errors
    # model.cluster_standard_errors(cluster_var='country')

    # Fit event study
    # model.fit_event_study(leads=12, lags=24)

    # Plot results
    # model.plot_event_study()

    # Save artifacts
    # model.save_artifacts('models/artifacts/did')

    print("\nDID Pipeline template created successfully!")
    print("Uncomment the lines above and provide your data path to run the full pipeline.")


if __name__ == "__main__":
    main()
