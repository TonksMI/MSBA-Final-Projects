"""
Steel Demand Prediction Models
Implements multiple regression models to forecast regional steel demand
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Set up paths
BASE_DIR = Path(__file__).parent.parent.parent
FEATURES_DIR = BASE_DIR / 'features'
MODELS_DIR = BASE_DIR / 'models' / 'regression'
VIZ_DIR = BASE_DIR / 'viz'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class SteelDemandPredictor:
    """Predicts steel demand using multiple regression models"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}
        self.feature_importance = {}

    def load_data(self) -> pd.DataFrame:
        """Load full feature dataset"""
        print("Loading feature data...")
        df = pd.read_parquet(FEATURES_DIR / 'msa_features_full.parquet')
        print(f"  Loaded {len(df)} records")
        return df

    def prepare_modeling_data(self, df: pd.DataFrame):
        """Prepare features and target for modeling"""
        print("\nPreparing modeling data...")

        # Target variable
        target = 'steel_demand_index'

        # Feature selection (from feature engineering)
        feature_cols = [
            # Core metrics
            'population',
            'median_income',
            'manufacturing_emp',
            'construction_emp',
            'building_permits',
            'infra_spending_millions',

            # Per capita metrics
            'mfg_emp_per_capita',
            'constr_emp_per_capita',
            'permits_per_capita',

            # Growth metrics
            'population_growth',
            'manufacturing_emp_growth',
            'construction_emp_growth',
            'building_permits_growth',

            # Composite indices
            'manufacturing_intensity_index',
            'construction_momentum_index',
            'demographic_tailwind_index',

            # Interaction features
            'mfg_constr_interaction',
            'income_permits_interaction',

            # Industry metrics
            'industry_diversity_index',
        ]

        # Add lagged features if available
        lag_features = [col for col in df.columns if 'lag1' in col]
        feature_cols.extend(lag_features[:5])

        # Ensure all features exist and have no missing values
        feature_cols = [f for f in feature_cols if f in df.columns]

        # Remove rows with missing target or features
        df_model = df[feature_cols + [target]].dropna()

        X = df_model[feature_cols]
        y = df_model[target]

        print(f"  ✓ Features: {len(feature_cols)}")
        print(f"  ✓ Samples: {len(df_model)}")
        print(f"  ✓ Target: {target}")

        return X, y, feature_cols

    def split_data(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Split data into train and test sets"""
        print(f"\nSplitting data (test size: {test_size})...")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        print(f"  ✓ Train samples: {len(X_train)}")
        print(f"  ✓ Test samples: {len(X_test)}")

        return X_train_scaled, X_test_scaled, y_train, y_test, X_train, X_test

    def train_linear_regression(self, X_train, y_train, X_test, y_test):
        """Train Linear Regression model"""
        print("\n[1/4] Training Linear Regression...")

        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        # Metrics
        results = self._calculate_metrics('Linear Regression', y_train, y_train_pred, y_test, y_test_pred)

        self.models['linear'] = model
        self.results['linear'] = results

        print(f"  ✓ Train R²: {results['train_r2']:.4f}")
        print(f"  ✓ Test R²: {results['test_r2']:.4f}")
        print(f"  ✓ Test RMSE: {results['test_rmse']:.4f}")

    def train_elastic_net(self, X_train, y_train, X_test, y_test):
        """Train Elastic Net with hyperparameter tuning"""
        print("\n[2/4] Training Elastic Net...")

        param_grid = {
            'alpha': [0.1, 0.5, 1.0, 5.0],
            'l1_ratio': [0.2, 0.5, 0.8]
        }

        model = ElasticNet(random_state=42, max_iter=2000)
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='r2', n_jobs=-1)
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_

        # Predictions
        y_train_pred = best_model.predict(X_train)
        y_test_pred = best_model.predict(X_test)

        # Metrics
        results = self._calculate_metrics('Elastic Net', y_train, y_train_pred, y_test, y_test_pred)
        results['best_params'] = grid_search.best_params_

        self.models['elasticnet'] = best_model
        self.results['elasticnet'] = results

        print(f"  ✓ Best params: {grid_search.best_params_}")
        print(f"  ✓ Train R²: {results['train_r2']:.4f}")
        print(f"  ✓ Test R²: {results['test_r2']:.4f}")
        print(f"  ✓ Test RMSE: {results['test_rmse']:.4f}")

    def train_random_forest(self, X_train, y_train, X_test, y_test, feature_names):
        """Train Random Forest with hyperparameter tuning"""
        print("\n[3/4] Training Random Forest...")

        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [5, 10],
            'min_samples_leaf': [2, 4]
        }

        model = RandomForestRegressor(random_state=42, n_jobs=-1)

        # Use smaller param grid for speed
        grid_search = GridSearchCV(model, param_grid, cv=3, scoring='r2', n_jobs=-1, verbose=0)
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_

        # Predictions
        y_train_pred = best_model.predict(X_train)
        y_test_pred = best_model.predict(X_test)

        # Metrics
        results = self._calculate_metrics('Random Forest', y_train, y_train_pred, y_test, y_test_pred)
        results['best_params'] = grid_search.best_params_

        # Feature importance
        self.feature_importance['random_forest'] = pd.DataFrame({
            'feature': feature_names,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)

        self.models['random_forest'] = best_model
        self.results['random_forest'] = results

        print(f"  ✓ Best params: {grid_search.best_params_}")
        print(f"  ✓ Train R²: {results['train_r2']:.4f}")
        print(f"  ✓ Test R²: {results['test_r2']:.4f}")
        print(f"  ✓ Test RMSE: {results['test_rmse']:.4f}")

    def train_gradient_boosting(self, X_train, y_train, X_test, y_test, feature_names):
        """Train Gradient Boosting with hyperparameter tuning"""
        print("\n[4/4] Training Gradient Boosting...")

        param_grid = {
            'n_estimators': [100, 200],
            'learning_rate': [0.05, 0.1],
            'max_depth': [3, 5],
            'subsample': [0.8, 1.0]
        }

        model = GradientBoostingRegressor(random_state=42)
        grid_search = GridSearchCV(model, param_grid, cv=3, scoring='r2', n_jobs=-1, verbose=0)
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_

        # Predictions
        y_train_pred = best_model.predict(X_train)
        y_test_pred = best_model.predict(X_test)

        # Metrics
        results = self._calculate_metrics('Gradient Boosting', y_train, y_train_pred, y_test, y_test_pred)
        results['best_params'] = grid_search.best_params_

        # Feature importance
        self.feature_importance['gradient_boosting'] = pd.DataFrame({
            'feature': feature_names,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)

        self.models['gradient_boosting'] = best_model
        self.results['gradient_boosting'] = results

        print(f"  ✓ Best params: {grid_search.best_params_}")
        print(f"  ✓ Train R²: {results['train_r2']:.4f}")
        print(f"  ✓ Test R²: {results['test_r2']:.4f}")
        print(f"  ✓ Test RMSE: {results['test_rmse']:.4f}")

    def _calculate_metrics(self, model_name, y_train, y_train_pred, y_test, y_test_pred):
        """Calculate regression metrics"""
        return {
            'model': model_name,
            'train_r2': r2_score(y_train, y_train_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_test_pred)),
            'test_mae': mean_absolute_error(y_test, y_test_pred),
        }

    def compare_models(self):
        """Compare performance across all models"""
        print("\n" + "=" * 70)
        print("Model Comparison")
        print("=" * 70)

        comparison_df = pd.DataFrame([
            {
                'Model': results['model'],
                'Train R²': results['train_r2'],
                'Test R²': results['test_r2'],
                'Test RMSE': results['test_rmse'],
                'Test MAE': results['test_mae']
            }
            for results in self.results.values()
        ])

        print(comparison_df.to_string(index=False))

        # Visualize comparison
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # R² comparison
        ax1 = axes[0]
        x = np.arange(len(comparison_df))
        width = 0.35
        ax1.bar(x - width/2, comparison_df['Train R²'], width, label='Train R²', alpha=0.8)
        ax1.bar(x + width/2, comparison_df['Test R²'], width, label='Test R²', alpha=0.8)
        ax1.set_xlabel('Model')
        ax1.set_ylabel('R² Score')
        ax1.set_title('Model Performance: R² Score')
        ax1.set_xticks(x)
        ax1.set_xticklabels(comparison_df['Model'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # RMSE comparison
        ax2 = axes[1]
        ax2.bar(comparison_df['Model'], comparison_df['Test RMSE'], color='coral', alpha=0.7)
        ax2.set_xlabel('Model')
        ax2.set_ylabel('RMSE')
        ax2.set_title('Model Performance: Test RMSE')
        ax2.set_xticklabels(comparison_df['Model'], rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'model_comparison.png', dpi=300, bbox_inches='tight')
        print(f"\n  ✓ Saved comparison plot: {VIZ_DIR / 'model_comparison.png'}")

        return comparison_df

    def plot_feature_importance(self):
        """Plot feature importance for tree-based models"""
        print("\nPlotting feature importance...")

        if not self.feature_importance:
            print("  No feature importance available (tree-based models only)")
            return

        fig, axes = plt.subplots(1, len(self.feature_importance), figsize=(16, 6))
        if len(self.feature_importance) == 1:
            axes = [axes]

        for idx, (model_name, importance_df) in enumerate(self.feature_importance.items()):
            ax = axes[idx]

            # Plot top 15 features
            top_features = importance_df.head(15)

            ax.barh(range(len(top_features)), top_features['importance'], color='steelblue', alpha=0.7)
            ax.set_yticks(range(len(top_features)))
            ax.set_yticklabels(top_features['feature'])
            ax.set_xlabel('Importance')
            ax.set_title(f'{model_name.replace("_", " ").title()} - Top 15 Features')
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(VIZ_DIR / 'feature_importance.png', dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved feature importance plot: {VIZ_DIR / 'feature_importance.png'}")

    def save_models(self, comparison_df):
        """Save all models and results"""
        print("\nSaving models and results...")

        # Save models
        for name, model in self.models.items():
            with open(MODELS_DIR / f'{name}_model.pkl', 'wb') as f:
                pickle.dump(model, f)

        # Save scaler
        with open(MODELS_DIR / 'scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)

        # Save comparison results
        comparison_df.to_csv(MODELS_DIR / 'model_comparison.csv', index=False)

        # Save feature importance
        for name, importance_df in self.feature_importance.items():
            importance_df.to_csv(MODELS_DIR / f'{name}_feature_importance.csv', index=False)

        print(f"  ✓ Saved to {MODELS_DIR}")

def main():
    """Main execution function"""
    print("=" * 70)
    print("Steel Demand Prediction Models")
    print("=" * 70)

    predictor = SteelDemandPredictor()

    # Load and prepare data
    df = predictor.load_data()
    X, y, feature_names = predictor.prepare_modeling_data(df)
    X_train, X_test, y_train, y_test, X_train_raw, X_test_raw = predictor.split_data(X, y)

    # Train all models
    predictor.train_linear_regression(X_train, y_train, X_test, y_test)
    predictor.train_elastic_net(X_train, y_train, X_test, y_test)
    predictor.train_random_forest(X_train, y_train, X_test, y_test, feature_names)
    predictor.train_gradient_boosting(X_train, y_train, X_test, y_test, feature_names)

    # Compare models
    comparison_df = predictor.compare_models()

    # Plot feature importance
    predictor.plot_feature_importance()

    # Save everything
    predictor.save_models(comparison_df)

    print("\n" + "=" * 70)
    print("Demand prediction modeling complete!")
    print(f"Models saved to: {MODELS_DIR}")
    print(f"Visualizations saved to: {VIZ_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
