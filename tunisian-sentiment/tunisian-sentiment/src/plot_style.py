"""Shared plot style: fixed colors, readable defaults, Arabic text rendering.

Colors (checked for colorblind safety with a palette validator):
- Arabic script  #1f77b4 (blue)     - Arabizi  #ff7f0e (orange)
- positive       #2ca02c (green)    - negative #9467bd (purple)
Green/red was dropped for pos/neg: the two are nearly identical for
red-green colorblind viewers (deuteranopia).
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

COLORS = {
    "arabic": "#1f77b4",
    "arabizi": "#ff7f0e",
    "pos": "#2ca02c",
    "neg": "#9467bd",
}
INK = "#222222"
MUTED = "#666666"
GRID = "#e6e6e6"


def setup():
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",      # has Arabic glyphs
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlepad": 20,               # room for the grey subtitle line
        "axes.labelcolor": INK,
        "axes.edgecolor": "#bbbbbb",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "legend.frameon": False,
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def _mpl_shapes_text() -> bool:
    """matplotlib >= 3.11 ships libraqm and joins/orders Arabic by itself."""
    try:
        import matplotlib.ft2font as ft2font
        return bool(getattr(ft2font, "__libraqm_version__", ""))
    except Exception:
        return False


def ar(text: str) -> str:
    """Make Arabic text display correctly in matplotlib (joined letters, right-to-left).

    Newer matplotlib does this itself (reshaping again would reverse the word);
    older versions need arabic-reshaper + python-bidi.
    """
    if _mpl_shapes_text():
        return text
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
    except ImportError:  # in Colab: !pip install arabic-reshaper python-bidi
        return text
    return get_display(arabic_reshaper.reshape(text))


def subtitle(ax, text: str):
    """Grey line under the title (used for n = rows, data source)."""
    ax.text(0, 1.02, text, transform=ax.transAxes, fontsize=9, color=MUTED, va="bottom")


def label_bars(ax, fmt="{:.0f}", inside=False, **kw):
    """Direct value labels on top of bars (text in ink, never in the bar color)."""
    for container in ax.containers:
        ax.bar_label(container, fmt=fmt, padding=2, color=INK, fontsize=9, **kw)
