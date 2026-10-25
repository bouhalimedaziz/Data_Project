"""Feature builders shared by the feature-engineering notebook and the modelling phase.

Every builder is FITTED ON TRAINING ROWS ONLY and then applied to the test rows,
so no information from the test set leaks into the features.

Final feature set (justified in notebooks/05_features.ipynb):
1. TF-IDF on character n-grams (2-5, within word boundaries) of the text column
   (`text_norm` = without mapping, `text_conv` = with mapping): the main features.
2. log(1 + n_chars), standardized: the only length feature (chars and words are 95% correlated).
3. has_elongation (0/1): normalization collapses stretched letters, so the flag keeps that signal.
Deliberately excluded: script (would let a model use the script-label shortcut found by the
chi-square test), has_arabizi_digits (a proxy for script), has_emoji (absent from TUNIZI).
"""
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import StandardScaler

TFIDF_PARAMS = dict(
    analyzer="char_wb",   # character n-grams inside word boundaries
    ngram_range=(2, 5),   # 2-5 characters: sub-word pieces robust to spelling variation
    min_df=5,             # drop n-grams seen in fewer than 5 comments (typos, noise)
    max_df=0.9,           # drop n-grams in more than 90% of comments (no information)
    sublinear_tf=True,    # 1 + log(tf): a repeated n-gram doesn't dominate
    lowercase=False,      # text is already lowercased by normalize()
    dtype=np.float32,
)


def build_tfidf(train_text, test_text, k_best=None, train_labels=None, **overrides):
    """Fit TF-IDF on train_text, transform both. Optionally keep the k_best n-grams by chi-square
    (fitted on training labels only). Returns X_train, X_test, vectorizer, selector."""
    vec = TfidfVectorizer(**{**TFIDF_PARAMS, **overrides})
    X_tr = vec.fit_transform(train_text)
    X_te = vec.transform(test_text)
    sel = None
    if k_best is not None and k_best < X_tr.shape[1]:
        sel = SelectKBest(chi2, k=k_best).fit(X_tr, train_labels)
        X_tr, X_te = sel.transform(X_tr), sel.transform(X_te)
    return X_tr, X_te, vec, sel


def build_numeric(train_df, test_df):
    """log1p(n_chars) standardized (scaler fitted on train) + has_elongation as 0/1."""
    def raw(d):
        return np.column_stack([np.log1p(d["n_chars"].astype(float)),
                                d["has_elongation"].astype(str).eq("True").astype(float)])
    a_tr, a_te = raw(train_df), raw(test_df)
    scaler = StandardScaler().fit(a_tr[:, :1])
    a_tr[:, :1], a_te[:, :1] = scaler.transform(a_tr[:, :1]), scaler.transform(a_te[:, :1])
    return a_tr, a_te, scaler


def combine(X_text, X_num):
    """Text n-grams + numeric columns in one sparse matrix."""
    return sparse.hstack([X_text, sparse.csr_matrix(X_num)], format="csr")


def build_char_sequences(train_text, test_text, max_len):
    """Character-index sequences for the CNN/BiLSTM: vocabulary from train only,
    0 = padding, 1 = unknown character, sequences cut or padded to max_len."""
    chars = sorted({c for t in train_text for c in t})
    index = {c: i + 2 for i, c in enumerate(chars)}

    def encode(texts):
        out = np.zeros((len(texts), max_len), dtype=np.int32)
        for r, t in enumerate(texts):
            ids = [index.get(c, 1) for c in t[:max_len]]
            out[r, :len(ids)] = ids
        return out

    return encode(list(train_text)), encode(list(test_text)), index
