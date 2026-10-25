"""Shared cleaning helpers used on BOTH datasets (TUNIZI and TSAC).

Rule: cleaning removes rows and fixes encoding only.
It never lowercases or rewrites words; that is the conversion step
(src/transliteration.py).
"""
import re
import unicodedata

import pandas as pd

# Letters we accept: Latin (incl. accented French letters) and Arabic
# (U+0621..U+064A plus the Tunisian extras ڤ پ چ گ).
LETTER_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿء-يڤپچگ]")
_SPACES_RE = re.compile(r"\s+")
# Arabic "presentation forms": an old encoding of the same letters (e.g. ﻣﻤﺜﻞ, ﻻ).
# Our letter checks only know the standard block, so these are mapped back to it.
_PRESENTATION_RE = re.compile(r"[ﭐ-﷿ﹰ-ﻼ]")
# Invisible characters that break duplicate matching: byte-order mark / zero-width
# no-break space, zero-width space and non-joiner, direction marks and embeddings.
# (The zero-width joiner U+200D is kept: it glues multi-part emoji together.)
_INVISIBLE_RE = re.compile(r"[﻿​‌‎‏‪-‮⁦-⁩]")


def fix_text(text) -> str:
    """Fix encoding only, never the words themselves.

    - `_x000D_` artifacts become a space
    - invisible characters (U+FEFF, zero-width space, direction marks) are removed
    - Arabic presentation forms are mapped to standard Arabic letters (ﻻ -> لا)
    - surrounding spaces are stripped and repeated spaces collapsed

    Non-string values (NaN) become an empty string so they are caught by the
    empty-row step.
    """
    if not isinstance(text, str):
        return ""
    text = text.replace("_x000D_", " ")
    text = _INVISIBLE_RE.sub("", text)
    text = _PRESENTATION_RE.sub(lambda m: unicodedata.normalize("NFKC", m.group()), text)
    return _SPACES_RE.sub(" ", text).strip()


def has_letter(text) -> bool:
    """True if the text contains at least one Latin or Arabic letter."""
    return isinstance(text, str) and bool(LETTER_RE.search(text))


class CleaningLog:
    """Collects one row per cleaning step.

    Columns: step, rows_before, rows_after, removed, note
    (one row per step; saved as logs/cleaning_log_*.csv).
    """

    def __init__(self):
        self.rows = []

    def add(self, step: str, before: int, after: int, note: str = ""):
        self.rows.append(
            {"step": step, "rows_before": before, "rows_after": after,
             "removed": before - after, "note": note}
        )
        print(f"{step:<45} {before:>7} -> {after:>7}  (removed {before - after})")

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows, columns=["step", "rows_before", "rows_after", "removed", "note"])

    def save(self, path):
        self.to_frame().to_csv(path, index=False, encoding="utf-8")
