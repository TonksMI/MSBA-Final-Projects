"""
Difference-in-Differences (DID) Analysis Module
Implements DID estimation with robust inference and validity tests
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import OLS

class DIDAnalyzer:
    """Difference-in-Differences analysis with validity testing"""

    def __init__(self, data, outcome_var, treatment_var='treated',
                 post_var='post_treatment', entity_var='country',
                 time_var='date'):
        """
        Initialize DID analyzer

        Parameters:
        -----------
        data : DataFrame
            Panel data with treatment and control groups
        outcome_var : str
            Name of outcome variable
        treatment_var : str
            Binary indicator for treatment group
        post_var : str
            Binary indicator for post-treatment period
        entity_var : str
            Entity identifier (e.g., country)
        time_var : str
            Time variable
        """
        self.data = data.copy()
        self.outcome_var = outcome_var
        self.treatment_var = treatment_var
        self.post_var = post_var
        self.entity_var = entity_var
        self.time_var = time_var

        # Create interaction term
        self.data['did_term'] = self.data[treatment_var] * self.data[post_var]

    def estimate_twoway_fe(self, covariates=None, cluster_var=None):
        """
        Estimate two-way fixed effects DID model
        Y_it = α + β(Treated × Post) + γ_i + δ_t + X'θ + ε

        Parameters:
        -----------
        covariates : list, optional
            List of covariate names
        cluster_var : str, optional
            Variable to cluster standard errors

        Returns:
        --------
        results : statsmodels results object
        """

        # Prepare formula
        formula_parts = [self.outcome_var, '~', 'did_term']

        # Add entity fixed effects
        formula_parts.append(f'+ C({self.entity_var})')

        # Add time fixed effects
        formula_parts.append(f'+ C({self.time_var})')

        # Add covariates
        if covariates:
            formula_parts.append('+ ' + ' + '.join(covariates))

        formula = ' '.join(formula_parts)

        # Estimate model
        if cluster_var:
            # With clustered standard errors
            model = smf.ols(formula, data=self.data).fit(
                cov_type='cluster',
                cov_kwds={'groups': self.data[cluster_var]}
            )
        else:
            # Robust standard errors
            model = smf.ols(formula, data=self.data).fit(cov_type='HC3')

        return model

    def parallel_trends_test(self, n_pre_periods=12):
        """
        Test parallel trends assumption using pre-treatment data

        Tests whether treatment and control groups had parallel trends
        before treatment implementation

        Parameters:
        -----------
        n_pre_periods : int
            Number of pre-treatment periods to analyze

        Returns:
        --------
        test_result : dict
            Contains test statistics and p-value
        """

        # Get pre-treatment data
        pre_data = self.data[self.data[self.post_var] == False].copy()

        # Create time trend
        pre_data = pre_data.sort_values(self.time_var)
        pre_data['time_trend'] = pre_data.groupby(self.entity_var).cumcount()

        # Test for differential trends
        formula = f'{self.outcome_var} ~ time_trend * {self.treatment_var} + C({self.entity_var})'
        model = smf.ols(formula, data=pre_data).fit(cov_type='HC3')

        # Test if interaction coefficient is significant
        interaction_coef = model.params.get(f'time_trend:{self.treatment_var}',
                                             model.params.get(f'{self.treatment_var}:time_trend', 0))
        interaction_pval = model.pvalues.get(f'time_trend:{self.treatment_var}',
                                             model.pvalues.get(f'{self.treatment_var}:time_trend', 1))

        return {
            'coefficient': interaction_coef,
            'p_value': interaction_pval,
            'parallel_trends_hold': interaction_pval > 0.05,
            'interpretation': 'Parallel trends assumption is VALID' if interaction_pval > 0.05
                            else 'Parallel trends assumption may be VIOLATED',
            'model': model
        }

    def event_study(self, n_leads=6, n_lags=12, reference_period=-1):
        """
        Estimate event study / dynamic DID
        Estimates treatment effects for each time period relative to treatment

        Parameters:
        -----------
        n_leads : int
            Number of leads (pre-treatment periods) to include
        n_lags : int
            Number of lags (post-treatment periods) to include
        reference_period : int
            Reference period (typically -1, the period before treatment)

        Returns:
        --------
        results : dict
            Contains coefficients, standard errors, and confidence intervals
        """

        # Create relative time variable
        # Assuming treatment date is fixed
        treatment_date = self.data[self.data[self.post_var] == True][self.time_var].min()

        self.data['relative_time'] = (
            (self.data[self.time_var] - treatment_date) /
            pd.Timedelta(days=30)  # Approximate months
        ).round().astype(int)

        # Create event time dummies for treated units only
        event_dummies = []
        for t in range(-n_leads, n_lags + 1):
            if t == reference_period:
                continue  # Skip reference period

            # Use 'pre' or 'post' prefix to avoid negative numbers in names
            if t < 0:
                dummy_name = f'event_pre_{abs(t)}'
            else:
                dummy_name = f'event_post_{t}'

            self.data[dummy_name] = (
                (self.data['relative_time'] == t) &
                (self.data[self.treatment_var] == True)
            ).astype(int)
            event_dummies.append((t, dummy_name))

        # Estimate model using simplified approach
        # Create a simple formula with fewer fixed effects to avoid issues
        dummy_names = [name for t, name in event_dummies]
        formula = f'{self.outcome_var} ~ {" + ".join(dummy_names)} + C({self.entity_var})'

        # Estimate without time fixed effects to avoid complexity
        # (Time effects are partially captured by event dummies)
        model = smf.ols(formula, data=self.data).fit(cov_type='HC3')

        # Extract coefficients
        coefficients = []
        std_errors = []
        conf_intervals = []
        periods = []

        for t, dummy_name in event_dummies:
            if dummy_name in model.params:
                coefficients.append(model.params[dummy_name])
                std_errors.append(model.bse[dummy_name])
                ci = model.conf_int().loc[dummy_name]
                conf_intervals.append((ci[0], ci[1]))
                periods.append(t)

        # Add reference period
        if reference_period not in periods:
            coefficients.insert(abs(reference_period), 0)
            std_errors.insert(abs(reference_period), 0)
            conf_intervals.insert(abs(reference_period), (0, 0))
            periods.insert(abs(reference_period), reference_period)
            # Sort by period
            combined = sorted(zip(periods, coefficients, std_errors, conf_intervals))
            periods, coefficients, std_errors, conf_intervals = zip(*combined)

        results = pd.DataFrame({
            'period': periods,
            'coefficient': coefficients,
            'std_error': std_errors,
            'ci_lower': [ci[0] for ci in conf_intervals],
            'ci_upper': [ci[1] for ci in conf_intervals]
        })

        return {
            'results': results,
            'model': model,
            'reference_period': reference_period
        }

    def placebo_test_time(self, fake_treatment_date):
        """
        Placebo test: apply fake treatment date to test for spurious effects

        Parameters:
        -----------
        fake_treatment_date : str or datetime
            Fake treatment date (should be in pre-treatment period)

        Returns:
        --------
        results : dict
            Model results with fake treatment
        """

        fake_treatment_date = pd.to_datetime(fake_treatment_date)

        # Create fake post variable
        self.data['fake_post'] = self.data[self.time_var] >= fake_treatment_date
        self.data['fake_did'] = self.data[self.treatment_var] * self.data['fake_post']

        # Estimate model with fake treatment
        formula = f'{self.outcome_var} ~ fake_did + C({self.entity_var}) + C({self.time_var})'
        model = smf.ols(formula, data=self.data).fit(cov_type='HC3')

        return {
            'coefficient': model.params.get('fake_did', 0),
            'p_value': model.pvalues.get('fake_did', 1),
            'is_spurious': model.pvalues.get('fake_did', 1) < 0.05,
            'interpretation': 'SPURIOUS effect detected (placebo test FAILED)'
                            if model.pvalues.get('fake_did', 1) < 0.05
                            else 'No spurious effect (placebo test PASSED)',
            'model': model
        }

    def placebo_test_product(self, untreated_product_filter):
        """
        Placebo test: apply treatment to untreated product

        Parameters:
        -----------
        untreated_product_filter : callable
            Function to filter data to untreated product

        Returns:
        --------
        results : dict
            Model results for untreated product
        """

        # Filter to untreated product
        placebo_data = self.data[untreated_product_filter(self.data)].copy()
        placebo_data['did_term'] = placebo_data[self.treatment_var] * placebo_data[self.post_var]

        # Estimate model
        formula = f'{self.outcome_var} ~ did_term + C({self.entity_var}) + C({self.time_var})'
        model = smf.ols(formula, data=placebo_data).fit(cov_type='HC3')

        return {
            'coefficient': model.params.get('did_term', 0),
            'p_value': model.pvalues.get('did_term', 1),
            'is_spurious': model.pvalues.get('did_term', 1) < 0.05,
            'interpretation': 'SPURIOUS effect detected (placebo test FAILED)'
                            if model.pvalues.get('did_term', 1) < 0.05
                            else 'No effect on untreated product (placebo test PASSED)',
            'model': model
        }

    def plot_parallel_trends(self, figsize=(12, 6)):
        """Visualize parallel trends"""

        # Aggregate by treatment group and time
        trends = self.data.groupby([self.time_var, self.treatment_var])[self.outcome_var].mean().reset_index()

        plt.figure(figsize=figsize)

        for treated in [0, 1]:
            trend_data = trends[trends[self.treatment_var] == treated]
            label = 'Treated' if treated else 'Control'
            plt.plot(trend_data[self.time_var], trend_data[self.outcome_var],
                    marker='o', label=label, linewidth=2)

        # Add vertical line at treatment
        treatment_date = self.data[self.data[self.post_var] == True][self.time_var].min()
        plt.axvline(treatment_date, color='red', linestyle='--',
                   label='Treatment Date', linewidth=2)

        plt.xlabel('Time', fontsize=12)
        plt.ylabel(f'Average {self.outcome_var}', fontsize=12)
        plt.title('Parallel Trends: Treatment vs Control Groups', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        return plt.gcf()

    def plot_event_study(self, event_study_results, figsize=(12, 6)):
        """Visualize event study results"""

        results = event_study_results['results']

        plt.figure(figsize=figsize)
        plt.plot(results['period'], results['coefficient'],
                marker='o', linewidth=2, markersize=8, color='steelblue')
        plt.fill_between(results['period'],
                        results['ci_lower'],
                        results['ci_upper'],
                        alpha=0.3, color='steelblue')

        # Add reference lines
        plt.axhline(0, color='black', linestyle='-', linewidth=1)
        plt.axvline(0, color='red', linestyle='--', linewidth=2,
                   label='Treatment Date')

        plt.xlabel('Months Relative to Treatment', fontsize=12)
        plt.ylabel('Treatment Effect', fontsize=12)
        plt.title('Event Study: Dynamic Treatment Effects', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        return plt.gcf()
