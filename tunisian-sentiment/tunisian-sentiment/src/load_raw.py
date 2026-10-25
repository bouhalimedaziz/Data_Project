"""Load the raw datasets with stable ids.

All notebooks load through these two functions, so the same comment always gets the same id
in every notebook and file (cleaning, manual sample, merge).

Id order (fixed, do not change):
- TUNIZI V2: file order, tunizi_000001 ... tunizi_100000
- TSAC: per split, the *_pos.txt lines first, then *_neg.txt, numbered from 1:
  tsac_train_00001 ... tsac_train_13669, tsac_test_00001 ... tsac_test_03400
"""
from pathlib import Path

import pandas as pd

TUNIZI_LABELS = {"1": "pos", "-1": "neg", "0": "neutral"}


def _lines(path: Path):
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    if lines and lines[-1] == "":  # trailing newline at end of file
        lines = lines[:-1]
    return lines


def load_tunizi(root=".") -> pd.DataFrame:
    """TUNIZI V2 as id, text, label_raw ('1', '-1', '0'). Text is untouched."""
    lines = [l for l in _lines(Path(root) / "data/raw/tunizi/TUNIZI_V2.txt") if l != ""]
    rows = [l.rsplit(";", 1) for l in lines]  # split on the LAST ';'
    if any(len(r) != 2 for r in rows):
        raise ValueError("a TUNIZI line has no ';' separator")
    df = pd.DataFrame(rows, columns=["text", "label_raw"])
    df.insert(0, "id", [f"tunizi_{i:06d}" for i in range(1, len(df) + 1)])
    return df


def load_tsac(split: str, root=".") -> pd.DataFrame:
    """One TSAC split ('train' or 'test') as id, text, label ('pos'/'neg'), split.

    Text is untouched (empty lines are kept so the cleaning log can count them).
    """
    if split not in ("train", "test"):
        raise ValueError("split must be 'train' or 'test'")
    parts = []
    for label in ("pos", "neg"):
        lines = _lines(Path(root) / f"data/raw/tsac/{split}_{label}.txt")
        parts.append(pd.DataFrame({"text": lines, "label": label}))
    df = pd.concat(parts, ignore_index=True)
    df.insert(0, "id", [f"tsac_{split}_{i:05d}" for i in range(1, len(df) + 1)])
    df["split"] = split
    return df
