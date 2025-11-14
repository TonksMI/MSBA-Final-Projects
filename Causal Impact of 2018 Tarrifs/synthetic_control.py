"""
Synthetic Control Method Implementation
Creates synthetic counterfactual using weighted donor pool
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler

class SyntheticControl:
    """Synthetic Control Method for causal inference"""

    def __init__(self, data, treated_unit, outcome_var,
                 time_var='date', unit_var='country',
                 treatment_date=None):
        """
        Initialize Synthetic Control

        Parameters:
        -----------
        data : DataFrame
            Panel data
        treated_unit : str
            Name of treated unit
        outcome_var : str
            Outcome variable name
        time_var : str
            Time variable name
        unit_var : str
            Unit identifier variable name
        treatment_date : str or datetime
            Treatment date
        """
        self.data = data.copy()
        self.treated_unit = treated_unit
        self.outcome_var = outcome_var
        self.time_var = time_var
        self.unit_var = unit_var
        self.treatment_date = pd.to_datetime(treatment_date)

        # Separate treated and donor pool
        self.treated_data = self.data[self.data[unit_var] == treated_unit].copy()
        self.donor_data = self.data[self.data[unit_var] != treated_unit].copy()

        # Pre and post treatment data
        self.pre_treatment_data = self.data[self.data[time_var] < self.treatment_date].copy()
        self.post_treatment_data = self.data[self.data[time_var] >= self.treatment_date].copy()

    def fit(self, predictor_vars=None, time_predictors_prior=None):
        """
        Fit synthetic control by finding optimal weights

        Uses optimization to minimize pre-treatment fit

        Parameters:
        -----------
        predictor_vars : list, optional
            List of predictor variables (in addition to outcome)
        time_predictors_prior : dict, optional
            Dictionary mapping time periods to their importance

        Returns:
        --------
        weights : dict
            Optimal weights for donor units
        """

        # Get donor units
        donor_units = self.donor_data[self.unit_var].unique()

        # Prepare predictor matrix for pre-treatment period
        pre_treated = self.pre_treatment_data[
            self.pre_treatment_data[self.unit_var] == self.treated_unit
        ]
        pre_donors = self.pre_treatment_data[
            self.pre_treatment_data[self.unit_var].isin(donor_units)
        ]

        # Create outcome matrix: rows = time periods, columns = units
        treated_outcome = pre_treated.sort_values(self.time_var)[self.outcome_var].values

        donor_outcomes = {}
        for donor in donor_units:
            donor_outcome = pre_donors[pre_donors[self.unit_var] == donor].sort_values(
                self.time_var
            )[self.outcome_var].values
            donor_outcomes[donor] = donor_outcome

        # Create donor matrix (T x J)
        donor_matrix = np.column_stack([donor_outcomes[donor] for donor in donor_units])

        # Objective function: minimize pre-treatment MSPE
        def objective(weights):
            synthetic = donor_matrix @ weights
            return np.mean((treated_outcome - synthetic) ** 2)

        # Constraints: weights sum to 1 and are non-negative
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = [(0, 1) for _ in donor_units]

        # Initial guess: equal weights
        w0 = np.ones(len(donor_units)) / len(donor_units)

        # Optimize
        result = minimize(objective, w0, method='SLSQP',
                         bounds=bounds, constraints=constraints,
                         options={'ftol': 1e-9, 'maxiter': 1000})

        # Store weights
        self.weights = dict(zip(donor_units, result.x))
        self.donor_units = donor_units
        self.donor_matrix = donor_matrix
        self.treated_outcome_pre = treated_outcome

        # Create synthetic control for full time period
        self._create_synthetic_series()

        return self.weights

    def _create_synthetic_series(self):
        """Create synthetic control series for all time periods"""

        # Create synthetic control using weights
        synthetic_data = []

        for time in sorted(self.data[self.time_var].unique()):
            time_data = self.data[self.data[self.time_var] == time]

            synthetic_value = 0
            for donor, weight in self.weights.items():
                donor_value = time_data[
                    time_data[self.unit_var] == donor
                ][self.outcome_var].values

                if len(donor_value) > 0:
                    synthetic_value += weight * donor_value[0]

            synthetic_data.append({
                self.time_var: time,
                self.outcome_var: synthetic_value,
                'type': 'synthetic'
            })

        self.synthetic_series = pd.DataFrame(synthetic_data)

    def get_treatment_effect(self):
        """
        Calculate treatment effect as gap between treated and synthetic

        Returns:
        --------
        effects : DataFrame
            Treatment effects over time
        """

        treated_series = self.treated_data[[self.time_var, self.outcome_var]].copy()
        treated_series['type'] = 'treated'

        # Merge with synthetic
        comparison = treated_series.merge(
            self.synthetic_series,
            on=self.time_var,
            suffixes=('_treated', '_synthetic')
        )

        comparison['treatment_effect'] = (
            comparison[f'{self.outcome_var}_treated'] -
            comparison[f'{self.outcome_var}_synthetic']
        )

        comparison['post_treatment'] = comparison[self.time_var] >= self.treatment_date

        return comparison

    def get_pre_treatment_fit(self):
        """Calculate pre-treatment RMSPE"""

        effects = self.get_treatment_effect()
        pre_effects = effects[~effects['post_treatment']]

        rmspe = np.sqrt(np.mean(pre_effects['treatment_effect'] ** 2))

        return {
            'RMSPE': rmspe,
            'mean_treated': pre_effects[f'{self.outcome_var}_treated'].mean(),
            'mean_synthetic': pre_effects[f'{self.outcome_var}_synthetic'].mean(),
            'fit_quality': 'Good' if rmspe < 0.1 * pre_effects[f'{self.outcome_var}_treated'].mean()
                          else 'Moderate' if rmspe < 0.2 * pre_effects[f'{self.outcome_var}_treated'].mean()
                          else 'Poor'
        }

    def placebo_test_in_space(self, n_placebos=None):
        """
        Placebo test: apply synthetic control to untreated units

        Tests whether treatment effect is unusually large compared to
        placebo effects in control units

        Parameters:
        -----------
        n_placebos : int, optional
            Number of placebo tests to run

        Returns:
        --------
        placebo_results : DataFrame
            Treatment effects for placebo units
        """

        if n_placebos is None:
            n_placebos = len(self.donor_units)

        placebo_results = []

        for donor in list(self.donor_units)[:n_placebos]:
            # Create synthetic control for this donor
            placebo_sc = SyntheticControl(
                self.data,
                treated_unit=donor,
                outcome_var=self.outcome_var,
                time_var=self.time_var,
                unit_var=self.unit_var,
                treatment_date=self.treatment_date
            )

            # Exclude this donor from donor pool
            placebo_sc.donor_data = placebo_sc.donor_data[
                placebo_sc.donor_data[self.unit_var] != donor
            ]

            try:
                placebo_sc.fit()
                effects = placebo_sc.get_treatment_effect()

                # Calculate post-treatment average effect
                post_effects = effects[effects['post_treatment']]
                avg_effect = post_effects['treatment_effect'].mean()

                placebo_results.append({
                    'unit': donor,
                    'avg_effect': avg_effect,
                    'type': 'placebo'
                })
            except:
                continue

        # Add actual treated unit
        actual_effects = self.get_treatment_effect()
        post_effects = actual_effects[actual_effects['post_treatment']]
        placebo_results.append({
            'unit': self.treated_unit,
            'avg_effect': post_effects['treatment_effect'].mean(),
            'type': 'treated'
        })

        placebo_df = pd.DataFrame(placebo_results)

        # Calculate p-value: proportion of placebos with larger effect
        treated_effect = placebo_df[placebo_df['type'] == 'treated']['avg_effect'].values[0]
        placebo_effects = placebo_df[placebo_df['type'] == 'placebo']['avg_effect'].abs()

        p_value = (placebo_effects >= abs(treated_effect)).mean()

        return {
            'results': placebo_df,
            'p_value': p_value,
            'interpretation': f'Treatment effect is significant (p={p_value:.3f})'
                            if p_value < 0.05
                            else f'Treatment effect is not significant (p={p_value:.3f})'
        }

    def placebo_test_in_time(self, fake_treatment_date):
        """
        Placebo test: use fake treatment date in pre-treatment period

        Parameters:
        -----------
        fake_treatment_date : str or datetime
            Fake treatment date

        Returns:
        --------
        results : dict
            Placebo test results
        """

        fake_treatment_date = pd.to_datetime(fake_treatment_date)

        # Create new synthetic control with fake treatment date
        placebo_sc = SyntheticControl(
            self.data,
            treated_unit=self.treated_unit,
            outcome_var=self.outcome_var,
            time_var=self.time_var,
            unit_var=self.unit_var,
            treatment_date=fake_treatment_date
        )

        placebo_sc.fit()
        effects = placebo_sc.get_treatment_effect()

        # Calculate "treatment effect" in fake post period
        fake_post = effects[effects['post_treatment']]
        avg_fake_effect = fake_post['treatment_effect'].mean()

        return {
            'avg_fake_effect': avg_fake_effect,
            'interpretation': 'Placebo test PASSED (no pre-treatment effect)'
                            if abs(avg_fake_effect) < abs(self.get_treatment_effect()[
                                self.get_treatment_effect()['post_treatment']
                            ]['treatment_effect'].mean()) * 0.5
                            else 'Placebo test FAILED (spurious pre-treatment effect detected)'
        }

    def plot_synthetic_control(self, figsize=(12, 6)):
        """Visualize synthetic control vs treated unit"""

        effects = self.get_treatment_effect()

        plt.figure(figsize=figsize)

        # Plot treated unit
        plt.plot(effects[self.time_var],
                effects[f'{self.outcome_var}_treated'],
                label=f'Treated: {self.treated_unit}',
                linewidth=2.5, color='steelblue', marker='o', markersize=4)

        # Plot synthetic control
        plt.plot(effects[self.time_var],
                effects[f'{self.outcome_var}_synthetic'],
                label='Synthetic Control',
                linewidth=2.5, color='darkorange', linestyle='--', marker='s', markersize=4)

        # Add vertical line at treatment
        plt.axvline(self.treatment_date, color='red', linestyle='-',
                   linewidth=2, label='Treatment Date', alpha=0.7)

        plt.xlabel('Time', fontsize=12)
        plt.ylabel(self.outcome_var, fontsize=12)
        plt.title('Synthetic Control vs Treated Unit', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        return plt.gcf()

    def plot_treatment_effect(self, figsize=(12, 6)):
        """Visualize treatment effect (gap between treated and synthetic)"""

        effects = self.get_treatment_effect()

        plt.figure(figsize=figsize)

        # Plot treatment effect
        plt.plot(effects[self.time_var],
                effects['treatment_effect'],
                linewidth=2.5, color='darkgreen', marker='o', markersize=5)

        # Add horizontal line at zero
        plt.axhline(0, color='black', linestyle='-', linewidth=1)

        # Add vertical line at treatment
        plt.axvline(self.treatment_date, color='red', linestyle='--',
                   linewidth=2, label='Treatment Date', alpha=0.7)

        # Shade post-treatment period
        plt.axvspan(self.treatment_date, effects[self.time_var].max(),
                   alpha=0.2, color='gray', label='Post-Treatment')

        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Treatment Effect (Gap)', fontsize=12)
        plt.title('Causal Effect: Treated - Synthetic Control', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        return plt.gcf()

    def plot_weights(self, figsize=(10, 6)):
        """Visualize donor weights"""

        weights_df = pd.DataFrame({
            'Donor': list(self.weights.keys()),
            'Weight': list(self.weights.values())
        }).sort_values('Weight', ascending=True)

        # Only show non-zero weights
        weights_df = weights_df[weights_df['Weight'] > 0.01]

        plt.figure(figsize=figsize)
        plt.barh(weights_df['Donor'], weights_df['Weight'], color='steelblue')
        plt.xlabel('Weight', fontsize=12)
        plt.ylabel('Donor Unit', fontsize=12)
        plt.title('Synthetic Control Weights', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()

        return plt.gcf()

    def plot_placebo_tests(self, placebo_results, figsize=(10, 6)):
        """Visualize placebo test results"""

        results = placebo_results['results']

        plt.figure(figsize=figsize)

        # Plot placebo effects
        placebos = results[results['type'] == 'placebo']
        treated = results[results['type'] == 'treated']

        plt.scatter(range(len(placebos)), placebos['avg_effect'].values,
                   alpha=0.6, s=100, color='lightgray', label='Placebo Units')

        plt.scatter(len(placebos), treated['avg_effect'].values,
                   s=200, color='red', marker='*', label='Treated Unit',
                   edgecolors='darkred', linewidths=2, zorder=10)

        plt.axhline(0, color='black', linestyle='--', linewidth=1)
        plt.xlabel('Unit', fontsize=12)
        plt.ylabel('Average Treatment Effect', fontsize=12)
        plt.title(f'Placebo Test: In-Space\n{placebo_results["interpretation"]}',
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        return plt.gcf()
