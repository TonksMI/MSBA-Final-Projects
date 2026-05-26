# MSBA Final Projects Reorganization — Design Spec
**Date:** 2026-05-26  
**Author:** Matthew Tonks  
**Status:** Approved

---

## Goal

Reorganize the `MSBA-Final-Projects` GitHub repo into a clean, thematic portfolio structure that:
1. Moves final-submission code from `MSBA-Notes` into themed project folders
2. Links standalone project repos (PPE-Detection, LLM-Hallucination) as git submodules
3. Preserves existing planning documents (economics projects) under the new structure
4. Standardizes filenames to descriptive kebab-case for portfolio readability

---

## Source Repos

| Repo | Status | Contains |
|---|---|---|
| `TonksMI/MSBA-Notes` | Public | Coursework, notes, lab code, final submissions |
| `TonksMI/MSBA-Final-Projects` | Private | Existing economics project stubs on `main`; empty Claude-created branches |
| `TonksMI/PPE-Detection` | Public | Full computer vision project (YOLO-based PPE detection) |
| `TonksMI/LLM-Hulucination` | Public | Full NLP research project (LLM hallucination study) |

---

## Target Structure

```
MSBA-Final-Projects/
├── predictive-modeling/
│   ├── bus659-midterm-exam.ipynb
│   ├── bus659-problem-set-2.ipynb
│   ├── bus659-problem-set-3.ipynb
│   └── redfin-housing-prediction.Rmd
│
├── data-visualization/
│   ├── visualization-playbook.py
│   └── visualization-guide.pdf
│
├── statistical-ml/
│   ├── cpsc540-hw1-analysis.Rmd
│   ├── cpsc540-hw1-plots.R
│   ├── marketingcampaign.csv
│   └── glm-exercise.Rmd
│
├── computer-vision/
│   └── PPE-Detection/              ← git submodule (TonksMI/PPE-Detection)
│
├── nlp-research/
│   └── LLM-Hallucination/          ← git submodule (TonksMI/LLM-Hulucination)
│
├── economics/
│   ├── tariff-causal-analysis/
│   │   └── Project Overview.txt    ← moved/renamed from root
│   └── regional-demand-forecasts/
│       └── Project Overview.txt    ← moved/renamed from root
│
├── docs/                           ← spec lives here
└── README.md                       ← updated project index
```

---

## File Mapping

### predictive-modeling/

| New filename | Original path in MSBA-Notes |
|---|---|
| `bus659-midterm-exam.ipynb` | `BUS 659/Class Folder/Midterm/Matt_Tonks_BUS659_Midterm_Exam.ipynb` |
| `bus659-problem-set-2.ipynb` | `BUS 659/Class Folder/problem sets/BUS659_ProblemSet2_Tonks.ipynb` |
| `bus659-problem-set-3.ipynb` | `BUS 659/Class Folder/problem sets/BUS659_ProblemSet3_MattTonks.ipynb` |
| `redfin-housing-prediction.Rmd` | `sample files/FinalProject.Rmd` |

### data-visualization/

| New filename | Original path in MSBA-Notes |
|---|---|
| `visualization-playbook.py` | `BUS 672/Assignments/Assignment 2/Visualization-Playbook-By-Type.py` |
| `visualization-guide.pdf` | `BUS 672/Assignments/Assignment 2/Matthew Tonks Visualization guide.pdf` |

### statistical-ml/

| New filename | Original path in MSBA-Notes |
|---|---|
| `cpsc540-hw1-analysis.Rmd` | `CPSC 540/Assignments/HW 1/Claude Code/HW1_Analysis.Rmd` |
| `cpsc540-hw1-plots.R` | `CPSC 540/Assignments/HW 1/Claude Code/generate_plots.R` |
| `marketingcampaign.csv` | `CPSC 540/Assignments/HW 1/Claude Code/marketingcampaign.csv` |
| `glm-exercise.Rmd` | `CPSC 540/R Notebooks/GLMExercise.Rmd` |

### computer-vision/ and nlp-research/

Added as git submodules — no files copied, repos linked in place:
- `computer-vision/PPE-Detection` → `https://github.com/TonksMI/PPE-Detection.git`
- `nlp-research/LLM-Hallucination` → `https://github.com/TonksMI/LLM-Hulucination.git`

### economics/ (reorganized from root)

Existing folder names on `main` are moved under `economics/` and renamed:
- `Causal Impact of 2018 Tarrifs/` → `economics/tariff-causal-analysis/`
- `Regional Demand Forcasts/` → `economics/regional-demand-forecasts/`

---

## Files Intentionally Excluded

| File | Reason |
|---|---|
| `BUS659_ProblemSet1.ipynb` (5.6MB) | Likely template/starter file, not a named submission |
| `BUS659_ProblemSet1_L.ipynb` | Same — no "Tonks" suffix, appears to be course-provided |
| All `Claude_*` and `Codex_*` exam variants | Drafts/AI comparisons, not final submissions |
| `BUS 672/Assignments/Assignment 1/` | Personal story drafts in markdown — not code |
| `CPSC 540/Assignments/HW 1/codex code/` | Alternative implementation; Claude Code version selected |
| `BUS 672/Jupyter NoteBooks/Fixing data Visualization.ipynb` | In-class exercise, not a final assignment |
| `Claude Code/` (Streamlit app) | Not a course deliverable |
| All `Notes/`, `Assisted Notes/`, `Lectures/` folders | Study materials, not projects |

---

## Architecture Decisions

**Why submodules for PPE-Detection and LLM-Hallucination?**  
These are full, active repositories. Copying their code would create a stale duplicate. Submodules keep them linked to the source of truth while including them in the portfolio index.

**Why the Claude Code HW1 version over codex?**  
The `Claude Code` version has more complete source files (Rmd + R script + dataset + documentation). The `codex code` version has only a Quarto document and compiled model binaries (`.rds`), which are less useful for portfolio review.

**Why kebab-case file renaming?**  
Original filenames embed course codes and author names (`BUS659_ProblemSet2_Tonks.ipynb`). A final projects repo is a portfolio — names like `bus659-problem-set-2.ipynb` are cleaner, searchable, and professional without losing context.

---

## README Content (outline)

The root README will contain:
- One-line description of each project area
- Links to each thematic folder
- Brief tech stack per project (Python/R, key libraries)
- Status indicator for economics projects (planning vs. complete)

---

## Out of Scope

- Writing any new code for the economics projects (tariff analysis, regional demand forecasts)
- Uploading or modifying files in the source repos (MSBA-Notes, PPE-Detection, LLM-Hulucination)
- BUS 671 (SQL/database course) — no code artifacts found, only notes
