# Quick Start Guide
## Steel Distribution Market Analysis

This guide will help you get started with the analysis in 5 minutes.

## Prerequisites

- Python 3.9+
- pip or conda

## Installation

```bash
# Navigate to project directory
cd steel-distribution-analysis

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Demo (Using Sample Data)

### Option 1: Run Full Pipeline

```bash
# Run complete analysis pipeline
python scripts/run_full_pipeline.py
```

This will execute:
1. Data acquisition (creates sample data)
2. Data cleaning
3. Feature engineering
4. Clustering analysis
5. Predictive modeling
6. Momentum analysis
7. Spatial visualizations

**Time:** ~5-10 minutes

### Option 2: Run Individual Steps

```bash
# Step 1: Generate sample data
python scripts/01_download_data.py

# Step 2: Clean and transform
python scripts/02_clean_data.py

# Step 3: Engineer features
python scripts/03_engineer_features.py

# Step 4: Cluster analysis
python models/clustering/clustering_model.py

# Step 5: Demand prediction
python models/regression/demand_prediction.py

# Step 6: Momentum analysis
python models/timeseries/momentum_analysis.py

# Step 7: Spatial visualizations
python viz/spatial_analysis.py
```

### Option 3: Interactive Notebooks

```bash
# Launch Jupyter
jupyter notebook

# Open notebooks in analysis/ directory:
# - regional_archetypes.ipynb
# - demand_forecast.ipynb
```

## Outputs

After running the pipeline, you'll find:

### Data Files
- `data/clean/` - Cleaned MSA panel data
- `features/` - Engineered features

### Models
- `models/clustering/` - Cluster assignments and profiles
- `models/regression/` - Demand prediction models and results
- `models/timeseries/` - Momentum analysis results

### Visualizations
- `viz/` - All charts, maps, and plots

### Reports
- `reports/executive_summary.md` - Strategic recommendations
- `reports/top_20_opportunities.csv` - Ranked expansion targets

## Key Outputs to Review

1. **Executive Summary:** `reports/executive_summary.md`
2. **Cluster Profiles:** `viz/cluster_radar_charts.png`
3. **Model Performance:** `viz/model_comparison.png`
4. **Momentum Map:** `viz/momentum_analysis.png`
5. **Competitive Landscape:** `viz/competitive_landscape.png`
6. **Top Opportunities:** `viz/opportunity_ranking.csv`

## Next Steps

### For Business Users
1. Read `reports/executive_summary.md`
2. Review visualizations in `viz/` directory
3. Examine top expansion candidates in CSV outputs

### For Technical Users
1. Open Jupyter notebooks in `analysis/` directory
2. Review model code in `models/` directories
3. Customize feature engineering in `scripts/03_engineer_features.py`
4. Adjust model hyperparameters in regression/clustering scripts

### For Data Scientists
1. Examine feature importance outputs
2. Review model comparison metrics
3. Extend with additional data sources (see data acquisition scripts)
4. Validate predictions against industry benchmarks

## Using Your Own Data

To use real data instead of sample data:

1. **Census API:** Get API key from https://api.census.gov/data/key_signup.html
2. **BLS API:** Register at https://data.bls.gov/registrationEngine/
3. Update `scripts/01_download_data.py` with your API keys
4. Uncomment real data download functions
5. Re-run pipeline

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

### Missing Data
```bash
# Regenerate sample data
python scripts/01_download_data.py
```

### Visualization Issues
```bash
# Install additional dependencies
pip install matplotlib seaborn plotly --upgrade
```

## Project Structure

```
steel-distribution-analysis/
├── data/              # Raw and cleaned data
├── features/          # Engineered features
├── models/            # Trained models and results
│   ├── clustering/
│   ├── regression/
│   └── timeseries/
├── viz/               # Visualizations
├── analysis/          # Jupyter notebooks
├── reports/           # Executive summaries
└── scripts/           # Pipeline scripts
```

## Support

For questions or issues:
1. Check `README.md` for detailed documentation
2. Review code comments in individual scripts
3. Examine notebook outputs for examples

## License

Educational and portfolio use.
