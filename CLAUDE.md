# CLAUDE.md - AI Assistant Guide

## Repository Overview

This repository contains MSBA (Master of Science in Business Analytics) final projects focused on steel distribution industry analytics. The repository is organized around two major analytical projects, each demonstrating advanced quantitative methods and strategic business insights.

**Repository Name:** MSBA-Final-Projects
**Primary Focus:** Steel distribution industry analytics and econometric analysis
**Status:** Active development - projects are in early implementation phase

## Repository Structure

```
MSBA-Final-Projects/
├── README.md                              # Repository overview
├── Causal Impact of 2018 Tarrifs/         # Project 1: Trade policy analysis
│   └── Project Overview.txt               # Detailed project specification
└── Regional Demand Forcasts/              # Project 2: Regional market analysis
    └── Project Overview.txt               # Detailed project specification
```

## Project Descriptions

### Project 1: Causal Impact of Section 232 Tariffs

**Location:** `Causal Impact of 2018 Tarrifs/`

**Business Problem:**
Analyze the causal impact of 2018 Section 232 tariffs (25% on steel imports) on steel distribution economics, import sources, and cost structures. This analysis informs supplier diversification strategy and trade policy risk management.

**Analytical Approach:**
- Difference-in-differences (DID) or Synthetic Control Method (SCM)
- Compare tariff-affected vs. exempt countries
- Test parallel trends assumption
- Conduct placebo tests on pre-tariff periods

**Data Sources:**
- USA Trade Online (Census, monthly import data by HS code)
- USITC DataWeb (tariff rates and trade flows)
- BLS import price indices for steel
- Domestic production data (AISI/Federal Reserve)
- BLS PPI for competing products

**Technical Capabilities:**
- Causal inference (DID/SCM)
- Econometric rigor (parallel trends testing, placebo tests, event studies)
- Policy analysis and natural experiments
- Robustness checks with multiple specifications

**Expected Deliverables:**
- Causal effect estimates of tariff impact
- Import source substitution analysis
- Price passthrough analysis
- Policy recommendations for trade risk management

### Project 2: Regional Demand Heterogeneity and Market Expansion

**Location:** `Regional Demand Forcasts/`

**Business Problem:**
Identify growth opportunities and optimal locations for new distribution centers based on regional steel demand patterns, construction activity, and manufacturing concentration.

**Analytical Approach:**
- Cluster analysis for regional archetypes
- Regression models predicting steel demand intensity by metro area
- Time series analysis of regional construction growth
- Geographic visualization of opportunity zones

**Data Sources:**
- County Business Patterns (Census, establishment/employment data)
- Regional construction spending and building permits
- Census population growth and demographics by MSA
- State infrastructure spending trackers
- BLS regional employment in steel-consuming industries
- USGS state-level steel consumption estimates

**Technical Capabilities:**
- Predictive modeling (regression, random forests)
- Clustering (K-means, hierarchical)
- Spatial analysis and geographic visualization
- Feature engineering for composite demand scores
- Strategic framing for capital allocation decisions

**Expected Deliverables:**
- Regional demand forecasts
- Market opportunity identification
- Distribution center location recommendations
- ROI analysis for market expansion

## Development Workflows

### Project Setup and Structure

When implementing each project, follow this standard structure:

```
Project Name/
├── Project Overview.txt           # Keep original project specification
├── README.md                      # Project-specific documentation
├── data/
│   ├── raw/                      # Original, immutable data
│   ├── processed/                # Cleaned, transformed data
│   └── external/                 # Data from external sources
├── notebooks/
│   ├── 01-data-collection.ipynb # Data gathering and API calls
│   ├── 02-exploratory-analysis.ipynb
│   ├── 03-modeling.ipynb
│   └── 04-results-visualization.ipynb
├── src/
│   ├── __init__.py
│   ├── data/                     # Data loading and processing
│   ├── features/                 # Feature engineering
│   ├── models/                   # Model implementations
│   └── visualization/            # Plotting functions
├── tests/                         # Unit tests
├── reports/
│   ├── figures/                  # Generated graphics
│   └── final_report.pdf          # Final analysis report
├── requirements.txt              # Python dependencies
└── .gitignore                    # Git ignore patterns
```

### Data Management Guidelines

1. **Raw Data:**
   - Never modify raw data files
   - Store in `data/raw/` directory
   - Document data sources in project README
   - Include data dictionaries when available

2. **Processed Data:**
   - Store cleaned data in `data/processed/`
   - Document all transformations
   - Use versioning for different processing stages

3. **Large Files:**
   - Do NOT commit large data files to git
   - Use `.gitignore` for data directories
   - Document where to obtain data in README
   - Consider using data versioning tools (DVC) if needed

### Code Quality Standards

1. **Python Code:**
   - Follow PEP 8 style guidelines
   - Use meaningful variable names
   - Include docstrings for functions
   - Keep functions focused and modular
   - Use type hints where appropriate

2. **Jupyter Notebooks:**
   - Clear markdown explanations between code cells
   - Restart kernel and run all cells before committing
   - Keep notebooks focused on specific tasks
   - Extract reusable code to `src/` modules

3. **Documentation:**
   - Document assumptions clearly
   - Explain analytical choices
   - Include interpretation of results
   - Reference academic papers for methods

### Analysis Standards

#### For Causal Inference Projects:

1. **Identification Strategy:**
   - Clearly state causal question
   - Document identification assumptions
   - Test parallel trends (for DID)
   - Validate synthetic control weights (for SCM)

2. **Robustness Checks:**
   - Multiple control group specifications
   - Placebo tests on pre-treatment periods
   - Alternative bandwidth/matching specifications
   - Sensitivity analysis

3. **Visualization:**
   - Event study plots
   - Parallel trends graphs
   - Synthetic control trajectories
   - Effect size distributions

#### For Predictive Modeling Projects:

1. **Model Development:**
   - Train/validation/test split
   - Cross-validation for hyperparameter tuning
   - Multiple model comparison
   - Feature importance analysis

2. **Model Evaluation:**
   - Appropriate metrics (RMSE, MAE, R², etc.)
   - Residual analysis
   - Prediction interval estimation
   - Out-of-sample validation

3. **Visualization:**
   - Actual vs. predicted plots
   - Feature importance charts
   - Geographic heatmaps
   - Cluster visualizations

### Git Workflow

1. **Branch Strategy:**
   - Main branch contains stable, reviewed code
   - Feature branches for development (use `claude/` prefix for AI-assisted work)
   - Never commit directly to main without review

2. **Commit Messages:**
   - Use descriptive, imperative mood messages
   - Reference project name in multi-project commits
   - Examples:
     - "Add tariff data collection script"
     - "Implement synthetic control method for tariff analysis"
     - "Create regional demand clustering analysis"

3. **What to Commit:**
   - Source code and notebooks
   - Documentation and reports
   - Small reference datasets (< 1MB)
   - Requirements and environment files

4. **What NOT to Commit:**
   - Large data files (> 10MB)
   - API keys or credentials
   - Temporary/cache files
   - Model artifacts (unless small)

## Key Conventions

### Naming Conventions

1. **Files:**
   - Notebooks: `##-descriptive-name.ipynb` (numbered for sequence)
   - Python modules: `lowercase_with_underscores.py`
   - Data files: `descriptive_name_YYYYMMDD.csv`

2. **Variables:**
   - Python: `snake_case` for variables and functions
   - Constants: `UPPER_CASE`
   - Classes: `PascalCase`

3. **Data Columns:**
   - Use descriptive names: `tariff_rate` not `tr`
   - Date columns: `date`, `year_month`, `observation_date`
   - Geographic: `country_code`, `metro_area`, `state_abbr`

### Statistical Notation

- Use consistent notation across projects
- Document Greek letters and mathematical symbols
- Standard conventions:
  - β (beta): Regression coefficients
  - α (alpha): Significance level (typically 0.05)
  - δ (delta): Treatment effect
  - ε (epsilon): Error term

### Domain-Specific Terms

**Steel Industry:**
- HS Code: Harmonized System code for trade classification
- Section 232: Trade policy provision for tariffs
- AISI: American Iron and Steel Institute
- USITC: United States International Trade Commission
- BLS: Bureau of Labor Statistics
- PPI: Producer Price Index
- MSA: Metropolitan Statistical Area

## AI Assistant Guidelines

### When Working on These Projects:

1. **Understand Context:**
   - Read the relevant Project Overview.txt first
   - Understand the business problem before coding
   - Consider both technical rigor and business impact

2. **Data Collection:**
   - Document data sources with URLs
   - Include date accessed
   - Note any data limitations or issues
   - Verify data availability before extensive coding

3. **Methodology:**
   - Follow established econometric/statistical practices
   - Reference academic papers for methods
   - Explain assumptions clearly
   - Implement robustness checks

4. **Code Quality:**
   - Write modular, reusable code
   - Include error handling
   - Add comments for complex logic
   - Create functions for repeated operations

5. **Visualization:**
   - Use publication-quality graphics
   - Clear labels and titles
   - Appropriate color schemes
   - Include legends and annotations

6. **Communication:**
   - Write for a technical but non-specialist audience
   - Explain statistical concepts clearly
   - Connect findings to business implications
   - Provide actionable recommendations

### Common Tasks and Approaches

#### Setting Up a New Analysis:

```python
# Standard imports for these projects
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Configure visualization
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
```

#### Loading Trade Data:

```python
# Example pattern for trade data
df = pd.read_csv('data/raw/trade_data.csv')
df['date'] = pd.to_datetime(df['date'])
df['year_month'] = df['date'].dt.to_period('M')
```

#### Difference-in-Differences Template:

```python
# DID regression specification
# Y_it = β0 + β1*Treated + β2*Post + β3*(Treated*Post) + ε_it
# β3 is the DID estimator (treatment effect)
```

#### Geographic Visualization:

```python
# Use geopandas for maps
import geopandas as gpd
import contextily as ctx  # For basemaps

# Common geographic data sources:
# - US states: Natural Earth or Census Tiger/Line
# - MSAs: Census metropolitan statistical areas
```

### Testing and Validation

1. **Unit Tests:**
   - Test data processing functions
   - Validate statistical calculations
   - Check edge cases

2. **Data Validation:**
   - Check for missing values
   - Verify date ranges
   - Validate foreign keys/joins
   - Confirm units and scales

3. **Statistical Validation:**
   - Check model assumptions
   - Validate coefficient signs
   - Test sensitivity to specifications
   - Compare to literature benchmarks

## External Resources

### Statistical Methods:
- Causal Inference: "Causal Inference: The Mixtape" by Scott Cunningham
- Econometrics: "Mostly Harmless Econometrics" by Angrist & Pischke
- Synthetic Control: Abadie et al. papers

### Data Sources Documentation:
- USA Trade Online: https://usatrade.census.gov/
- USITC DataWeb: https://dataweb.usitc.gov/
- Bureau of Labor Statistics: https://www.bls.gov/
- Census Bureau: https://www.census.gov/

### Python Libraries:
- pandas: Data manipulation
- statsmodels: Statistical models
- scikit-learn: Machine learning
- geopandas: Geographic analysis
- plotly/matplotlib/seaborn: Visualization

## Current Status

Both projects are in the planning/early implementation phase. Project Overview.txt files contain detailed specifications that should guide all development work.

### Next Steps for Implementation:

**Causal Impact of 2018 Tariffs:**
1. Data collection from USA Trade Online and USITC
2. Exploratory data analysis of trade patterns
3. Parallel trends testing
4. DID or SCM implementation
5. Robustness checks and sensitivity analysis

**Regional Demand Forecasts:**
1. Data collection from County Business Patterns and Census
2. Feature engineering for demand indicators
3. Cluster analysis for regional segmentation
4. Predictive model development
5. Geographic visualization and recommendations

## Notes for AI Assistants

- **Note on Typo:** The directory "Causal Impact of 2018 Tarrifs" has a typo (should be "Tariffs"), but maintain this spelling for file paths to avoid breaking references
- **Interdisciplinary Nature:** These projects blend econometrics, statistics, machine learning, and business strategy
- **Audience:** Work should be rigorous enough for academic review but accessible for business stakeholders
- **Reproducibility:** All analyses should be fully reproducible from documented data sources
- **Ethics:** Consider implications of trade policy analysis; present balanced findings

## Questions or Issues?

When working with this repository:
1. Read the relevant Project Overview.txt for detailed context
2. Check this CLAUDE.md for conventions and standards
3. Consult academic references for methodology questions
4. Document decisions and assumptions clearly

---

*Last Updated: 2025-11-14*
*This document should be updated as projects evolve and new conventions are established.*
