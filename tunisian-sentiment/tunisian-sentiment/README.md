# Cross-Script Sentiment Transfer for Tunisian Dialect

Midway project (CRISP-DM: Business Understanding → Data Understanding → Data Preparation).
Team: Aziz, Khaoula, Mouhib, Iskander. Presentation: Wednesday 21 October 2026.

## Layout

```
data/raw/tunizi/      TUNIZI V1 + V2 as downloaded (never edit)
data/raw/tsac/        TSAC train/test pos/neg as downloaded (never edit)
data/interim/         tunizi_clean.csv (Aziz), tsac_clean.csv (Khaoula)
data/processed/       master_clean.csv (Aziz), master_converted.csv (Iskander)
data/manual/          manual_sample.csv + one file per annotator
logs/                 cleaning and merge logs (one row per step)
notebooks/            01_clean_tunizi, 01_clean_tsac, 01b_manual_sample, 02_merge, 03_eda, 04_conversion
src/                  shared code: load_raw.py, cleaning_utils.py, script_detect.py, transliteration.py
figures/              plots, PNG 200 dpi
slides/README.md      link to the shared deck
```

## Shared code (use it, don't copy it)

| File | What it gives you |
|---|---|
| `src/load_raw.py` | `load_tunizi(root)`, `load_tsac(split, root)`: raw data with **stable ids** |
| `src/cleaning_utils.py` | `fix_text()`, `has_letter()`, `CleaningLog` (writes the log format) |
| `src/script_detect.py` | `detect_script(text)` → `arabic` / `arabizi` / `mixed` (80% rule) |

**Ids:** TUNIZI rows are `tunizi_000001…` in file order. TSAC rows are numbered per split, **pos file first, then neg**:
`tsac_train_00001…tsac_train_13669`, `tsac_test_00001…tsac_test_03400`. Always load through `load_raw.py` so ids match everywhere.

## Running in Colab

```python
!git clone https://github.com/<owner>/tunisian-sentiment.git
%cd tunisian-sentiment
```
Then run the notebook top to bottom; the first cell finds the repo root by itself.
Save back with File → Save a copy in GitHub.

## Pipeline status

| Step | Owner | Output | Status |
|---|---|---|---|
| Clean TUNIZI V2 | Aziz | `data/interim/tunizi_clean.csv` (96,444 rows) | done |
| Manual sample | Aziz | `data/manual/manual_*.csv` (60 rows) | done, waiting for conversions |
| Clean TSAC | Khaoula | `data/interim/tsac_clean.csv` | in progress |
| Merge | Aziz | `data/processed/master_clean.csv` | notebook ready, runs once `tsac_clean.csv` is pushed |
