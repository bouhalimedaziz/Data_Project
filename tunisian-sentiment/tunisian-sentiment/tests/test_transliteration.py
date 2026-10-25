"""Run from the repo root:  python -m pytest tests/ -v"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from transliteration import convert, normalize  # noqa: E402

# (Arabic, Arabizi) pairs that must give the same output.
PAIRS = [
    ("عيشك", "3aychek"),        # -> 3chk
    ("حبيت", "7abbit"),         # -> 7bt
    ("برشا", "barcha"),
    ("يعطيك", "ya3tik"),
    ("نحب", "n7ebb"),
    ("مش", "mech"),
    ("خايب", "khayeb"),
    ("غالي", "ghali"),
    ("غالي", "8ali"),           # 8 -> gh
    ("قلبي", "9albi"),
    ("مزيان", "mezyen"),
    ("فرحان", "far7an"),
    ("عجبني", "ya3jbni"),
    ("ممتاز", "momtaz"),
    ("ضعيف", "dha3if"),
    ("شفت", "chouft"),
    ("شوف", "shouf"),           # sh -> ch
    ("كرهت", "krhet"),
]


@pytest.mark.parametrize("arabic,arabizi", PAIRS)
def test_pairs_match(arabic, arabizi):
    assert convert(arabic) == convert(arabizi)


def test_worked_examples():
    assert convert("عيشك") == "3chk"
    assert convert("3aychek") == "3chk"
    assert convert("حبيت") == "7bt"
    assert convert("7abbit") == "7bt"


def test_elongation():
    assert normalize("ya3333jbni") == "ya3jbni"


def test_accents_and_case():
    assert normalize("Très Élégant ÇA") == "tres elegant ca"


def test_arabic_diacritics_tatweel_unify_digits():
    assert normalize("أَحْبَـــك") == "احبك"      # diacritics + tatweel removed, أ -> ا
    assert normalize("مصطفى") == "مصطفي"          # ى -> ي
    assert normalize("٢٠١٦") == "2016"


def test_emoji_spacing_and_modifiers():
    assert normalize("top👍🏽!") == "top 👍 !"
    assert normalize("❤️❤️") == "❤ ❤"
    assert "😂" in convert("mdr😂")


def test_year_not_turned_into_gh():
    assert "gh" not in convert("2018")


def test_hamza_letters_kept_as_2():
    assert convert("سؤال") == "s2l"


def test_keep_wy_variant_differs():
    assert convert("wlad", keep_wy=True) != convert("wlad", keep_wy=False)


def test_empty_and_non_string():
    assert convert("") == ""
    assert convert(None) == ""
