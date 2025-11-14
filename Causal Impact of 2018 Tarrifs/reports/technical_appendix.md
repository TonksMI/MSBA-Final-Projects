# Technical Appendix
## Causal Impact of Section 232 Tariffs on Steel Imports

**Econometric Methodology and Detailed Results**

---

## Table of Contents

1. [Data Description](#1-data-description)
2. [Difference-in-Differences Methodology](#2-difference-in-differences-methodology)
3. [Synthetic Control Methodology](#3-synthetic-control-methodology)
4. [Diagnostic Tests](#4-diagnostic-tests)
5. [Regression Tables](#5-regression-tables)
6. [Robustness Checks](#6-robustness-checks)
7. [Additional Analyses](#7-additional-analyses)
8. [References](#8-references)

---

## 1. Data Description

### 1.1 Data Sources

**Primary Data:**
- **USA Trade Online** (U.S. Census Bureau)
  - Monthly import data by HS code and country of origin
  - Coverage: January 1989 - December 2020
  - Variables: Import value ($), import quantity (kg), customs value

**Supplementary Data:**
- **USITC DataWeb:** Detailed tariff rates and trade flows
- **BLS Import Price Indices:** Price data by country of origin
- **AISI/Federal Reserve:** Domestic steel production data

### 1.2 Sample Construction

**Sample Period:** January 2010 - December 2020
- Pre-treatment: January 2010 - March 22, 2018 (99 months)
- Post-treatment: March 23, 2018 - December 2020 (33 months)

**HS Codes Included:**
```
7208: Flat-rolled products of iron/steel, hot-rolled (HRC)
7209: Flat-rolled products of iron/steel, cold-rolled (CRC)
7210: Flat-rolled products of iron/steel, plated/coated
7211: Flat-rolled products of iron/steel, further worked
7212: Flat-rolled products of iron/steel, clad/plated
```

**Treatment Groups:**

*Treated Countries (Subject to 25% Tariff):*
- China, South Korea, Japan, Germany, Taiwan, Turkey, Brazil, India, Russia, Vietnam, and others

*Control Countries (Initially Exempt):*
- Canada, Mexico (under NAFTA/USMCA)
- Note: Canada and Mexico lost exemptions in 2025

**Sample Restrictions:**
1. Dropped observations with missing or zero import values
2. Excluded re-exports and trans-shipments
3. Winsorized extreme outliers (top/bottom 1%)
4. Aggregated to monthly country-product level

### 1.3 Summary Statistics

**Table 1.1: Descriptive Statistics**

| Variable | Mean | Std. Dev. | Min | Max | N |
|----------|------|-----------|-----|-----|---|
| Import Value ($M) | [X.XX] | [X.XX] | [X.XX] | [X.XX] | [XXX,XXX] |
| Import Quantity (000 tons) | [X.XX] | [X.XX] | [X.XX] | [X.XX] | [XXX,XXX] |
| Log Import Value | [X.XX] | [X.XX] | [X.XX] | [X.XX] | [XXX,XXX] |
| Unit Price ($/ton) | [X.XX] | [X.XX] | [X.XX] | [X.XX] | [XXX,XXX] |
| Treated (=1) | [X.XX] | [X.XX] | 0 | 1 | [XXX,XXX] |
| Post (=1) | [X.XX] | [X.XX] | 0 | 1 | [XXX,XXX] |

**Table 1.2: Treatment Group Balance (Pre-Treatment Period)**

| Variable | Treated | Control | Difference | T-stat |
|----------|---------|---------|------------|--------|
| Import Value ($M) | [X.XX] | [X.XX] | [X.XX] | [X.XX] |
| Import Quantity | [X.XX] | [X.XX] | [X.XX] | [X.XX] |
| Log Import Value | [X.XX] | [X.XX] | [X.XX] | [X.XX] |
| Unit Price | [X.XX] | [X.XX] | [X.XX] | [X.XX] |

*Note: All variables measured in pre-treatment period (2010-2018Q1)*

---

## 2. Difference-in-Differences Methodology

### 2.1 Identification Strategy

The **difference-in-differences (DID)** estimator exploits the Section 232 tariff as a natural experiment, comparing treated countries (subject to tariff) to control countries (exempt) before and after implementation.

**Key Identifying Assumption:** Parallel trends - In the absence of treatment, treated and control groups would have followed parallel trends.

### 2.2 Baseline Specification

**Two-Way Fixed Effects Model:**

```
Y_ict = β₀ + β₁·(Treated_i × Post_t) + γ_ic + δ_t + ε_ict
```

Where:
- `Y_ict`: Outcome for country `i`, product `c`, at time `t` (log import value or quantity)
- `Treated_i`: Binary indicator for tariff-affected country
- `Post_t`: Binary indicator for post-tariff period (≥ March 2018)
- `γ_ic`: Country-product fixed effects (absorbs time-invariant heterogeneity)
- `δ_t`: Time (year-month) fixed effects (absorbs common time trends)
- `ε_ict`: Error term

**Coefficient of Interest:** `β₁` = Average treatment effect on the treated (ATT)

**Standard Errors:** Clustered at the country level to account for serial correlation and heteroskedasticity

### 2.3 Event-Study Specification

To examine dynamic treatment effects and test pre-trends:

```
Y_ict = α + Σ_{τ=-K}^{-2} β_τ·(Treated_i × 1[t=τ]) + Σ_{τ=0}^{L} β_τ·(Treated_i × 1[t=τ]) + γ_ic + δ_t + ε_ict
```

Where:
- `τ`: Months relative to treatment (τ = 0 is March 2018)
- `τ = -1` omitted as reference period
- `K`: Number of pre-treatment leads (typically 12)
- `L`: Number of post-treatment lags (typically 24)

**Tests:**
1. **Pre-trends:** Joint test that `β_τ = 0` for all `τ < 0`
2. **Anticipation:** Individual tests for `τ = -1, -2, -3`
3. **Dynamic effects:** Pattern of `β_τ` for `τ ≥ 0`

### 2.4 Alternative Specifications

**Specification 1: With Controls**
```
Y_ict = β₁·DID_ict + X'_ict·θ + γ_ic + δ_t + ε_ict
```

Controls (`X_ict`):
- Lagged domestic steel production
- Exchange rate (country currency per USD)
- Oil price (proxy for shipping costs)
- GDP growth rate

**Specification 2: Product-Specific Effects**
```
Y_ict = Σ_c β₁c·(DID_ict × 1[product=c]) + γ_ic + δ_t + ε_ict
```

**Specification 3: Continuous Treatment Intensity**
```
Y_ict = β₁·(TariffRate_ic × Post_t) + γ_ic + δ_t + ε_ict
```

Where `TariffRate_ic` varies by country-product (some countries faced different rates)

---

## 3. Synthetic Control Methodology

### 3.1 Overview

The **Synthetic Control Method (SCM)** constructs a weighted combination of control units (donor countries) that best approximates the treated unit's pre-treatment characteristics. The post-treatment gap between actual and synthetic represents the causal effect.

**Reference:** Abadie, Diamond, and Hainmueller (2010, JASA)

### 3.2 Setup

**For each product `c`:**

**Treated Unit:** Total imports to USA from tariff-affected countries

**Donor Pool:** Country-level imports from tariff-exempt or less-affected countries
- Canada, Mexico, [other exempt countries]
- Countries with minimal tariff exposure

**Pre-Treatment Period:** January 2010 - December 2017 (96 months)

**Post-Treatment Period:** January 2018 - December 2020 (36 months)

### 3.3 Optimization Problem

Find weights `W = (w₁, ..., w_J)` that minimize:

```
||X₁ - X₀W||_V = √[(X₁ - X₀W)'V(X₁ - X₀W)]
```

Subject to:
```
w_j ≥ 0  ∀j
Σ_j w_j = 1
```

Where:
- `X₁`: Vector of pre-treatment characteristics for treated unit
- `X₀`: Matrix of pre-treatment characteristics for donor pool
- `V`: Diagonal matrix of predictor weights (chosen to minimize RMSE)

**Predictors Used:**
1. Pre-treatment import values (monthly averages by year)
2. Pre-treatment import quantities
3. Pre-treatment unit prices
4. Lagged 12-month moving averages

### 3.4 Estimation Procedure

**Algorithm (Nested Optimization):**

1. **Outer loop:** Choose predictor weights `V`
   - Grid search or optimization over `V`
   - For each `V`, solve inner loop

2. **Inner loop:** Find donor weights `W` given `V`
   - Quadratic programming with simplex constraints
   - Use SLSQP or similar constrained optimizer

3. **Selection:** Choose `V` that minimizes pre-treatment RMSE:
   ```
   RMSE_pre = √[Σ_t=1^T₀ (Y₁t - Σ_j w_j*Y_jt)² / T₀]
   ```

**Implementation:** Using `scipy.optimize.minimize` with SLSQP method

### 3.5 Inference

**Standard SCM does not provide conventional standard errors.** We use:

1. **Placebo Tests:** Apply SCM to each donor country as if it were treated
   - Compute gap distribution under null of no effect
   - P-value = Fraction of placebos with gap ≥ actual gap

2. **In-time Placebo Tests:** Assign fake treatment dates in pre-period
   - Should find no effects if method is valid

3. **Leave-One-Out Sensitivity:**
   - Re-estimate excluding each donor one at a time
   - Check robustness of weights and gap estimates

---

## 4. Diagnostic Tests

### 4.1 Parallel Trends Test

**Test Statistic:** Coefficient on `Treated × Time_trend` in pre-period

**Table 4.1: Parallel Trends Test Results**

| Outcome Variable | Coefficient | Std. Error | T-stat | P-value | Conclusion |
|------------------|-------------|------------|--------|---------|------------|
| Log Import Value | [X.XXXX] | [X.XXXX] | [X.XX] | [X.XXX] | [Pass/Fail] |
| Log Import Quantity | [X.XXXX] | [X.XXXX] | [X.XX] | [X.XXX] | [Pass/Fail] |
| Log Unit Price | [X.XXXX] | [X.XXXX] | [X.XX] | [X.XXX] | [Pass/Fail] |

**Interpretation:**
- If p-value > 0.05: Fail to reject parallel trends (✓ assumption satisfied)
- If p-value < 0.05: Reject parallel trends (⚠ assumption violated)

**Result:** [Describe findings]

### 4.2 Placebo Tests (DID)

**Fake Treatment Dates in Pre-Period:**

Test whether we detect "effects" at fake treatment dates (2014, 2015, 2016, 2017). Under parallel trends, coefficients should be ~0.

**Table 4.2: Placebo Test Results**

| Fake Treatment Date | DID Coefficient | Std. Error | P-value | Significant? |
|---------------------|-----------------|------------|---------|--------------|
| 2014-01-01 | [X.XXX] | [X.XXX] | [X.XXX] | [Yes/No] |
| 2015-01-01 | [X.XXX] | [X.XXX] | [X.XXX] | [Yes/No] |
| 2016-01-01 | [X.XXX] | [X.XXX] | [X.XXX] | [Yes/No] |
| 2017-01-01 | [X.XXX] | [X.XXX] | [X.XXX] | [Yes/No] |

**Expected:** 0-1 significant placebos (5% false positive rate)
**Observed:** [X] / 4 significant

### 4.3 Pre-Treatment Fit (Synthetic Control)

**Table 4.3: Synthetic Control Pre-Treatment RMSE by Product**

| Product | Pre-Treatment RMSE | Mean Outcome | RMSE/Mean | Donor Countries (Top 3) |
|---------|-------------------|--------------|-----------|------------------------|
| HRC | [XXX.XX] | [XXX.XX] | [X.XX]% | [Country1 (wt), Country2 (wt), Country3 (wt)] |
| CRC | [XXX.XX] | [XXX.XX] | [X.XX]% | [...] |
| Plate | [XXX.XX] | [XXX.XX] | [X.XX]% | [...] |

**Benchmark:** RMSE/Mean < 10% indicates good fit

### 4.4 Sensitivity to Donor Pool

**Leave-One-Out Analysis:**

For each donor with weight > 0.05, re-estimate excluding that donor and compare results.

**Table 4.4: Leave-One-Out Sensitivity (HRC Example)**

| Excluded Donor | Original Weight | New RMSE | Change in ATT | % Change |
|----------------|----------------|----------|---------------|----------|
| [Country 1] | [X.XXX] | [XXX.X] | [+/- X.XX] | [+/- X]% |
| [Country 2] | [X.XXX] | [XXX.X] | [+/- X.XX] | [+/- X]% |
| [Country 3] | [X.XXX] | [XXX.X] | [+/- X.XX] | [+/- X]% |

**Interpretation:** ATT changes by less than [XX]% across all LOO specifications → Results are robust

---

## 5. Regression Tables

### 5.1 Main DID Results

**Table 5.1: Baseline Difference-in-Differences Estimates**

```
Dependent Variable: Log Import Value
```

|  | (1) | (2) | (3) | (4) |
|--|-----|-----|-----|-----|
|  | Baseline | + Controls | By Product | Continuous Treatment |
| **DID** | [X.XXX]*** | [X.XXX]*** | - | - |
|  | ([X.XXX]) | ([X.XXX]) | - | - |
| **DID × HRC** | - | - | [X.XXX]*** | - |
|  | - | - | ([X.XXX]) | - |
| **DID × CRC** | - | - | [X.XXX]*** | - |
|  | - | - | ([X.XXX]) | - |
| **DID × Plate** | - | - | [X.XXX]*** | - |
|  | - | - | ([X.XXX]) | - |
| **Tariff Rate × Post** | - | - | - | [X.XXX]*** |
|  | - | - | - | ([X.XXX]) |
| **Exchange Rate** | - | [X.XXX] | [X.XXX] | [X.XXX] |
|  | - | ([X.XXX]) | ([X.XXX]) | ([X.XXX]) |
| **Country-Product FE** | Yes | Yes | Yes | Yes |
| **Time FE** | Yes | Yes | Yes | Yes |
| **Clustered SE** | Country | Country | Country | Country |
| **R-squared** | [X.XXX] | [X.XXX] | [X.XXX] | [X.XXX] |
| **Observations** | [XXX,XXX] | [XXX,XXX] | [XXX,XXX] | [XXX,XXX] |
| **Clusters** | [XX] | [XX] | [XX] | [XX] |

*Notes: Robust standard errors clustered by country in parentheses. \*, \*\*, \*\*\* denote significance at 10%, 5%, 1% levels.*

**Interpretation:**
- Column (1): Baseline specification shows [X]% reduction in imports from treated countries
- Column (2): Adding controls [does not materially change/changes] the estimate
- Column (3): Heterogeneity across products - [Product X] most affected
- Column (4): Continuous treatment intensity confirms robustness

### 5.2 Event-Study Results

**Table 5.2: Event-Study Coefficients**

*See Figure A1 for visual representation*

| Rel. Month (τ) | Coefficient | Std. Error | 95% CI Lower | 95% CI Upper |
|----------------|-------------|------------|--------------|--------------|
| -12 | [X.XXX] | [X.XXX] | [X.XXX] | [X.XXX] |
| -11 | [X.XXX] | [X.XXX] | [X.XXX] | [X.XXX] |
| ... | ... | ... | ... | ... |
| -2 | [X.XXX] | [X.XXX] | [X.XXX] | [X.XXX] |
| -1 | 0.000 | - | - | - |
| 0 | [X.XXX]*** | [X.XXX] | [X.XXX] | [X.XXX] |
| 1 | [X.XXX]*** | [X.XXX] | [X.XXX] | [X.XXX] |
| ... | ... | ... | ... | ... |
| 24 | [X.XXX]*** | [X.XXX] | [X.XXX] | [X.XXX] |

**Pre-Trend Test:**
- Joint F-test for `τ ∈ {-12, ..., -2}`: F = [X.XX], p = [X.XXX]
- Conclusion: [Fail to reject/Reject] null of no pre-trends

**Dynamic Effects:**
- Immediate effect (τ=0): [X.XXX]
- Short-run (τ=0-6): [X.XXX]
- Medium-run (τ=7-12): [X.XXX]
- Long-run (τ=13-24): [X.XXX]

### 5.3 Synthetic Control Estimates

**Table 5.3: Synthetic Control Treatment Effects by Product**

| Product | Pre-Period RMSE | Post-Period Mean Gap | Mean Gap (%) | Cumulative Gap | P-value (Placebo) |
|---------|----------------|---------------------|--------------|----------------|-------------------|
| HRC | [XXX.X] | [X,XXX] | [XX.X]% | [XX,XXX] | [X.XXX] |
| CRC | [XXX.X] | [X,XXX] | [XX.X]% | [XX,XXX] | [X.XXX] |
| Plate | [XXX.X] | [X,XXX] | [XX.X]% | [XX,XXX] | [X.XXX] |
| Other | [XXX.X] | [X,XXX] | [XX.X]% | [XX,XXX] | [X.XXX] |

**Table 5.4: Donor Weights (HRC Example)**

| Donor Country | Weight | Contribution |
|---------------|--------|--------------|
| Canada | [X.XXX] | [XX.X]% |
| Mexico | [X.XXX] | [XX.X]% |
| [Country 3] | [X.XXX] | [XX.X]% |
| [Country 4] | [X.XXX] | [XX.X]% |
| [Country 5] | [X.XXX] | [XX.X]% |
| Other (< 0.05) | [X.XXX] | [XX.X]% |
| **Total** | **1.000** | **100.0%** |

---

## 6. Robustness Checks

### 6.1 Alternative Treatment Definitions

**Table 6.1: Robustness to Treatment Group Definition**

| Treatment Definition | DID Coefficient | Std. Error | N |
|---------------------|-----------------|------------|---|
| Baseline (25% tariff countries) | [X.XXX]*** | ([X.XXX]) | [XXX,XXX] |
| Exclude countries w/ exemptions | [X.XXX]*** | ([X.XXX]) | [XXX,XXX] |
| Only major exporters (>1% share) | [X.XXX]*** | ([X.XXX]) | [XXX,XXX] |
| Continuous (tariff rate) | [X.XXX]*** | ([X.XXX]) | [XXX,XXX] |

### 6.2 Alternative Time Windows

**Table 6.2: Robustness to Sample Period**

| Sample Period | DID Coefficient | Std. Error | N |
|---------------|-----------------|------------|---|
| Baseline (2010-2020) | [X.XXX]*** | ([X.XXX]) | [XXX,XXX] |
| 2012-2020 (shorter pre) | [X.XXX]*** | ([X.XXX]) | [XXX,XXX] |
| 2010-2019 (shorter post) | [X.XXX]*** | ([X.XXX]) | [XXX,XXX] |
| 2015-2020 (balanced) | [X.XXX]*** | ([X.XXX]) | [XXX,XXX] |

### 6.3 Alternative Outcome Measures

**Table 6.3: Results for Different Outcomes**

| Outcome Variable | DID Coefficient | Std. Error | Interpretation |
|------------------|-----------------|------------|----------------|
| Log Import Value | [X.XXX]*** | ([X.XXX]) | [XX]% reduction |
| Log Import Quantity | [X.XXX]*** | ([X.XXX]) | [XX]% reduction |
| Log Unit Price | [X.XXX]*** | ([X.XXX]) | [XX]% increase |
| Import Share (%) | [X.XXX]*** | ([X.XXX]) | [X]ppt decline |

**Price-Volume Decomposition:**
```
Δlog(Value) = Δlog(Price) + Δlog(Quantity)
[X.XXX]     = [X.XXX]     + [X.XXX]
```

### 6.4 Clustering and Inference

**Table 6.4: Robustness to Different Standard Error Clustering**

| Clustering Level | DID Coefficient | Std. Error | T-stat |
|------------------|-----------------|------------|--------|
| Country | [X.XXX] | [X.XXX] | [X.XX]*** |
| Product | [X.XXX] | [X.XXX] | [X.XX]*** |
| Country-Product | [X.XXX] | [X.XXX] | [X.XX]*** |
| Two-way (Country & Time) | [X.XXX] | ([X.XXX], [X.XXX]) | [X.XX]*** |

*Note: Two-way clustering shows lower and upper bounds following Cameron et al. (2011)*

---

## 7. Additional Analyses

### 7.1 Price Passthrough

**Specification:**
```
Δlog(Price_ic) = α + β·Δlog(1 + TariffRate_ic) + γ_i + ε_ic
```

**Table 7.1: Tariff Passthrough to Import Prices**

| | (1) | (2) |
|--|-----|-----|
|  | All Products | HRC Only |
| **Δlog(1 + Tariff)** | [X.XXX]*** | [X.XXX]*** |
|  | ([X.XXX]) | ([X.XXX]) |
| **Observations** | [XXX] | [XXX] |
| **R-squared** | [X.XXX] | [X.XXX] |

**Interpretation:** A 25% tariff (log(1.25) = 0.223) increases prices by `[X.XXX] × 0.223 = [X.XX]`, implying **[XX]% passthrough**.

### 7.2 Substitution Elasticities

Estimate cross-price elasticities between tariff-affected and exempt countries.

**Table 7.2: Substitution Matrix (Log Import Quantity)**

| | Treated Price (+10%) | Control Price (+10%) |
|--|---------------------|---------------------|
| **Treated Quantity** | [X.XX] (own-price) | [X.XX] (cross-price) |
| **Control Quantity** | [X.XX] (cross-price) | [X.XX] (own-price) |

**Interpretation:** [XX]% increase in treated country prices → [X]% increase in control country imports (substitution effect)

### 7.3 Heterogeneity by Country Size

**Table 7.3: Treatment Effects by Export Size**

| Country Group | DID Coefficient | Std. Error | N |
|---------------|-----------------|------------|---|
| Large exporters (>$1B/year) | [X.XXX]*** | ([X.XXX]) | [XXX] |
| Medium exporters ($100M-$1B) | [X.XXX]*** | ([X.XXX]) | [XXX] |
| Small exporters (<$100M) | [X.XXX] | ([X.XXX]) | [XXX] |

---

## 8. References

### Econometric Methods

1. **Abadie, A., Diamond, A., & Hainmueller, J. (2010).** "Synthetic Control Methods for Comparative Case Studies: Estimating the Effect of California's Tobacco Control Program." *Journal of the American Statistical Association*, 105(490), 493-505.

2. **Abadie, A. (2021).** "Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects." *Journal of Economic Literature*, 59(2), 391-425.

3. **Athey, S., & Imbens, G. W. (2022).** "Design-based Analysis in Difference-in-Differences Settings with Staggered Adoption." *Journal of Econometrics*, 226(1), 62-79.

4. **Bertrand, M., Duflo, E., & Mullainathan, S. (2004).** "How Much Should We Trust Differences-in-Differences Estimates?" *Quarterly Journal of Economics*, 119(1), 249-275.

5. **Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2011).** "Robust Inference with Multiway Clustering." *Journal of Business & Economic Statistics*, 29(2), 238-249.

6. **Cunningham, S. (2021).** *Causal Inference: The Mixtape*. Yale University Press.

### Trade Policy and Tariffs

7. **Amiti, M., Redding, S. J., & Weinstein, D. E. (2019).** "The Impact of the 2018 Tariffs on Prices and Welfare." *Journal of Economic Perspectives*, 33(4), 187-210.

8. **Fajgelbaum, P. D., Goldberg, P. K., Kennedy, P. J., & Khandelwal, A. K. (2020).** "The Return to Protectionism." *Quarterly Journal of Economics*, 135(1), 1-55.

9. **Flaaen, A., & Pierce, J. (2019).** "Disentangling the Effects of the 2018-2019 Tariffs on a Globally Connected U.S. Manufacturing Sector." *Federal Reserve Board Finance and Economics Discussion Series* 2019-086.

### Data Sources

10. **U.S. Census Bureau.** USA Trade Online. https://usatrade.census.gov/

11. **U.S. International Trade Commission.** USITC DataWeb. https://dataweb.usitc.gov/

12. **Bureau of Labor Statistics.** Import/Export Price Indexes. https://www.bls.gov/mxp/

---

## Appendix A: Additional Figures

### Figure A1: Event-Study Plot
*[See event_study_main.png]*

### Figure A2: Parallel Trends Visual Test
*[See parallel_trends_visual.png]*

### Figure A3: Synthetic Control: HRC
*[See HRC_synth_vs_actual.png]*

### Figure A4: Market Share Shifts
*[See market_share_shifts.png]*

### Figure A5: Country Import Trajectories
*[See country_trajectories.png]*

---

## Appendix B: Code Availability

All analysis code is available at:
- **Repository:** [GitHub link]
- **Models:** `models/did_model.py`, `models/synthetic_control.py`
- **Analysis:** `analysis/parallel_trends.ipynb`, `analysis/event_study.ipynb`
- **Visualizations:** `viz/import_trends.py`, `viz/synthetic_vs_actual.py`

**Reproducibility:** All results can be reproduced by running:
```bash
python models/did_model.py
python models/synthetic_control.py
jupyter notebook analysis/event_study.ipynb
```

---

*This technical appendix provides full methodological details and results for the causal analysis of Section 232 tariff impacts on steel imports. For executive summary and strategic recommendations, see `executive_summary.md`.*
