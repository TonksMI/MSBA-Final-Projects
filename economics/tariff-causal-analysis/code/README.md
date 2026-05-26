# Steel Tariff Analysis Pipeline

A comprehensive data pipeline for analyzing the impact of Section 232 steel tariffs on U.S. imports, built with Python.

## Overview

This project implements a complete data pipeline following the specification for analyzing U.S. steel tariff policy (Section 232). The pipeline:

1. **Collects** data from multiple public sources (Census, BLS, FRED, USITC)
2. **Transforms** raw data into standardized formats
3. **Constructs** a panel dataset (country × HS code × month) from 2000–2025
4. **Enables** difference-in-differences and event study analyses

## Project Structure

```
steel_tariff_analysis/
├── config/
│   └── config.py              # Configuration and parameters
├── src/
│   ├── collectors/            # Data collection modules
│   │   ├── census_collector.py
│   │   ├── bls_collector.py
│   │   ├── fred_collector.py
│   │   └── usitc_collector.py
│   ├── transformers/          # Data transformation modules
│   │   ├── data_cleaner.py
│   │   └── panel_constructor.py
│   └── utils/
│       └── helpers.py         # Helper functions
├── raw/                       # Raw data (CSV dumps)
├── clean/                     # Cleaned data (Parquet)
├── analysis/                  # Analysis outputs
├── main.py                    # Main orchestration script
├── analysis_example.py        # Example analysis script
├── requirements.txt           # Python dependencies
├── .env.template             # API key template
└── README.md                 # This file
```

## Data Sources

| Source | Use Case | Data Type |
|--------|----------|-----------|
| **USA Trade Online (Census)** | Monthly imports by HS6 × country, 1989–present | Trade flows |
| **USITC DataWeb** | Tariff schedules, trade flows | Tariff rates |
| **BLS Import Price Index** | Country-of-origin steel prices | Price data |
| **BLS PPI** | Downstream price effects | Price data |
| **FRED** | Macro controls (oil, PMI, industrial production) | Economic indicators |

## Installation

### 1. Clone and Setup

```bash
cd steel_tariff_analysis
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy the environment template and add your API keys:

```bash
cp .env.template .env
```

Edit `.env` and fill in your API keys:

```bash
# Get API keys from:
# - Census: https://api.census.gov/data/key_signup.html
# - FRED: https://fred.stlouisfed.org/docs/api/api_key.html
# - BLS: https://www.bls.gov/developers/home.htm (optional)

CENSUS_API_KEY=your_key_here
FRED_API_KEY=your_key_here
BLS_API_KEY=your_key_here
```

## Usage

### Run Full Pipeline

Run all steps (collection, cleaning, panel construction):

```bash
python main.py
```

### Run Individual Steps

```bash
# Data collection only
python main.py --collection-only

# Data cleaning only (requires raw data)
python main.py --cleaning-only

# Panel construction only (requires clean data)
python main.py --panel-only

# Skip collection (use existing raw data)
python main.py --skip-collection
```

### Run Example Analysis

After the pipeline completes, run example analyses:

```bash
python analysis_example.py
```

This generates:
- Descriptive statistics
- Difference-in-differences estimates
- Event study plots
- Import trend visualizations

## Panel Structure

The final panel has structure: **(country × HS code × month), 2000–2025**

### Key Variables

**Identifiers:**
- `date`: Month (YYYY-MM-DD)
- `country`: Country name (standardized)
- `hs6`: 6-digit HS code

**Treatment Variables:**
- `exposure_indicator`: 1 if Section 232-affected steel product, 0 otherwise
- `post_treat`: 1 if after March 2018, 0 otherwise
- `treated_post`: Interaction term (exposure × post)

**Outcome Variables:**
- `import_volume_mt`: Import volume (metric tons)
- `import_value_usd`: Import value (USD)
- `unit_value`: Price per metric ton
- `import_volume_change`: Year-over-year % change
- `country_market_share`: Country's share of HS6 imports

**Control Variables:**
- `tariff_rate`: Effective tariff rate
- `import_price_index`: BLS import price index
- `ppi_steel`: Producer price index for steel
- `oil_price`: WTI crude oil price (from FRED)
- `industrial_production`: Industrial production index

**Derived Variables:**
- `log_import_volume`: Log transformation of volume
- `log_import_value`: Log transformation of value
- `log_unit_value`: Log transformation of unit value
- Lagged variables: `import_volume_lag{1,3,6,12}`, `tariff_rate_lag{1,3,6,12}`

## Data Transformations

The pipeline performs the following transformations:

### 1. HS Code Standardization
- Converts all HS codes to 6-digit level
- Maps codes to Section 232-affected vs. unaffected sets

### 2. Unit Conversion
- Converts all import quantities to metric tons
- Handles various input units (kg, lbs, short tons)

### 3. Country Standardization
- Normalizes country names across data sources
- Maps variants (e.g., "Korea, South" → "South Korea")

### 4. Tariff Merge
- Merges tariff rate schedules by date × HS6
- Accounts for country-specific exemptions (Canada, Mexico, etc.)

### 5. Temporal Aggregation
- Aggregates all data to monthly frequency
- Forward-fills missing values for price indexes

### 6. Derived Calculations
- Import volume changes (YoY)
- Market shares
- Price differentials
- Log transformations for regression

## Analysis Examples

### 1. Difference-in-Differences

Basic DiD specification:

```python
log_import_volume = α + β1*Treated + β2*Post + β3*(Treated×Post) + ε
```

With controls:

```python
log_import_volume = α + β1*(Treated×Post) + β2*Macro_Controls + γ_i + δ_t + ε
```

### 2. Event Study

Estimate treatment effects over time:

```python
log_import_volume = α + Σ β_τ*(Treated × Event_Time_τ) + γ_i + δ_t + ε
```

Where `τ` ranges from -24 to +24 months around March 2018.

### 3. Substitution Analysis

Examine source country substitution:

```python
country_market_share = α + β*(Treated×Post) + γ_c + δ_t + ε
```

## Section 232 Steel Tariffs

**Implementation:** March 2018
**Rate:** 25% ad valorem tariff on steel imports

**Key Features:**
- Applied to most steel products (identified by HS codes)
- Country exemptions: Canada, Mexico (under USMCA), Australia
- Quota arrangements: South Korea, Argentina, Brazil
- Aim: Protect national security via domestic steel production

## Customization

### Adding HS Codes

Edit `config/config.py`:

```python
STEEL_HS6_CODES = [
    "720810",  # Your codes here
    # ...
]
```

### Adjusting Date Range

Edit `config/config.py`:

```python
START_YEAR = 2000
END_YEAR = 2025
```

### Adding Data Sources

1. Create collector in `src/collectors/`
2. Add cleaning logic in `src/transformers/data_cleaner.py`
3. Update panel merge in `src/transformers/panel_constructor.py`
4. Update `main.py` orchestration

## Output Files

### Raw Data (`raw/`)
- `census_imports.csv`: Raw Census import data
- `bls_prices.csv`: Raw BLS price indexes
- `fred_macro.csv`: Raw FRED macro indicators
- `usitc_tariffs.csv`: Tariff rate schedules
- `country_exemptions.csv`: Country-specific exemptions
- `hs_descriptions.csv`: HS code descriptions

### Clean Data (`clean/`)
- `census_clean.csv`: Cleaned import data
- `bls_clean.csv`: Cleaned price data
- `fred_clean.csv`: Cleaned macro data
- `tariffs_clean.csv`: Cleaned tariff data
- `steel_panel.parquet`: **Final panel dataset** (Parquet format)
- `steel_panel.csv`: Sample of panel (first 10,000 rows)

### Analysis (`analysis/`)
- `summary_statistics.txt`: Descriptive statistics
- `event_study.png`: Event study plot
- `import_trends.png`: Import trend visualizations

## Important Notes

### API Limitations

1. **Census API**: Some endpoints may require manual data download from [USA Trade Online](https://usatrade.census.gov/)
2. **USITC DataWeb**: Typically requires manual download from [DataWeb](https://dataweb.usitc.gov/)
3. **BLS API**: Rate limits apply (25 queries/day without key, 500/day with key)

### Data Quality

- Price indexes may have gaps (forward-filled in cleaning)
- Some country-product-month combinations may have zero imports
- Tariff exemptions require country-level tariff data (simplified in current implementation)

### Performance

- Full pipeline runtime: ~30-60 minutes (depending on API availability)
- Panel size: Typically 1-5M rows depending on date range and HS codes
- Parquet format used for efficient storage and loading

## Troubleshooting

### Missing API Keys

If you see warnings about missing API keys, the pipeline will use synthetic/placeholder data for testing. For production use, obtain real API keys.

### Import Errors

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

### Data Collection Failures

If data collection fails:
1. Check API keys are valid
2. Verify network connectivity
3. Check API rate limits
4. Run with `--skip-collection` and use manual downloads

### Memory Issues

For large panels:
1. Reduce date range in `config/config.py`
2. Reduce number of HS codes
3. Increase system RAM or use chunked processing

## Contributing

To extend this pipeline:

1. Follow the modular structure (collectors, transformers, utils)
2. Add tests for new functionality
3. Update documentation
4. Ensure compatibility with panel structure

## References

- [Section 232 Steel Tariffs (USITC)](https://www.usitc.gov/steel)
- [USA Trade Online](https://usatrade.census.gov/)
- [BLS Import/Export Price Indexes](https://www.bls.gov/mxp/)
- [FRED Economic Data](https://fred.stlouisfed.org/)

## License

This project is for educational and research purposes.

## Contact

For questions or issues, please open an issue in the project repository.
