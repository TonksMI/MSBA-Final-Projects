# Causal Impact of 2018 Steel Tariffs (Section 232)

**Econometric Analysis Using Difference-in-Differences and Synthetic Control Methods**

---

## Project Overview

This project provides a comprehensive causal analysis of the Section 232 steel tariffs implemented in March 2018. Using advanced econometric techniques, we estimate the causal impact on:

- 📉 **Import volumes** from tariff-affected countries
- 💰 **Import and domestic prices**
- 🏭 **Domestic steel production**
- 🔄 **Source country substitution patterns**

The project includes both:
1. **Complete working implementation** with synthetic data and full analysis results
2. **Modeling framework** for extending the analysis to real-world data from USA Trade Online

---

## Methodology

We employ **two parallel causal inference strategies** to ensure robust estimates:

### 1. Difference-in-Differences (DID)
- Compares treated countries (China, South Korea, Brazil) vs control countries (Canada, Mexico)
- Uses two-way fixed effects with clustered standard errors
- Estimates: `Y_c,t = α + β(Treated × Post) + γ_c + δ_t + ε`

### 2. Synthetic Control Method
- Creates optimal counterfactual using weighted donor pool
- Matches pre-treatment characteristics perfectly
- Extends synthetic unit to post-treatment period

---

## Repository Structure

```
Causal Impact of 2018 Tarrifs/
│
├── data_generator.py               # Synthetic data generation
├── did_analysis.py                 # DID implementation
├── synthetic_control.py            # Synthetic control implementation
├── main_analysis.py                # Main analysis pipeline (synthetic data)
├── data_collection_pipeline.py     # Real data collection pipeline
├── analysis_example.py             # Example analysis workflow
│
├── requirements.txt                # Python dependencies
├── .env.template                   # Template for API keys
├── README.md                       # This file
├── METHODOLOGY_EXPLANATION.md      # Detailed methodology guide
├── DATA_COLLECTION_OVERVIEW.md     # Data collection documentation
├── DATA_COLLECTION_QUICKSTART.md   # Quick start for data collection
│
├── config/                         # Configuration
│   └── config.py                   # Project configuration and parameters
│
├── src/                            # Source modules for data collection
│   ├── collectors/                 # Data collection modules
│   │   ├── census_collector.py    # USA Trade Online / Census data
│   │   ├── bls_collector.py       # Bureau of Labor Statistics data
│   │   ├── fred_collector.py      # Federal Reserve Economic Data
│   │   └── usitc_collector.py     # USITC DataWeb
│   ├── transformers/               # Data transformation modules
│   │   ├── data_cleaner.py        # Data cleaning utilities
│   │   └── panel_constructor.py   # Panel data construction
│   └── utils/                      # Utility functions
│       └── helpers.py              # Helper functions
│
├── data/                           # Data files
│   ├── trade_data.csv              # Generated synthetic trade data
│   ├── domestic_data.csv           # Generated synthetic domestic data
│   ├── raw/                        # Raw data from APIs (gitignored)
│   └── clean/                      # Cleaned panel data (gitignored)
│
├── models/                         # Modeling framework (extensible)
│   ├── did_model.py                # DID estimation pipeline
│   ├── synthetic_control.py        # Synthetic Control implementation
│   └── artifacts/                  # Saved model results
│
├── analysis/                       # Interactive analysis notebooks
│   ├── parallel_trends.ipynb       # Parallel trends diagnostic tests
│   └── event_study.ipynb           # Event-study analysis
│
├── viz/                            # Visualization modules
│   ├── import_trends.py            # Import trend visualizations
│   ├── synthetic_vs_actual.py      # Synthetic control plots
│   └── output/                     # Generated figures
│
├── reports/                        # Analysis reports
│   ├── executive_summary.md        # Business-focused findings
│   └── technical_appendix.md       # Full methodology & results
│
└── results/                        # Analysis outputs
    ├── EXECUTIVE_SUMMARY.txt
    ├── did_import_volume_results.txt
    └── figures/                    # All visualizations
        ├── parallel_trends_*.png
        ├── event_study_*.png
        ├── synthetic_control_*.png
        └── domestic_effects.png
```

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Option 1: Run Complete Analysis with Synthetic Data

```bash
# Run complete analysis pipeline
python main_analysis.py
```

This will:
1. Generate synthetic trade data (mimicking real Census/BLS data)
2. Run DID analysis for import volumes and prices
3. Estimate domestic production responses
4. Analyze source country substitution
5. Perform synthetic control analysis
6. Run all validity tests
7. Generate visualizations and summary report

### Option 2: Collect Real Data from Government APIs

```bash
# Set up API keys (one-time setup)
cp .env.template .env
# Edit .env and add your API keys:
# CENSUS_API_KEY=your_key_here
# FRED_API_KEY=your_key_here
# BLS_API_KEY=your_key_here

# Run data collection pipeline
python data_collection_pipeline.py
```

See [DATA_COLLECTION_QUICKSTART.md](DATA_COLLECTION_QUICKSTART.md) for detailed instructions on:
- Obtaining API keys
- Configuring data collection parameters
- Understanding data sources

### Option 3: Use Modeling Framework with Real Data

#### 1. DID Analysis

```python
from models.did_model import DIDModel

# Initialize model
model = DIDModel(treatment_date="2018-03-23")

# Load cleaned panel data
model.load_panel('data/clean/steel_panel.parquet')

# Define treated countries (subject to 25% tariff)
treated_countries = ['China', 'South Korea', 'Japan', 'Germany', 'Taiwan']
model.create_treatment_indicators(treated_countries=treated_countries)

# Test parallel trends assumption
model.test_parallel_trends()

# Run baseline DID
model.run_base_did(outcome_var='log_import_value')

# Cluster standard errors by country
model.cluster_standard_errors(cluster_var='country')

# Fit event-study specification
model.fit_event_study(leads=12, lags=24)

# Generate plots
model.plot_event_study(save_path='viz/output/event_study.png')

# Save all results
model.save_artifacts('models/artifacts/did')
```

#### 2. Synthetic Control Analysis

```python
from models.synthetic_control import SyntheticControl, SyntheticControlConfig

# Configure analysis
config = SyntheticControlConfig(
    pre_period_start='2010-01-01',
    pre_period_end='2017-12-31',
    post_period_start='2018-03-01',
    target_country='USA'
)

# Initialize model
sc = SyntheticControl(config=config)

# Load data for specific product
sc.load_data('data/clean/steel_panel.parquet', product='HRC')

# Fit donor weights
sc.fit_weights(outcome_var='import_value')

# Generate synthetic counterfactual
sc.generate_synthetic()

# Plot results
sc.plot_synthetic_vs_actual(product_name='Hot-Rolled Coil')

# Compute treatment effects
gap_stats = sc.compute_post_treatment_gaps()

# Sensitivity analysis (optional - computationally intensive)
sc.leave_one_out_sensitivity()

# Save artifacts
sc.save_artifacts('models/artifacts/synthetic_control', 'HRC')
```

#### 3. Running Jupyter Notebooks

```bash
# Start Jupyter
jupyter notebook

# Open analysis notebooks
# - analysis/parallel_trends.ipynb
# - analysis/event_study.ipynb
```

---

## Key Features

✅ **Comprehensive Validity Testing**
- Parallel trends tests
- Event studies (dynamic DID)
- Placebo tests (time, space, product)
- Pre-treatment fit diagnostics

✅ **Robust Inference**
- Clustered standard errors
- Multiple specifications
- Sensitivity analyses

✅ **Professional Visualizations**
- Parallel trends plots
- Event study graphs
- Synthetic control comparisons
- Treatment effect timelines

✅ **Extensible Framework**
- Modular design for easy extension
- Support for real data from USA Trade Online
- Jupyter notebooks for interactive analysis

---

## Key Results (Synthetic Data Analysis)

### Import Volume Effect
- **-35%** reduction in imports from treated countries
- Highly significant (p < 0.001)
- Validated by both DID and Synthetic Control

### Price Effects
- **+20%** increase in import prices
- **+12%** increase in domestic prices
- Net cost increase for steel consumers

### Domestic Response
- **+15%** increase in domestic production
- Partial offset of import reduction
- Evidence of protection effect

---

## Validity Tests

All key assumptions validated:

✅ **Parallel Trends**: No differential pre-treatment trends (p > 0.05)
✅ **Event Study**: No pre-treatment effects, clear post-treatment jump
✅ **Placebo Tests**: No spurious effects detected
✅ **Pre-Treatment Fit**: Excellent (RMSPE < 10% of mean)

---

## Methodology Documentation

For detailed explanation of the econometric methods, assumptions, and testing logic, see:

📘 **[METHODOLOGY_EXPLANATION.md](METHODOLOGY_EXPLANATION.md)**

This document covers:
- Causal inference framework
- DID vs Synthetic Control logic
- Why each test is necessary
- How to interpret results
- Limitations and assumptions

---

## Technical Details

### Data Structure
- **Panel data**: Country × Time (Monthly, 2016-2020)
- **Treatment date**: March 23, 2018
- **Treated countries**: China, South Korea, Brazil, Germany
- **Control countries**: Canada, Mexico

### Statistical Methods
- Two-way fixed effects regression
- Clustered standard errors (by country)
- Constrained optimization (Synthetic Control)
- Bootstrap inference (placebo tests)

### Software
- Python 3.8+
- statsmodels (econometric models)
- scipy (optimization)
- pandas, numpy (data manipulation)
- matplotlib, seaborn (visualization)

---

## Data Sources (for Real Data Extension)

1. **USA Trade Online** (U.S. Census Bureau)
   - Monthly import data by HS code and country
   - Coverage: 1989-present
   - URL: https://usatrade.census.gov/
   - HS codes: 7208, 7209, 7210, 7211, 7212

2. **USITC DataWeb**
   - Detailed tariff rates and trade flows
   - URL: https://dataweb.usitc.gov/

3. **BLS Import Price Indices**
   - Price data by country of origin
   - URL: https://www.bls.gov/mxp/

4. **AISI/Federal Reserve**
   - Domestic steel production data
   - For control variables and context

---

## Use Cases

This project demonstrates:

1. **Causal Inference Skills**
   - Natural experiment design
   - Counterfactual construction
   - Identification strategies

2. **Policy Analysis**
   - Trade policy evaluation
   - Cost-benefit assessment
   - Substitution patterns

3. **Econometric Rigor**
   - Assumption testing
   - Robustness checks
   - Inference under clustering

4. **Data Science**
   - Panel data analysis
   - Optimization algorithms
   - Professional reporting

---

## Extensions

Possible extensions:
- Add more countries to donor pool
- Incorporate product-level heterogeneity
- Analyze employment effects
- Estimate general equilibrium effects
- Compare synthetic results to actual Census/BLS data
- Firm-level analysis using confidential Census data (requires RDC access)
- Welfare analysis: compute consumer/producer surplus changes
- Machine learning: causal forests for heterogeneous effects
- Text analysis: scrape company earnings calls for qualitative impact

---

## References

### Econometric Methods
- Abadie, Diamond, & Hainmueller (2010). "Synthetic Control Methods for Comparative Case Studies." *JASA*
- Angrist & Pischke (2009). *Mostly Harmless Econometrics*
- Bertrand, Duflo, & Mullainathan (2004). "How Much Should We Trust Differences-in-Differences Estimates?" *QJE*
- Callaway & Sant'Anna (2021). "Difference-in-Differences with Multiple Time Periods"
- Cunningham (2021). *Causal Inference: The Mixtape*. Yale University Press

### Trade Policy
- Amiti, Redding, & Weinstein (2019). "The Impact of the 2018 Tariffs on Prices and Welfare." *JEP*
- Fajgelbaum et al. (2020). "The Return to Protectionism." *QJE*
- Flaaen & Pierce (2019). "Disentangling the Effects of the 2018-2019 Tariffs." *Federal Reserve*
- U.S. Department of Commerce. Section 232 Investigation
- USITC. *Steel Import Monitoring and Analysis*
- Congressional Research Service. "Section 232 Tariffs on Steel and Aluminum"

---

## Author

MSBA Final Project - Tariff Causal Analysis

---

## License

This project is for academic/portfolio/educational use only. Data sources retain their original licenses.

---

## Acknowledgments

- **USA Trade Online** for providing comprehensive trade data
- **USITC** for tariff information
- Causal inference methods from Abadie, Athey, Imbens, and others
- *Causal Inference: The Mixtape* by Scott Cunningham for pedagogical clarity

---

**Last Updated:** 2025-11-14
**Status:** ✅ Implementation Complete - Synthetic Data Analysis Functional | Framework Ready for Real Data Extension
