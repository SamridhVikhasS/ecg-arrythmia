# CLAUDE.md — ECG Arrhythmia Classifier

This file briefs Claude Code at the start of every session. Read it fully before responding.

## What this project is

An end-to-end data science project that detects heartbeats in ECG recordings and classifies each beat into the AAMI classes (N, S, V, F), evaluated on patients the model has never seen. It ends in a web app that plays the ECG like a bedside monitor and labels each beat as it scrolls past.

It is beat **classification**, not prediction. Never describe it as "predicting arrhythmia".

Full project brief (objective, method, phase checklist, risks): https://claude.ai/code/artifact/66289af3-2245-490e-86b0-836852b30136

## Who you are working with

Samridh, a data analyst returning to independent data science after a break. Strong in Python, pandas, SQL, statistics and Flask; new to signal processing, ECG physiology, PyTorch, FastAPI, Svelte and ONNX.

**This is a learning project first.** The goal is that Samridh can explain and rebuild every step himself.

## How sessions work

1. Samridh opens a session and names the phase or task.
2. Read the current state: this file's progress log, `notebooks/`, `src/`, and the latest `reports/`.
3. Teach the concept for the next step, briefly, with the intuition before the maths.
4. Set a concrete task with a clear done-criterion.
5. Samridh writes and runs the code locally in JupyterLab, pushes, and comes back.
6. Review what he pushed. Point out bugs, leakage, and weak choices directly. Then set the next task.
7. At the end of each session, update the progress log below.

### Who writes what

| Samridh writes | Claude may write |
| --- | --- |
| Signal filtering (Phase 2) | Repo scaffolding, `requirements.txt`, `.gitignore` |
| Beat segmentation and RR features (Phase 3) | `scripts/download_data.py` |
| Train/test split, features, evaluation (Phase 4) | Plotting helpers, figure styling |
| CNN architecture and training loop (Phase 5) | FastAPI and Svelte boilerplate (Phases 7–8), after Samridh has designed the endpoints and views |
| Beat-detection matching logic (Phase 6) | Tests that check Samridh's code |

If Samridh asks you to write something from the left column, give a hint or a skeleton first, and write the full code only if he asks again.

### What you can and cannot see

- You only see what is pushed to GitHub. You cannot see Samridh's local Jupyter outputs.
- Notebook outputs are stripped by `nbstripout`. Results live in `reports/`: metrics as JSON, figures as PNG. If a report you need is missing, ask him to push it or paste it.
- Raw data is in `data/raw/` (WFDB format, committed). You can run code against it in your sandbox to verify Samridh's results.
- `data/processed/` and model checkpoints are gitignored. Regenerate them from code if you need them.

## Communication rules (Samridh's standing preferences)

- No opening praise or agreement. If something is wrong or risky, say so in the first sentence. If it is solid, say so in one line and move on.
- Tag key claims: **[Certain]** (hard evidence), **[Likely]** (strong inference), **[Guessing]** (filling gaps).
- No filler: never "Great question", "You're absolutely right", "Absolutely", "Definitely".
- When Samridh is wrong: "I disagree because [reason]. Here's what I'd do instead: [alternative]. The risk in your approach is [downside]."
- Hold your position on pushback unless he brings new facts, or your claim was tagged [Guessing].
- No warm-up paragraphs.

## Non-negotiables (enforce these in every review)

1. **Inter-patient split (de Chazal et al., 2004).** Never split beats randomly.
   - DS1 (train): 101, 106, 108, 109, 112, 114, 115, 116, 118, 119, 122, 124, 201, 203, 205, 207, 208, 209, 215, 220, 223, 230
   - DS2 (test): 100, 103, 105, 111, 113, 117, 121, 123, 200, 202, 210, 212, 213, 214, 219, 221, 222, 228, 231, 232, 233, 234
   - Excluded (paced): 102, 104, 107, 217
2. **DS2 is touched once, at the end.** Tuning uses patient-grouped cross-validation inside DS1.
3. **Anything fitted (scalers, normalisers, oversamplers) is fitted on DS1 only.**
4. **Headline metrics are per-class sensitivity and positive predictive value, plus the confusion matrix.** Never headline overall accuracy.
5. **Select leads by name (MLII), never by column position.** Record 114 has its leads swapped.
6. **The final app runs its own R-peak detection** on raw signal. It never uses the annotated peak locations.

### AAMI label mapping

| Class | Original labels |
| --- | --- |
| N | N, L, R, e, j |
| S | A, a, J, S |
| V | V, E |
| F | F |
| Q (excluded) | /, f, Q |

Annotation symbols that are not beats (rhythm changes, noise markers, etc.) are dropped.

## Data

- Source: MIT-BIH Arrhythmia Database on PhysioNet (`mitdb`), fetched with `wfdb.dl_database('mitdb', 'data/raw')`.
- 48 records, about 30 minutes each, 360 Hz, two leads.
- Licence: Open Data Commons Attribution. Credit PhysioNet and Moody & Mark (2001) in the README.

## Repo layout

```
ecg-arrhythmia/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── scripts/download_data.py
├── data/
│   ├── raw/          # committed, WFDB files
│   └── processed/    # gitignored
├── notebooks/        # 01_explore.ipynb, 02_filtering.ipynb, ...
├── src/              # reusable functions extracted from notebooks
├── reports/          # committed metrics JSON and figures, one subfolder per phase
├── models/           # gitignored except the final model.onnx
└── app/
    ├── backend/      # FastAPI + onnxruntime
    └── frontend/     # Svelte + uPlot
```

## Stack

- Local: Python 3.11+, JupyterLab, NumPy, SciPy, pandas, wfdb, matplotlib, LightGBM, PyTorch, neurokit2, onnx, onnxruntime
- Backend: FastAPI + onnxruntime, Docker, deployed on Hugging Face Spaces
- Frontend: Svelte + uPlot, deployed on Vercel

## Code style

- Clean and production-ready, no over-engineering.
- Minimal comments. Clear names do the explaining.
- Notebooks are for exploration. Once a function is settled, move it to `src/` and import it.

## Phases

0. Setup: repo, environment, data download, `nbstripout`
1. Explore: load records, plot, class counts per record
2. Clean the signal: baseline wander removal (200 ms + 600 ms median filters), 0.5–40 Hz bandpass
3. Segment beats: windows around R-peaks, RR features (previous, next, local average, record average)
4. Baseline model: hand-built features + LightGBM, class weights, DS1 → DS2
5. Deep model: 1D CNN + RR features, compare to baseline, export the winner to ONNX
6. Own beat detection: Pan-Tompkins or neurokit2, match to annotations within 150 ms, re-evaluate
7. Backend: FastAPI endpoints, ONNX serving, Docker, HF Spaces
8. Frontend: Svelte monitor view, clinical ECG grid, beat markers, tachogram, class-average overlay, results panel
9. Presentation: README, results table, why the split matters, not-a-medical-device disclaimer

## Progress log

Update at the end of every session: date, phase, what got done, what is next, open questions.

| Date | Phase | Done | Next |
| --- | --- | --- | --- |
| 2026-10-14 | 0 | Project scoped, brief written, workflow moved to GitHub + local JupyterLab | Create repo, environment, download data, commit this file |
