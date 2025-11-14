# Tariff Causal Analysis: Methodology & Testing Logic

## Table of Contents
1. [Overview](#overview)
2. [Causal Inference Framework](#causal-inference-framework)
3. [Method 1: Difference-in-Differences (DID)](#method-1-difference-in-differences-did)
4. [Method 2: Synthetic Control Method](#method-2-synthetic-control-method)
5. [Validity Testing](#validity-testing)
6. [Robustness Checks](#robustness-checks)
7. [Interpretation Guidelines](#interpretation-guidelines)
8. [Limitations & Assumptions](#limitations--assumptions)

---

## Overview

This project estimates the **causal impact** of Section 232 steel tariffs (implemented March 2018) on:
- Import volumes from affected countries
- Import prices
- Domestic steel production
- Domestic steel prices
- Source country substitution patterns

We employ two parallel causal inference strategies:
1. **Difference-in-Differences (DID)** - Comparing treated vs control groups before/after treatment
2. **Synthetic Control Method** - Creating counterfactual using weighted donor pool

---

## Causal Inference Framework

### The Fundamental Problem

We want to answer: **"What would have happened to imports/prices if the tariff had NOT been implemented?"**

This is the **counterfactual** - we can never directly observe it because the tariff DID happen. Causal inference methods construct credible counterfactuals using:
- Control groups (untreated units)
- Pre-treatment trends
- Statistical assumptions

### Notation

- **Y(1)** = Outcome with treatment (observed for treated units)
- **Y(0)** = Outcome without treatment (counterfactual for treated units)
- **τ = Y(1) - Y(0)** = Causal effect (what we want to estimate)

**Challenge**: We observe either Y(1) OR Y(0) for each unit, never both!

**Solution**: Use control groups to estimate Y(0) for treated units.

---

## Method 1: Difference-in-Differences (DID)

### Core Logic

DID exploits **natural experiments** where:
1. Some units receive treatment (tariff-affected countries)
2. Some units do NOT receive treatment (exempt countries: Canada, Mexico)
3. Treatment timing is exogenous (not caused by the outcome)

### The DID Estimator

**Model**:
```
Y_c,t = α + β(Treated_c × Post_t) + γ_c + δ_t + ε_c,t
```

Where:
- **Y_c,t** = Outcome for country c at time t
- **Treated_c** = 1 if country is subject to tariff, 0 otherwise
- **Post_t** = 1 if period is after tariff implementation, 0 otherwise
- **β** = **CAUSAL EFFECT** (our parameter of interest!)
- **γ_c** = Country fixed effects (control for time-invariant differences)
- **δ_t** = Time fixed effects (control for common shocks)

### Why This Works

**Intuition**:
- Control group tells us what would have happened to treated group in absence of treatment
- We "difference out" confounding factors twice:
  1. First difference: Before vs After (removes time-invariant country factors)
  2. Second difference: Treated vs Control (removes common time trends)

**Visual Example**:
```
Treated Group:   |---trend--▲---JUMP UP---|  (pre-treatment → post-treatment)
Control Group:   |---trend--▲-------------|  (parallel trend continues)
                            ↑
                       Treatment

DID Effect = (Treated_post - Treated_pre) - (Control_post - Control_pre)
```

### Two-Way Fixed Effects (TWFE)

Our implementation uses **two-way fixed effects**:
- **Entity (Country) Fixed Effects**: Control for time-invariant country characteristics
  - Example: Germany always imports less than China (geography, industrial structure)
- **Time Fixed Effects**: Control for shocks affecting all countries
  - Example: Global recession affects all countries equally

This is more robust than simple 2x2 DID because it:
- Handles multiple time periods
- Controls for time-varying common shocks
- Allows flexible functional forms

### Clustered Standard Errors

We cluster standard errors at the **country level** because:
- Observations for the same country are not independent
- Errors may be correlated within countries over time
- Prevents underestimating standard errors (Type I error)

**Implementation**:
```python
model = smf.ols(formula, data=data).fit(
    cov_type='cluster',
    cov_kwds={'groups': data['country']}
)
```

---

## Method 2: Synthetic Control Method

### Core Logic

Instead of using actual control countries, we **construct an optimal synthetic control** by:
1. Taking a weighted combination of untreated countries
2. Optimizing weights to best match pre-treatment characteristics
3. Extending this synthetic unit to post-treatment period

**Key Advantage**: The synthetic control matches the treated unit MORE closely than any single control country.

### Mathematical Framework

**Objective**: Find weights **W = (w₁, w₂, ..., wⱼ)** that minimize pre-treatment fit:

```
min Σ(Y_treated,t - Σ wⱼ × Y_donor_j,t)²  for all pre-treatment periods t
  W

Subject to:
  - Σ wⱼ = 1  (weights sum to 1)
  - wⱼ ≥ 0    (non-negative weights)
```

This creates a **synthetic China** (or other treated unit) that:
- Has the same pre-treatment trend as actual China
- Is built from untreated countries
- Represents "what would have happened without tariff"

### Why This Works

**Intuition**:
- If synthetic control matches treated unit perfectly before treatment
- Any divergence AFTER treatment is the causal effect
- More flexible than DID (doesn't assume parallel trends)

**Visual Example**:
```
Actual China:     |---match---|---DIVERGES DOWN---|
Synthetic China:  |---match---|---continues trend---|
                              ↑
                         Treatment

Effect = Gap between actual and synthetic in post-period
```

### Implementation Steps

1. **Pre-Treatment Period**: Fit weights to minimize RMSPE
   - RMSPE = Root Mean Square Prediction Error
   - Measures how well synthetic matches treated unit

2. **Post-Treatment Period**: Extend synthetic unit forward
   - Apply same weights to donor pool outcomes
   - Gap = Causal effect

3. **Weight Interpretation**:
   - Large weight → That donor is similar to treated unit
   - Zero weight → That donor is not informative

**Code Example**:
```python
sc = SyntheticControl(data, treated_unit='China', ...)
weights = sc.fit()  # Optimize weights
effects = sc.get_treatment_effect()  # Calculate gap
```

---

## Validity Testing

Causal inference requires **strong assumptions**. We must test whether these hold!

### 1. Parallel Trends Test (DID)

**Assumption**: In the absence of treatment, treated and control groups would have followed parallel trends.

**Test**: Regress outcome on time trend, separately for treated vs control, using PRE-TREATMENT data only:

```
Y_c,t = α + β₁(time_trend) + β₂(Treated_c) + β₃(time_trend × Treated_c) + ε

H₀: β₃ = 0  (parallel trends)
H₁: β₃ ≠ 0  (differential trends - VIOLATION)
```

**Interpretation**:
- If p > 0.05: Parallel trends assumption is **VALID** ✓
- If p < 0.05: Parallel trends assumption is **VIOLATED** ✗
  - Treated and control had different trends even before treatment
  - DID estimate may be biased

**Why It Matters**: If groups had different trends before treatment, the control group is not a good counterfactual!

### 2. Event Study (Dynamic DID)

**Purpose**: Estimate treatment effects for EACH time period relative to treatment.

**Model**:
```
Y_c,t = α + Σ βₖ(Treated_c × Period_t=k) + γ_c + δ_t + ε

where k ranges from -6 (6 periods before) to +12 (12 periods after)
```

**What We Learn**:

1. **Pre-Treatment Effects (k < 0)**:
   - Should be ≈ 0 and statistically insignificant
   - If significant → Parallel trends violated
   - Tests the identifying assumption visually

2. **Post-Treatment Effects (k ≥ 0)**:
   - Shows dynamic evolution of treatment effect
   - Immediate vs gradual effects
   - Persistence or decay over time

3. **Anticipation Effects**:
   - If effects show up before official treatment → Anticipation!
   - Example: Firms might import early to avoid tariff

**Visual Interpretation**:
```
      Coefficient
         ↑
         |
      0  |--o--o--o---●●●●●●●  (pre: flat → post: negative jump)
         |           ↑
    -100 |      Treatment
         |
         └─────────────────→ Time Relative to Treatment
           -6  -3  0  +3  +6  +9  +12
```

Good event study:
- Pre-treatment coefficients ≈ 0
- Clear jump at treatment
- Post-treatment effects are significant

### 3. Placebo Tests

Placebo tests apply treatment where it **shouldn't have an effect** to check for spurious results.

#### A. Time Placebo (Fake Treatment Date)

**Test**: Apply fake treatment date in PRE-TREATMENT period
- Example: Pretend tariff happened in 2017 instead of 2018

**Logic**:
- If we find a "treatment effect" when there was no actual treatment → PROBLEM!
- Suggests our method picks up spurious effects

**Expected Result**: No significant effect (p > 0.05)

**Code**:
```python
placebo = did.placebo_test_time('2017-03-01')
# Should find: coefficient ≈ 0, p-value > 0.05
```

#### B. Product Placebo (Untreated Product)

**Test**: Apply same analysis to product that was NOT subject to tariff
- Example: Apply to aluminum when analyzing steel-specific tariffs

**Logic**:
- Untreated products should show NO effect
- If they do → Method is picking up confounding factors

**Expected Result**: No significant effect

#### C. Spatial Placebo (Synthetic Control)

**Test**: Apply synthetic control to UNTREATED countries
- Create "placebo gaps" for each control country
- Compare actual treatment effect to distribution of placebo effects

**Logic**:
- If treated unit's effect is not unusual compared to placebos → Not causal!
- Treatment effect should be in tail of placebo distribution

**Interpretation**:
```
p-value = (# placebos with |effect| ≥ |treated effect|) / (# placebos + 1)

If p < 0.05 → Treatment effect is statistically unusual
If p > 0.05 → Could be random noise
```

### 4. Pre-Treatment Fit (Synthetic Control)

**Metric**: Root Mean Square Prediction Error (RMSPE)

```
RMSPE = √(1/T × Σ(Y_treated,t - Y_synthetic,t)²)  for pre-treatment t
```

**Guidelines**:
- **RMSPE < 10% of mean outcome**: Excellent fit
- **RMSPE < 20% of mean outcome**: Good fit
- **RMSPE > 20% of mean outcome**: Poor fit → Results may be unreliable

**Why It Matters**:
- Poor pre-treatment fit → Synthetic control is not good counterfactual
- Cannot trust post-treatment divergence as causal effect

---

## Robustness Checks

Even if main tests pass, we should check sensitivity to alternative specifications:

### 1. Alternative Control Groups

**Test**: Re-run analysis with different sets of control countries
- Example: Include/exclude Canada, use only European controls, etc.

**Expected**: Results should be qualitatively similar

### 2. Alternative Lag Structures

**Test**: Try different time aggregations
- Monthly vs quarterly
- Different treatment windows

**Expected**: Magnitude may change, but sign and significance should be consistent

### 3. Different Outcome Measures

**Test**: Use alternative measures of same concept
- Volume: tons vs value
- Prices: unit values vs price indices

**Expected**: All measures should show consistent direction

### 4. Bandwidth Sensitivity (Synthetic Control)

**Test**: Vary the pre-treatment period length
- Shorter window (1 year) vs longer window (3 years)

**Expected**: Weights and effects should be similar

---

## Interpretation Guidelines

### Statistical Significance

**p-value < 0.01**: Highly significant (***) - Strong evidence of effect
**p-value < 0.05**: Significant (**) - Conventional threshold
**p-value < 0.10**: Marginally significant (*) - Weak evidence
**p-value ≥ 0.10**: Not significant (ns) - Cannot reject null hypothesis

### Effect Sizes

**Coefficient**: Raw effect in outcome units
- Example: -350 tons = Tariff reduced imports by 350 tons

**Percentage Change**: Relative effect
```
% Change = (Coefficient / Pre-treatment Mean) × 100
```
- Example: -350 tons / 1000 tons = -35% reduction

### Confidence Intervals

**95% CI**: We are 95% confident true effect lies in this range
- **Narrow CI**: Precise estimate
- **Wide CI**: Uncertain estimate
- **CI includes 0**: Effect is not statistically significant

### Economic vs Statistical Significance

**Statistical Significance**: Effect is unlikely due to chance
**Economic Significance**: Effect is large enough to matter practically

Example:
- Effect = -0.5 tons, p = 0.001 → Statistically significant but economically trivial
- Effect = -500 tons, p = 0.04 → Both statistically and economically significant

---

## Limitations & Assumptions

### DID Assumptions

1. **Parallel Trends** (Critical!)
   - Treated and control would have had same trend without treatment
   - Untestable directly (counterfactual is unobserved)
   - Can test with pre-treatment data and event studies

2. **No Anticipation**
   - Units don't change behavior before treatment
   - Violated if firms stockpile before tariff

3. **Stable Unit Treatment Value (SUTVA)**
   - Treatment of one unit doesn't affect others
   - Violated if countries substitute to each other (spillovers)

4. **Common Shocks**
   - Time fixed effects capture all common shocks
   - Violated if treated countries experience unique shock at same time

### Synthetic Control Assumptions

1. **No Interference**
   - Donor pool countries not affected by treatment
   - Violated if tariff causes trade diversion to controls

2. **Convex Hull**
   - Treated unit can be represented as convex combination of donors
   - Difficult if treated unit is extreme (e.g., largest importer)

3. **Pre-Treatment Stability**
   - Relationship between treated and donors is stable
   - Violated if structural break in pre-period

### General Limitations

1. **External Validity**
   - Results may not generalize to different tariffs or time periods
   - Context-specific: 2018 tariffs on steel

2. **Measurement Error**
   - Trade data may have reporting lags, misclassification
   - Prices are unit values (quantity-weighted), not pure prices

3. **Partial Equilibrium**
   - We analyze direct effects, not general equilibrium
   - Ignore feedback loops, macroeconomic adjustments

4. **Short Time Horizon**
   - Effects estimated over 2-3 years
   - Long-run effects may differ (structural adjustments)

---

## Technical Implementation Notes

### Software Requirements
```
numpy, pandas, matplotlib, seaborn
scipy, statsmodels, scikit-learn
```

### Data Structure
Panel data (country × time):
- **Unit identifier**: country
- **Time variable**: date (monthly)
- **Outcome variables**: import_volume_tons, import_price_per_ton
- **Treatment variables**: treated (binary), post_treatment (binary)

### Key Functions

**DID Analysis**:
```python
did = DIDAnalyzer(data, outcome_var='import_volume_tons')
model = did.estimate_twoway_fe()  # Main estimation
pt = did.parallel_trends_test()    # Validity test
event = did.event_study()          # Dynamic effects
placebo = did.placebo_test_time()  # Placebo test
```

**Synthetic Control**:
```python
sc = SyntheticControl(data, treated_unit='China')
weights = sc.fit()                     # Find optimal weights
effects = sc.get_treatment_effect()    # Calculate effects
fit = sc.get_pre_treatment_fit()       # Check fit quality
placebo = sc.placebo_test_in_space()   # Placebo test
```

---

## Conclusion

This methodology combines:
1. **Rigorous causal inference** (DID + Synthetic Control)
2. **Comprehensive validity testing** (parallel trends, event studies, placebos)
3. **Transparent reporting** (coefficients, p-values, confidence intervals)

The dual approach provides:
- **Triangulation**: Multiple methods reaching same conclusion → Strong evidence
- **Robustness**: Results hold across specifications → Reliable estimates
- **Credibility**: Assumptions tested and validated → Trustworthy inferences

**Final Recommendation**:
- Trust results if BOTH methods agree AND validity tests pass
- Be cautious if methods diverge or tests fail
- Always report limitations and assumptions clearly
