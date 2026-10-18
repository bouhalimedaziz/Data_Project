"""Script detection rule agreed by the team.

1. Count Arabic letters (U+0621..U+064A plus ڤ پ چ گ) and Latin letters
   (a-z, A-Z and accented letters such as é, à, ç). Digits, emoji and
   punctuation are ignored.
2. >= 80% Arabic letters -> "arabic"; >= 80% Latin letters -> "arabizi";
   anything else -> "mixed" (removed and counted at the merge step).

The 80% threshold lets an Arabic comment contain a stray Latin word
(a name, "ok") without being called mixed.
"""
import re

ARABIC_RE = re.compile(r"[ء-يڤپچگ]")
LATIN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")
THRESHOLD = 0.80


def script_counts(text: str):
    """Return (n_arabic_letters, n_latin_letters)."""
    if not isinstance(text, str):
        return 0, 0
    return len(ARABIC_RE.findall(text)), len(LATIN_RE.findall(text))


def detect_script(text: str) -> str:
    """Return 'arabic', 'arabizi' or 'mixed'."""
    n_ar, n_lat = script_counts(text)
    total = n_ar + n_lat
    if total == 0:
        return "mixed"  # no letters; such rows are already removed by cleaning
    if n_ar / total >= THRESHOLD:
        return "arabic"
    if n_lat / total >= THRESHOLD:
        return "arabizi"
    return "mixed"


if __name__ == "__main__":
    for s in ["عيشك", "3aychek", "عيشك ok", "bravo تبارك الله", "😂😂 2016"]:
        print(f"{s!r:25} -> {detect_script(s)}")
