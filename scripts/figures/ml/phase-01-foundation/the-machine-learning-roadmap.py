"""Figures for *The Machine Learning Roadmap*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


#: Display order and colour for each ``# @stage:`` marker in the reference
#: pipeline. Blue and amber are the data stages; green and purple are the
#: modelling and shipping stages.
STAGE_ORDER = [
    ("load", "Load + inspect the data", "data"),
    ("split", "Split before touching anything", "data"),
    ("clean", "Impute missing values", "data"),
    ("encode", "Encode + scale into a pipeline", "data"),
    ("model", "Choose the model", "model"),
    ("tune", "Cross-validate + tune", "model"),
    ("evaluate", "Evaluate against a baseline", "ship"),
    ("serve", "Persist + reload", "ship"),
]


def count_stages():
    """Count the real ``# @stage:`` lines in the reference pipeline."""
    import collections
    import re

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "_reference_pipeline.py")
    counts = collections.Counter()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            code = line.split("#")[0]
            if not code.strip():          # comment-only or blank
                continue
            if code.lstrip().startswith(("import ", "from ")):
                continue
            m = re.search(r"#\s*@stage:(\w+)", line)
            if m:
                counts[m.group(1)] += 1
    return counts


def where_the_code_goes(fig, axes, p: Palette) -> None:
    """Line counts from a complete, runnable end-to-end pipeline.

    Not a survey statistic — these are the actual code lines of
    ``_reference_pipeline.py``, the same listing printed on the page,
    tallied by the ``# @stage:`` marker each one carries.
    """
    counts = count_stages()
    palette = {"data": p.blue, "model": p.green, "ship": p.purple}

    rows = [(label, counts[key], palette[group])
            for key, label, group in STAGE_ORDER][::-1]
    total = sum(r[1] for r in rows)
    data_lines = sum(counts[k] for k, _, g in STAGE_ORDER if g == "data")

    bars = axes.barh([r[0] for r in rows], [r[1] for r in rows],
                     color=[r[2] for r in rows])
    for b, (_, v, _) in zip(bars, rows):
        axes.annotate(f"{v}  ({v / total:.0%})",
                      (v + 0.3, b.get_y() + b.get_height() / 2),
                      va="center", fontsize=9, color=p.muted)
    axes.set_xlim(0, max(r[1] for r in rows) + 6)
    axes.set_xlabel(f"lines of code (out of {total} in the reference pipeline)")
    axes.set_title(f"{data_lines} of {total} lines — {data_lines / total:.0%} — "
                   f"run before a model is chosen")


def two_tracks(fig, axes, p: Palette) -> None:
    """The same model, scored two ways: offline quality and serving latency."""
    import time

    from sklearn.datasets import load_breast_cancer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = load_breast_cancer(return_X_y=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                              random_state=0, stratify=y)

    models = [
        ("logistic", make_pipeline(StandardScaler(),
                                   LogisticRegression(max_iter=5000))),
        ("15-NN", make_pipeline(StandardScaler(), KNeighborsClassifier(15))),
        ("random forest\n(500 trees)", RandomForestClassifier(n_estimators=500,
                                                              random_state=0)),
    ]

    names, accs, sizes = [], [], []
    for name, m in models:
        accs.append(cross_val_score(m, X, y, cv=5).mean())
        m.fit(X_tr, y_tr)
        import pickle

        sizes.append(len(pickle.dumps(m)) / 1024)
        names.append(name)

    axs = fig.subplots(1, 2)
    b1 = axs[0].bar(names, accs, color=p.blue)
    for b, v in zip(b1, accs):
        axs[0].annotate(f"{v:.4f}", (b.get_x() + b.get_width() / 2, v + 0.004),
                        ha="center", fontsize=9, color=p.muted)
    axs[0].set_ylim(0.9, 1.0)
    axs[0].set_ylabel("5-fold accuracy")
    axs[0].set_title("Track A — modelling", fontsize=11)

    b2 = axs[1].bar(names, sizes, color=p.amber)
    for b, v in zip(b2, sizes):
        axs[1].annotate(f"{v:,.0f} KB",
                        (b.get_x() + b.get_width() / 2, v * 1.03),
                        ha="center", fontsize=9, color=p.muted)
    axs[1].set_yscale("log")
    axs[1].set_ylabel("pickled model size (KB, log scale)")
    axs[1].set_title("Track B — engineering", fontsize=11)
    fig.suptitle("Nearly identical accuracy; wildly different things to ship",
                 fontsize=10.5, color=p.muted)


FIGURES = [
    figure("where-the-code-goes", where_the_code_goes, size=(7.8, 4.2)),
    figure("two-tracks", two_tracks, size=(8.6, 3.8), axes=False),
]
