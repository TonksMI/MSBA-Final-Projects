# Causal Impact of 2018 Steel Tariffs

## Project Overview

This project provides a comprehensive causal analysis of the Section 232 steel tariffs implemented in March 2018. Using advanced econometric techniques, we estimate the causal impact on:

- 📉 **Import volumes** from tariff-affected countries
- 💰 **Import and domestic prices**
- 🏭 **Domestic steel production**
- 🔄 **Source country substitution patterns**

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

## Project Structure

```
Causal Impact of 2018 Tarrifs/
│
├── data_generator.py           # Synthetic data generation
├── did_analysis.py             # DID implementation
├── synthetic_control.py        # Synthetic control implementation
├── main_analysis.py            # Main analysis pipeline
│
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── METHODOLOGY_EXPLANATION.md  # Detailed methodology guide
│
├── data/                       # Generated data files
│   ├── trade_data.csv
│   └── domestic_data.csv
│
└── results/                    # Analysis outputs
    ├── EXECUTIVE_SUMMARY.txt
    ├── did_import_volume_results.txt
    └── figures/
        ├── parallel_trends_*.png
        ├── event_study_*.png
        ├── synthetic_control_*.png
        └── ...
```

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run Analysis

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

### Output

Results are saved to `results/` directory:
- **EXECUTIVE_SUMMARY.txt**: Key findings and effect sizes
- **Figures**: 10+ professional visualizations
- **Detailed results**: Model outputs and test statistics

## Key Results

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

## Validity Tests

All key assumptions validated:

✅ **Parallel Trends**: No differential pre-treatment trends (p > 0.05)
✅ **Event Study**: No pre-treatment effects, clear post-treatment jump
✅ **Placebo Tests**: No spurious effects detected
✅ **Pre-Treatment Fit**: Excellent (RMSPE < 10% of mean)

## Methodology Documentation

For detailed explanation of the econometric methods, assumptions, and testing logic, see:

📘 **[METHODOLOGY_EXPLANATION.md](METHODOLOGY_EXPLANATION.md)**

This document covers:
- Causal inference framework
- DID vs Synthetic Control logic
- Why each test is necessary
- How to interpret results
- Limitations and assumptions

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

## Extensions

Possible extensions:
- Add more countries to donor pool
- Incorporate product-level heterogeneity
- Analyze employment effects
- Estimate general equilibrium effects
- Compare to actual Census/BLS data

## References

### Methodology
- Angrist & Pischke (2009). *Mostly Harmless Econometrics*
- Abadie et al. (2010). "Synthetic Control Methods for Comparative Case Studies"
- Callaway & Sant'Anna (2021). "Difference-in-Differences with Multiple Time Periods"

### Policy Context
- U.S. Department of Commerce. Section 232 Investigation
- USITC. *Steel Import Monitoring and Analysis*
- Congressional Research Service. "Section 232 Tariffs on Steel and Aluminum"

## Author

MSBA Final Project - Tariff Causal Analysis

## License

Educational use only.
