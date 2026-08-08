"""Figures for *Saving and Loading Models (Pickle, Joblib)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import breast_cancer_split  # noqa: E402
from _style import Palette, figure  # noqa: E402


def pipeline_vs_bare(fig, axes, p: Palette) -> None:
    """Saving the estimator without its preprocessing is a silent catastrophe."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X_tr, X_te, y_tr, y_te = breast_cancer_split()

    scaler = StandardScaler().fit(X_tr)
    bare = LogisticRegression(max_iter=5000).fit(scaler.transform(X_tr), y_tr)
    pipe = make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=5000)).fit(X_tr, y_tr)

    rows = [
        ("Saved the whole Pipeline\npredict(raw X)",
         accuracy_score(y_te, pipe.predict(X_te)), p.green),
        ("Saved only the estimator\npredict(scaled X) — correct",
         accuracy_score(y_te, bare.predict(scaler.transform(X_te))), p.blue),
        ("Saved only the estimator\npredict(raw X) — the bug",
         accuracy_score(y_te, bare.predict(X_te)), p.red),
    ]

    bars = axes.barh([r[0] for r in rows][::-1], [r[1] for r in rows][::-1],
                     color=[r[2] for r in rows][::-1])
    for b, (_, v, _) in zip(bars, rows[::-1]):
        axes.annotate(f"{v:.4f}", (v + 0.012, b.get_y() + b.get_height() / 2),
                      va="center", fontsize=10, color=p.fg)
    axes.axvline(0.5, color=p.muted, ls="--", lw=1.3)
    axes.annotate("coin flip", (0.51, -0.42), color=p.muted, fontsize=9)
    axes.set_xlim(0, 1.12)
    axes.set_xlabel("test accuracy")
    axes.set_title("Forgetting the scaler costs 0.5848 — and raises no error")


def format_and_compression(fig, axes, p: Palette) -> None:
    """Artefact size by format and compression level — all stable, all on disk."""
    import pickle
    import tempfile

    import joblib
    from sklearn.ensemble import (HistGradientBoostingClassifier,
                                  RandomForestClassifier)
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X_tr, X_te, y_tr, y_te = breast_cancer_split()
    tmp = tempfile.mkdtemp()

    models = [
        ("logistic", make_pipeline(StandardScaler(),
                                   LogisticRegression(max_iter=5000))),
        ("15-NN", make_pipeline(StandardScaler(), KNeighborsClassifier(15))),
        ("boosting", HistGradientBoostingClassifier(random_state=0)),
        ("forest, 500", RandomForestClassifier(n_estimators=500, random_state=0)),
    ]

    axs = fig.subplots(1, 2)

    names, pk, jb = [], [], []
    for name, m in models:
        m.fit(X_tr, y_tr)
        pp = os.path.join(tmp, f"{name}.pkl")
        jp = os.path.join(tmp, f"{name}.joblib")
        with open(pp, "wb") as fh:
            pickle.dump(m, fh)
        joblib.dump(m, jp)
        names.append(name)
        pk.append(os.path.getsize(pp) / 1024)
        jb.append(os.path.getsize(jp) / 1024)

    x = np.arange(len(names))
    axs[0].bar(x - 0.2, pk, 0.4, color=p.blue, label="pickle")
    axs[0].bar(x + 0.2, jb, 0.4, color=p.amber, label="joblib (default)")
    for xi, v in zip(x, jb):
        axs[0].annotate(f"{v:,.0f}", (xi + 0.2, v * 1.15), ha="center",
                        fontsize=8.5, color=p.muted)
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(names, rotation=20, ha="right")
    axs[0].set_yscale("log")
    axs[0].set_ylabel("artefact size, KB (log scale)")
    axs[0].set_title("Format barely matters", fontsize=11)
    axs[0].legend(fontsize=9)

    forest = models[-1][1]
    levels = [0, 1, 3, 6, 9]
    sizes = []
    for c in levels:
        cp = os.path.join(tmp, f"c{c}.joblib")
        joblib.dump(forest, cp, compress=c)
        sizes.append(os.path.getsize(cp) / 1024)
    bars = axs[1].bar([str(c) for c in levels], sizes, color=p.green)
    for b, v in zip(bars, sizes):
        axs[1].annotate(f"{v:,.0f}", (b.get_x() + b.get_width() / 2, v + 30),
                        ha="center", fontsize=9, color=p.muted)
    axs[1].set_xlabel("joblib compress level")
    axs[1].set_ylabel("size, KB")
    axs[1].set_title(f"compress=3 is {sizes[0] / sizes[2]:.1f}x smaller",
                     fontsize=11)


FIGURES = [
    figure("pipeline-vs-bare", pipeline_vs_bare, size=(8.0, 3.4)),
    figure("format-and-compression", format_and_compression, size=(9.0, 3.8),
           axes=False),
]
