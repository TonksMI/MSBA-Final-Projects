# MSBA Final Projects

Portfolio of data science and machine learning projects from the Chapman University MSBA program.

---

## Projects

### Predictive Modeling
**[`predictive-modeling/`](predictive-modeling/)**  
ML for Managers coursework (BUS 659) and independent project.

| File | Description | Tech |
|---|---|---|
| `bus659-midterm-exam.ipynb` | Midterm: ad campaign analysis + graduate salary prediction | Python, pandas, scikit-learn |
| `bus659-problem-set-2.ipynb` | Classification models on tabular business data | Python, logistic regression, decision trees |
| `bus659-problem-set-3.ipynb` | Regularization: Lasso, Ridge, Elastic Net | Python, scikit-learn |
| `redfin-housing-prediction.Rmd` | Orange County house price prediction (Elastic Net / Lasso vs OLS) | R, glmnet |

---

### Data Visualization
**[`data-visualization/`](data-visualization/)**  
Data Visualization for Business coursework (BUS 672).

| File | Description | Tech |
|---|---|---|
| `visualization-playbook.py` | Chart-type reference implementation covering 20+ plot types | Python, matplotlib, seaborn, plotly |
| `visualization-guide.pdf` | Submitted visualization design guide | — |

---

### Statistical Machine Learning
**[`statistical-ml/`](statistical-ml/)**  
Statistical Machine Learning I coursework (CPSC 540).

| File | Description | Tech |
|---|---|---|
| `cpsc540-hw1-analysis.Rmd` | HW1: Poisson + spend regression on marketing campaign data | R, glm, ggplot2 |
| `cpsc540-hw1-plots.R` | Plot generation script for HW1 analysis | R, ggplot2 |
| `marketingcampaign.csv` | Dataset: marketing campaign response records | — |
| `glm-exercise.Rmd` | In-class GLM exercise with logistic and Poisson models | R |

---

### Computer Vision
**[`computer-vision/PPE-Detection/`](computer-vision/PPE-Detection/)**  
YOLOv8-based personal protective equipment detection system for CCTV footage.  
Tech: Python, YOLOv8, OpenCV. *(Full repo linked as submodule)*

---

### NLP Research
**[`nlp-research/LLM-Hallucination/`](nlp-research/LLM-Hallucination/)**  
Research project investigating hallucination patterns in large language models.  
Tech: Python, multi-agent framework, custom evaluation pipeline. *(Full repo linked as submodule)*

---

### Economics & Causal Inference
**[`economics/`](economics/)**  
Applied econometrics projects using public trade and regional data.  
*Status: planning / in progress*

| Project | Description | Methods |
|---|---|---|
| `tariff-causal-analysis/` | Causal impact of 2018 Section 232 steel tariffs on supply chain | Difference-in-Differences, Synthetic Control |
| `regional-demand-forecasts/` | Regional steel demand heterogeneity and market expansion analysis | Clustering, regression, time series, geo viz |

---

## Setup

To clone this repo including submodules:

```bash
git clone --recurse-submodules https://github.com/TonksMI/MSBA-Final-Projects.git
```

If you already cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```
