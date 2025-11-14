# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys (Optional for Testing)
```bash
cp .env.template .env
# Edit .env with your API keys (or skip for synthetic data testing)
```

### 3. Run the Pipeline
```bash
# Full pipeline with synthetic data (for testing)
python main.py

# Or with real data (requires API keys)
python main.py
```

### 4. Run Example Analysis
```bash
python analysis_example.py
```

## Expected Output

After running the pipeline, you'll have:

```
steel_tariff_analysis/
├── raw/
│   ├── census_imports.csv
│   ├── bls_prices.csv
│   ├── fred_macro.csv
│   └── usitc_tariffs.csv
├── clean/
│   ├── census_clean.csv
│   ├── bls_clean.csv
│   ├── fred_clean.csv
│   ├── tariffs_clean.csv
│   ├── steel_panel.parquet    ← Main output!
│   └── steel_panel.csv         ← Sample
└── analysis/
    ├── summary_statistics.txt
    ├── event_study.png
    └── import_trends.png
```

## Loading the Panel in Python

```python
import pandas as pd

# Load the panel
df = pd.read_parquet('clean/steel_panel.parquet')

# Explore
print(df.head())
print(df.columns)
print(df.describe())

# Filter to treated products post-treatment
treated_post = df[(df['exposure_indicator'] == 1) & (df['post_treat'] == 1)]
print(f"Treated observations: {len(treated_post)}")
```

## Loading the Panel in R

```r
library(arrow)

# Load the panel
df <- read_parquet('clean/steel_panel.parquet')

# Explore
head(df)
summary(df)

# Run DiD regression
library(fixest)
model <- feols(log_import_volume ~ treated_post | country + hs6 + date,
               data = df)
summary(model)
```

## Common Use Cases

### 1. Basic DiD Analysis
```python
import statsmodels.formula.api as smf

df = pd.read_parquet('clean/steel_panel.parquet')
model = smf.ols('log_import_volume ~ treated_post + oil_price', data=df).fit()
print(model.summary())
```

### 2. Country-Specific Analysis
```python
df = pd.read_parquet('clean/steel_panel.parquet')

# Focus on China
china_df = df[df['country'] == 'China']

# Plot China's steel imports over time
import matplotlib.pyplot as plt
china_agg = china_df.groupby('date')['import_volume_mt'].sum()
plt.plot(china_agg.index, china_agg.values)
plt.axvline(pd.to_datetime('2018-03-01'), color='red', linestyle='--')
plt.title('China Steel Imports to U.S.')
plt.show()
```

### 3. Product-Specific Analysis
```python
df = pd.read_parquet('clean/steel_panel.parquet')

# Focus on specific HS code
hs_df = df[df['hs6'] == '720810']  # Flat-rolled steel

# Average import volume by period
print(hs_df.groupby('post_treat')['import_volume_mt'].mean())
```

## Troubleshooting

**Q: Pipeline fails during data collection**
- A: Use synthetic data: `python main.py --skip-collection` is not needed; synthetic data is generated automatically if API keys are missing

**Q: Out of memory error**
- A: Reduce date range in `config/config.py` (e.g., 2015-2020 instead of 2000-2025)

**Q: Panel is empty**
- A: Check that raw data was collected successfully in `raw/` directory

**Q: Analysis fails with missing columns**
- A: Ensure panel construction completed successfully; check `clean/steel_panel.parquet` exists

## Next Steps

1. **Explore the data**: Open `clean/steel_panel.csv` in Excel or pandas
2. **Run regressions**: Use the example script or write your own
3. **Customize**: Edit `config/config.py` to add HS codes, change dates, etc.
4. **Extend**: Add new data sources or analysis modules

## Getting Help

- Check `README.md` for detailed documentation
- Examine `analysis_example.py` for analysis patterns
- Review `config/config.py` for customization options
