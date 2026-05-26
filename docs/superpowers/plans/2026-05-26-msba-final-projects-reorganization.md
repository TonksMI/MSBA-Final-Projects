# MSBA Final Projects Reorganization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize MSBA-Final-Projects into a clean thematic portfolio by moving final-submission files from MSBA-Notes, relocating existing economics stubs, and linking PPE-Detection and LLM-Hallucination as git submodules.

**Architecture:** All changes land on the `main` branch of `MSBA-Final-Projects`. Files from `MSBA-Notes` are copied (not moved) since that repo stays intact as a notes archive. Existing economics folders are renamed in-place using `git mv`. Submodules are registered in `.gitmodules` and initialized at their target paths.

**Tech Stack:** git 2.50+, PowerShell / Bash on Windows, no build tools required.

---

## Assumed State

Both repos are already cloned locally:
- `MSBA-Notes` → `D:\First Semester projects\MSBA-Notes`
- `MSBA-Final-Projects` → `D:\First Semester projects\MSBA-Final-Projects`

All commands below run from within `D:\First Semester projects\MSBA-Final-Projects` unless stated otherwise.

---

## Task 1: Reorganize economics/ folder

Move the two existing root-level stubs under a new `economics/` parent using `git mv` so the rename is tracked in git history.

**Files:**
- Rename: `Causal Impact of 2018 Tarrifs/` → `economics/tariff-causal-analysis/`
- Rename: `Regional Demand Forcasts/` → `economics/regional-demand-forecasts/`

- [ ] **Step 1.1: Create economics/ parent directory**

```bash
cd "D:/First Semester projects/MSBA-Final-Projects"
mkdir -p economics
```

Expected: directory `economics/` created with no output.

- [ ] **Step 1.2: Move tariff analysis folder**

```bash
git mv "Causal Impact of 2018 Tarrifs" economics/tariff-causal-analysis
```

Expected: no output, no error. Run `git status` — should show `renamed: Causal Impact of 2018 Tarrifs/Project Overview.txt -> economics/tariff-causal-analysis/Project Overview.txt`.

- [ ] **Step 1.3: Move regional demand folder**

```bash
git mv "Regional Demand Forcasts" economics/regional-demand-forecasts
```

Expected: no output. `git status` shows both renames staged.

- [ ] **Step 1.4: Commit**

```bash
git commit -m "$(cat <<'EOF'
refactor: move economics stubs under economics/ with corrected names

Renames typo'd root folders (Tarrifs, Forcasts) to kebab-case paths
under economics/ parent directory.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Expected: `[main xxxxxxx] refactor: move economics stubs under economics/ with corrected names`

---

## Task 2: Copy predictive-modeling files

Copy four final-submission files from MSBA-Notes into a new `predictive-modeling/` folder with standardized kebab-case names.

**Files:**
- Create: `predictive-modeling/bus659-midterm-exam.ipynb`
- Create: `predictive-modeling/bus659-problem-set-2.ipynb`
- Create: `predictive-modeling/bus659-problem-set-3.ipynb`
- Create: `predictive-modeling/redfin-housing-prediction.Rmd`

- [ ] **Step 2.1: Create the folder**

```bash
mkdir -p "D:/First Semester projects/MSBA-Final-Projects/predictive-modeling"
```

- [ ] **Step 2.2: Copy midterm exam**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\BUS 659\Class Folder\Midterm\Matt_Tonks_BUS659_Midterm_Exam.ipynb" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\predictive-modeling\bus659-midterm-exam.ipynb"
```

Expected: file appears at destination. Verify: `ls "D:\First Semester projects\MSBA-Final-Projects\predictive-modeling\"` shows `bus659-midterm-exam.ipynb`.

- [ ] **Step 2.3: Copy problem set 2**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\BUS 659\Class Folder\problem sets\BUS659_ProblemSet2_Tonks.ipynb" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\predictive-modeling\bus659-problem-set-2.ipynb"
```

- [ ] **Step 2.4: Copy problem set 3**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\BUS 659\Class Folder\problem sets\BUS659_ProblemSet3_MattTonks.ipynb" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\predictive-modeling\bus659-problem-set-3.ipynb"
```

- [ ] **Step 2.5: Copy Redfin housing prediction**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\sample files\FinalProject.Rmd" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\predictive-modeling\redfin-housing-prediction.Rmd"
```

- [ ] **Step 2.6: Stage and commit**

```bash
cd "D:/First Semester projects/MSBA-Final-Projects"
git add predictive-modeling/
git status
```

Expected: 4 new files listed under `Changes to be committed`.

```bash
git commit -m "$(cat <<'EOF'
feat: add predictive-modeling projects from BUS659 and sample files

Includes: midterm exam, problem sets 2 and 3 (ML for Managers),
and Redfin Orange County housing price prediction (elastic net / lasso).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Copy data-visualization files

Copy two files from BUS 672 Assignment 2 into `data-visualization/`.

**Files:**
- Create: `data-visualization/visualization-playbook.py`
- Create: `data-visualization/visualization-guide.pdf`

- [ ] **Step 3.1: Create the folder**

```bash
mkdir -p "D:/First Semester projects/MSBA-Final-Projects/data-visualization"
```

- [ ] **Step 3.2: Copy visualization playbook**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\BUS 672\Assignments\Assignment 2\Visualization-Playbook-By-Type.py" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\data-visualization\visualization-playbook.py"
```

- [ ] **Step 3.3: Copy visualization guide PDF**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\BUS 672\Assignments\Assignment 2\Matthew Tonks Visualization guide.pdf" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\data-visualization\visualization-guide.pdf"
```

- [ ] **Step 3.4: Stage and commit**

```bash
cd "D:/First Semester projects/MSBA-Final-Projects"
git add data-visualization/
git status
```

Expected: 2 new files listed.

```bash
git commit -m "$(cat <<'EOF'
feat: add data-visualization projects from BUS672

Includes: visualization playbook by chart type (Python/matplotlib/seaborn/plotly)
and the submitted visualization guide PDF.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Copy statistical-ml files

Copy four files from CPSC 540 into `statistical-ml/`.

**Files:**
- Create: `statistical-ml/cpsc540-hw1-analysis.Rmd`
- Create: `statistical-ml/cpsc540-hw1-plots.R`
- Create: `statistical-ml/marketingcampaign.csv`
- Create: `statistical-ml/glm-exercise.Rmd`

- [ ] **Step 4.1: Create the folder**

```bash
mkdir -p "D:/First Semester projects/MSBA-Final-Projects/statistical-ml"
```

- [ ] **Step 4.2: Copy HW1 analysis**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\CPSC 540\Assignments\HW 1\Claude Code\HW1_Analysis.Rmd" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\statistical-ml\cpsc540-hw1-analysis.Rmd"
```

- [ ] **Step 4.3: Copy HW1 plot generation script**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\CPSC 540\Assignments\HW 1\Claude Code\generate_plots.R" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\statistical-ml\cpsc540-hw1-plots.R"
```

- [ ] **Step 4.4: Copy marketing campaign dataset**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\CPSC 540\Assignments\HW 1\Claude Code\marketingcampaign.csv" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\statistical-ml\marketingcampaign.csv"
```

- [ ] **Step 4.5: Copy GLM exercise**

```powershell
Copy-Item -Path "D:\First Semester projects\MSBA-Notes\CPSC 540\R Notebooks\GLMExercise.Rmd" `
          -Destination "D:\First Semester projects\MSBA-Final-Projects\statistical-ml\glm-exercise.Rmd"
```

- [ ] **Step 4.6: Stage and commit**

```bash
cd "D:/First Semester projects/MSBA-Final-Projects"
git add statistical-ml/
git status
```

Expected: 4 new files listed.

```bash
git commit -m "$(cat <<'EOF'
feat: add statistical-ml projects from CPSC540

Includes: HW1 marketing campaign analysis (Poisson regression, R),
plot generation script, dataset, and GLM exercise notebook.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Add PPE-Detection as git submodule

Register the PPE-Detection repo as a submodule at `computer-vision/PPE-Detection`.

**Files:**
- Create: `computer-vision/PPE-Detection/` (submodule, populated by git)
- Modify: `.gitmodules` (auto-created/updated by git submodule add)

- [ ] **Step 5.1: Add the submodule**

```bash
cd "D:/First Semester projects/MSBA-Final-Projects"
git submodule add https://github.com/TonksMI/PPE-Detection.git computer-vision/PPE-Detection
```

Expected output:
```
Cloning into 'D:/First Semester projects/MSBA-Final-Projects/computer-vision/PPE-Detection'...
remote: Enumerating objects: ...
```

After completion, verify: `cat .gitmodules` should show:
```
[submodule "computer-vision/PPE-Detection"]
	path = computer-vision/PPE-Detection
	url = https://github.com/TonksMI/PPE-Detection.git
```

- [ ] **Step 5.2: Verify submodule content**

```bash
ls "D:/First Semester projects/MSBA-Final-Projects/computer-vision/PPE-Detection"
```

Expected: `README.md`, `setup_datasets.py`, `src/`, `notebooks/`, `yolov8n.pt`, etc.

- [ ] **Step 5.3: Commit**

```bash
git add .gitmodules computer-vision/
git commit -m "$(cat <<'EOF'
feat: add PPE-Detection as git submodule under computer-vision/

Links TonksMI/PPE-Detection (YOLOv8 PPE safety detection system).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Add LLM-Hallucination as git submodule

Register the LLM-Hulucination repo as a submodule at `nlp-research/LLM-Hallucination`.

**Files:**
- Create: `nlp-research/LLM-Hallucination/` (submodule)
- Modify: `.gitmodules`

- [ ] **Step 6.1: Add the submodule**

```bash
cd "D:/First Semester projects/MSBA-Final-Projects"
git submodule add https://github.com/TonksMI/LLM-Hulucination.git nlp-research/LLM-Hallucination
```

Expected: cloning output, then silent completion.

Verify `.gitmodules` now contains both submodule entries:
```
[submodule "computer-vision/PPE-Detection"]
	path = computer-vision/PPE-Detection
	url = https://github.com/TonksMI/PPE-Detection.git
[submodule "nlp-research/LLM-Hallucination"]
	path = nlp-research/LLM-Hallucination
	url = https://github.com/TonksMI/LLM-Hulucination.git
```

- [ ] **Step 6.2: Verify submodule content**

```bash
ls "D:/First Semester projects/MSBA-Final-Projects/nlp-research/LLM-Hallucination"
```

Expected: `README.md`, `main.py`, `src/`, `agents/`, `config.yaml`, `requirements.txt`, etc.

- [ ] **Step 6.3: Commit**

```bash
git add .gitmodules nlp-research/
git commit -m "$(cat <<'EOF'
feat: add LLM-Hallucination as git submodule under nlp-research/

Links TonksMI/LLM-Hulucination (LLM hallucination detection research).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Write root README.md

Replace the placeholder README with a full project index.

**Files:**
- Modify: `README.md`

- [ ] **Step 7.1: Write README**

Replace the contents of `README.md` with:

```markdown
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
```

- [ ] **Step 7.2: Stage and commit**

```bash
cd "D:/First Semester projects/MSBA-Final-Projects"
git add README.md
git commit -m "$(cat <<'EOF'
docs: write project index README with all six project areas

Covers predictive-modeling, data-visualization, statistical-ml,
computer-vision, nlp-research, and economics. Includes submodule
clone instructions.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Verify structure and push

Final sanity check, then push `main` to remote.

- [ ] **Step 8.1: Verify full tree**

```bash
cd "D:/First Semester projects/MSBA-Final-Projects"
find . -not -path './.git/*' -not -path './computer-vision/PPE-Detection/.git/*' -not -path './nlp-research/LLM-Hallucination/.git/*' | sort
```

Expected output (abbreviated):
```
.
./.gitmodules
./README.md
./computer-vision/PPE-Detection        ← submodule entry (not full tree)
./data-visualization/visualization-guide.pdf
./data-visualization/visualization-playbook.py
./docs/superpowers/plans/2026-05-26-msba-final-projects-reorganization.md
./docs/superpowers/specs/2026-05-26-msba-final-projects-design.md
./economics/regional-demand-forecasts/Project Overview.txt
./economics/tariff-causal-analysis/Project Overview.txt
./nlp-research/LLM-Hallucination       ← submodule entry (not full tree)
./predictive-modeling/bus659-midterm-exam.ipynb
./predictive-modeling/bus659-problem-set-2.ipynb
./predictive-modeling/bus659-problem-set-3.ipynb
./predictive-modeling/redfin-housing-prediction.Rmd
./statistical-ml/cpsc540-hw1-analysis.Rmd
./statistical-ml/cpsc540-hw1-plots.R
./statistical-ml/glm-exercise.Rmd
./statistical-ml/marketingcampaign.csv
```

If any file is missing, copy/add it before pushing.

- [ ] **Step 8.2: Check git log**

```bash
git log --oneline
```

Expected (most recent first):
```
xxxxxxx docs: write project index README with all six project areas
xxxxxxx feat: add LLM-Hallucination as git submodule under nlp-research/
xxxxxxx feat: add PPE-Detection as git submodule under computer-vision/
xxxxxxx feat: add statistical-ml projects from CPSC540
xxxxxxx feat: add data-visualization projects from BUS672
xxxxxxx feat: add predictive-modeling projects from BUS659 and sample files
xxxxxxx refactor: move economics stubs under economics/ with corrected names
xxxxxxx Add design spec for MSBA Final Projects reorganization
xxxxxxx Project Overviews
xxxxxxx Initial commit
```

- [ ] **Step 8.3: Push to remote**

```bash
git push origin main
```

Expected: `Branch 'main' set up to track remote branch 'main' from 'origin'.` and upload lines, ending with `main -> main`.

- [ ] **Step 8.4: Verify on GitHub**

Open `https://github.com/TonksMI/MSBA-Final-Projects` in a browser and confirm:
- All six thematic folders are visible on the `main` branch
- `computer-vision/PPE-Detection` and `nlp-research/LLM-Hallucination` show the submodule `@<commit>` indicator
- README renders with the full project table

---

## Rollback

If anything goes wrong before the push:

```bash
# Undo last N commits (keep files)
git reset --soft HEAD~N

# Remove a submodule completely
git submodule deinit -f computer-vision/PPE-Detection
git rm -f computer-vision/PPE-Detection
rm -rf .git/modules/computer-vision/PPE-Detection
```

The source files in `MSBA-Notes` are never modified — a re-run is always safe.
