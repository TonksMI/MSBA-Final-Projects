# Regional Demand Heterogeneity & Market Expansion Analysis for Steel Distribution

## Executive Summary

This project analyzes regional steel demand patterns across US metropolitan areas to identify optimal locations for distribution center expansion. Using public data from Census Bureau, BLS, and construction permit databases, we develop predictive models and spatial analytics to guide capital allocation decisions.

## Business Objectives

1. **Identify high-growth regions** that justify new warehouses or distribution centers
2. **Classify metro areas** by demand characteristics and growth potential
3. **Map competitive landscape** to find underserved markets
4. **Predict steel demand** using manufacturing, construction, and demographic indicators
5. **Rank expansion candidates** with ROI logic and risk assessment

## Project Structure

```
steel-distribution-analysis/
├── data/
│   ├── raw/              # Source data files (Census, BLS, permits)
│   ├── clean/            # Processed and merged datasets
│   └── geo/              # Shapefiles and geographic data
├── features/             # Engineered features and composite indicators
├── models/               # Trained models and pipelines
│   ├── clustering/       # Regional archetype models
│   ├── regression/       # Demand prediction models
│   └── timeseries/       # Momentum and trend analysis
├── viz/                  # Visualization scripts and outputs
├── analysis/             # Jupyter notebooks with full analysis
├── reports/              # Executive summaries and recommendations
└── scripts/              # Data acquisition and processing utilities
```

## Key Methodologies

### 1. **Regional Clustering**
- K-Means and Hierarchical clustering to identify metro archetypes
- Segments include: Manufacturing Hubs, Construction Boomtowns, Logistics Gateways, etc.

### 2. **Demand Prediction**
- Multiple models: Linear Regression, Random Forest, Gradient Boosting, Elastic Net
- Features: manufacturing employment, building permits, infrastructure spending, demographics

### 3. **Time-Series Momentum**
- Construction permit trends and growth acceleration
- Structural break detection for boom/bust cycles

### 4. **Spatial Analysis**
- Moran's I for spatial autocorrelation
- LISA for local cluster identification
- Geographic heatmaps of demand intensity

### 5. **Competitive Intelligence**
- Competitor facility mapping
- Identification of high-demand, low-competition markets

## Data Sources

| Source | Use Case | Frequency |
|--------|----------|-----------|
| County Business Patterns | Manufacturing establishments by NAICS | Annual |
| Building Permits Survey | Construction activity leading indicator | Monthly |
| Census ACS | Demographics and migration | Annual |
| BLS Regional Employment | Industry-specific job counts | Quarterly |
| State Infrastructure Trackers | Public project spending | Varies |
| USGS Minerals | Steel consumption benchmarks | Annual |

## Key Deliverables

1. **Market Opportunity Map** - Choropleth showing demand intensity and growth
2. **Top 10 Expansion Candidates** - Ranked list with ROI projections
3. **Regional Archetype Profiles** - Detailed segment characteristics
4. **Demand Forecasts** - 3-year predictions by metro area
5. **Competitive Gap Analysis** - White space identification

## Installation & Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download data (requires API keys for some sources)
python scripts/download_data.py
```

## Usage

### Data Pipeline
```bash
# Run full data pipeline
python scripts/run_pipeline.py

# Or run individual steps
python scripts/01_download_data.py
python scripts/02_clean_data.py
python scripts/03_engineer_features.py
```

### Analysis Notebooks
```bash
jupyter notebook analysis/regional_archetypes.ipynb
jupyter notebook analysis/demand_forecast.ipynb
```

### Generate Reports
```bash
python scripts/generate_executive_report.py
```

## Key Findings

*[To be populated after analysis completion]*

## Strategic Recommendations

*[To be populated after analysis completion]*

## Technical Stack

- **Data Processing**: pandas, numpy, geopandas
- **Modeling**: scikit-learn, xgboost, statsmodels
- **Spatial Analysis**: PySAL, shapely, folium
- **Visualization**: matplotlib, seaborn, plotly, altair
- **Notebooks**: Jupyter, papermill

## Authors

MSBA Final Project - Steel Distribution Market Analysis

## License

For educational and portfolio purposes.
