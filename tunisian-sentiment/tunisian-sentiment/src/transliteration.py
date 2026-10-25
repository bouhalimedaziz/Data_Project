"""
transliteration.py: shared-form conversion for Tunisian Arabic script and Arabizi.

Two public functions:
    normalize(text)                  used in BOTH conditions (with / without mapping)
    convert(text, keep_wy=False)     normalize + map both scripts to one vowel-free Latin form

Version 1. Every change to the mapping is recorded in CHANGELOG.
"""
import re
import unicodedata

VERSION = 1
CHANGELOG = [
    "v1: initial version.",
]

# ---------------------------------------------------------------------------
# Mapping table: Arabic letter -> shared form ("" = removed, vowel)
# ---------------------------------------------------------------------------
ARABIC_TO_SHARED = {
    # same letter
    "ه": "h", "ن": "n", "م": "m", "ل": "l", "ك": "k", "ف": "f",
    "س": "s", "ز": "z", "ر": "r", "د": "d", "ت": "t", "ب": "b",
    # Latin letter differs from the Arabic one
    "پ": "p", "ط": "t", "ص": "s", "ج": "j",
    "چ": "ch", "ش": "ch",
    "ث": "th",
    "ظ": "dh", "ض": "dh", "ذ": "dh",
    "غ": "gh",
    "گ": "g", "ڤ": "g",
    # Arabizi digits
    "ق": "9", "ع": "3", "خ": "5", "ح": "7",
    "ؤ": "2", "ئ": "2", "ء": "2",
    # removed (vowel)
    "ة": "", "ى": "", "ي": "", "و": "", "ا": "",
}
# Variant check: keep w and y, so Arabic و / ي become w / y instead of being removed
ARABIC_TO_SHARED_KEEP_WY = {**ARABIC_TO_SHARED, "و": "w", "ي": "y"}

LATIN_VOWELS = set("aeiouwy")
LATIN_VOWELS_KEEP_WY = set("aeiou")

# ---------------------------------------------------------------------------
# normalize() helpers
# ---------------------------------------------------------------------------
_ARABIC_DIACRITICS = {chr(c) for c in range(0x064B, 0x0653)}  # U+064B..U+0652
_TATWEEL = "\u0640"
_ARABIC_UNIFY = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي"})
_DIGITS = str.maketrans(
    {**{0x0660 + i: str(i) for i in range(10)},   # Arabic-Indic digits
     **{0x06F0 + i: str(i) for i in range(10)}}   # Extended (Persian) digits
)
_ELONGATION_RE = re.compile(r"(.)\1{2,}", re.DOTALL)
_EMOJI_STRIP_RE = re.compile("[\U0001F3FB-\U0001F3FF\uFE0F\uFE0E\u200D]")  # skin tones, VS16, VS15, ZWJ
_EMOJI_RE = re.compile(
    "([\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF\u2190-\u21FF\u203C\u2049\u2122\u2139])"
)
_SPACES_RE = re.compile(r"\s+")


def _strip_french_accents(text: str) -> str:
    """é -> e, à -> a, ç -> c ... Only Latin combining marks are dropped,
    then NFC recomposes Arabic letters such as ؤ and ئ that NFD splits."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not "\u0300" <= c <= "\u036f")
    return unicodedata.normalize("NFC", text)


def normalize(text: str) -> str:
    """Normalization shared by both conditions (with and without the mapping)."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # Arabic: unify alef/ya forms (before NFD so أ is not split), drop diacritics and tatweel
    text = text.translate(_ARABIC_UNIFY)
    text = "".join(c for c in text if c not in _ARABIC_DIACRITICS and c != _TATWEEL)
    text = text.translate(_DIGITS)
    # French accents
    text = _strip_french_accents(text)
    # Elongation: 3+ repeats -> 1  (ya3333jbni -> ya3jbni)
    text = _ELONGATION_RE.sub(r"\1", text)
    # Emoji: drop modifiers, then a space around each emoji
    text = _EMOJI_STRIP_RE.sub("", text)
    text = _EMOJI_RE.sub(r" \1 ", text)
    return _SPACES_RE.sub(" ", text).strip()


# ---------------------------------------------------------------------------
# convert()
# ---------------------------------------------------------------------------
_EIGHT_RE = re.compile(r"(?<=[a-z])8|8(?=[a-z])")  # 8 touching a letter only (2018 stays)
_REPEAT_RE = re.compile(r"(.)\1+", re.DOTALL)


def convert(text: str, keep_wy: bool = False) -> str:
    """normalize(), then map both scripts to the shared vowel-free Latin form.

    keep_wy=True is the variant check: w and y are not removed.
    """
    text = normalize(text)
    if not text:
        return ""

    # Arabizi spellings unified. Done BEFORE the Arabic mapping so that an Arabic
    # sequence like ك+ه (mapped to "kh") is not wrongly turned into 5.
    text = text.replace("sh", "ch").replace("kh", "5")
    text = _EIGHT_RE.sub("gh", text)

    # Arabic letters -> shared form
    table = ARABIC_TO_SHARED_KEEP_WY if keep_wy else ARABIC_TO_SHARED
    text = "".join(table.get(c, c) for c in text)

    # Remove Latin vowels
    vowels = LATIN_VOWELS_KEEP_WY if keep_wy else LATIN_VOWELS
    text = "".join(c for c in text if c not in vowels)

    # Collapse any repeated character (7bbt -> 7bt)
    text = _REPEAT_RE.sub(r"\1", text)
    return _SPACES_RE.sub(" ", text).strip()


if __name__ == "__main__":
    for s in ["عيشك", "3aychek", "ya3333jbni", "حبيت", "7abbit", "Ça va très bien 😂😂🏽"]:
        print(f"{s!r:28} norm={normalize(s)!r:24} conv={convert(s)!r}")
