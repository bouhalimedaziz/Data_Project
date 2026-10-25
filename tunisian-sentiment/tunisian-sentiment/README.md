# Cross-Script Sentiment Transfer for Tunisian Dialect

Midterm project, Data Science. CRISP-DM phases covered: Business Understanding, Data Understanding, Data Preparation (including feature engineering). No model is trained at this stage.

Authors: Aziz, Khaoula, Mouhib, Iskander.

**Question.** Can a sentiment model trained on Tunisian comments written in Latin letters (Arabizi, TUNIZI V2) work on comments written in Arabic script (TSAC)? The data preparation maps both scripts to one shared, vowel-free Latin form (عيشك → 3chk, 3aychek → 3chk) so that the two vocabularies overlap.

## Layout

```
data/raw/tunizi/      TUNIZI V2 as downloaded (never edited)
data/raw/tsac/        TSAC train/test, positive/negative, as downloaded (never edited)
data/interim/         tunizi_clean.csv, tsac_clean.csv
data/processed/       master_clean.csv, master_converted.csv.gz, overlap and error-rate results
data/manual/          manual_sample.csv (60 sampled comments) and the hand-written conversions
logs/                 cleaning, merge and feature logs (one row per step)
notebooks/            01_clean_tunizi, 01_clean_tsac, 01b_manual_sample, 02_merge, 03_eda, 04_conversion, 05_features
src/                  shared code used by all notebooks
tests/                unit tests for the conversion
figures/              plots, PNG 200 dpi
report/               midterm report (Word)
```

## Setup

```bash
pip install -r requirements.txt
python -m pytest tests/ -q        # 27 conversion tests
```

In Colab, clone the repository into `/content`, `%cd` into it, and run each notebook top to bottom. The first cell of every notebook finds the repository root by itself.

## Pipeline

Run the notebooks in this order; each one only needs the outputs of the previous ones.

| # | Notebook | Output |
|---|---|---|
| 1 | `01_clean_tunizi` | `data/interim/tunizi_clean.csv` (96,444 rows) + log |
| 2 | `01_clean_tsac` | `data/interim/tsac_clean.csv` (15,201 rows) + log |
| 3 | `01b_manual_sample` | `data/manual/manual_sample.csv` (60 rows); runs once and refuses to overwrite the hand-written files |
| 4 | `02_merge` | `data/processed/master_clean.csv` (111,531 rows), `logs/merge_log.csv`, `logs/script_check_30.csv` (script rule correct on 30/30 rows) |
| 5 | `03_eda` | 8 figures, two hypothesis tests (chi-square, Mann-Whitney U), correlation heatmap |
| 6 | `04_conversion` | `master_converted.csv.gz`, `overlap_results.csv`, `cer_rows.csv`, `cer_worst5.csv`, overlap figure |
| 7 | `05_features` | TF-IDF character n-grams with chi-square selection, numeric features, character sequences, `logs/features_summary.csv` |

## Shared code

| File | Contents |
|---|---|
| `src/load_raw.py` | `load_tunizi(root)`, `load_tsac(split, root)`: raw data with stable ids |
| `src/cleaning_utils.py` | `fix_text()`, `has_letter()`, `CleaningLog` |
| `src/script_detect.py` | `detect_script(text)` → `arabic` / `arabizi` / `mixed` (80% rule) |
| `src/transliteration.py` | `normalize(text)`, `convert(text, keep_wy=False)` |
| `src/features.py` | TF-IDF, numeric features, character sequences, all fitted on training rows only |
| `src/plot_style.py` | fixed colors and plot defaults |

**Ids.** TUNIZI rows are `tunizi_000001…` in file order. TSAC rows are numbered per split, positive file first, then negative: `tsac_train_00001…tsac_train_13669`, `tsac_test_00001…tsac_test_03400`. Loading through `load_raw.py` keeps ids identical in every file.

## Key results

- **Leakage control:** train copies of TSAC test comments and TUNIZI copies of TSAC texts are removed; every feature builder is fitted on training rows only.
- **Overlap:** without the mapping, 1.5% of distinct Arabic test words appear in the Arabizi training data; with the mapping, 73.1%.
- **Conversion accuracy:** character error rate 0.105 on 58 hand-written comments (target ≤ 0.15). Two comments are excluded because the annotator censored offensive words. Keeping w and y raises the error to 0.196, which supports removing all vowels.
- `fix_text()` removes invisible characters and maps Arabic presentation-form letters (ﻻ, ﻣ…) to standard Arabic; without this, 16 real Arabic comments were deleted as "no letters".
- Plot colors: Arabic blue `#1f77b4`, Arabizi orange `#ff7f0e`, positive green `#2ca02c`, negative purple `#9467bd` (colorblind-safe).

## Data sources

- TUNIZI V2: Fourati et al., WANLP 2021, [github.com/iCompass-ai/TUNIZI](https://github.com/iCompass-ai/TUNIZI) (MIT licence).
- TSAC: Medhaffar et al., WANLP 2017, [github.com/fbougares/TSAC](https://github.com/fbougares/TSAC) (LGPL-3.0 licence).
