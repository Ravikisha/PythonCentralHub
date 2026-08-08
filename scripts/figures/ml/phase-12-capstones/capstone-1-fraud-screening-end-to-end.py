"""Figure for *Capstone 1 — Fraud Screening End to End*."""

import functools
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _style import Palette, figure  # noqa: E402

C_FP, C_FN = 5.0, 500.0
T_STAR = C_FP / (C_FP + C_FN)
BUDGET = 50


def _phase10():
    path = os.path.join(HERE, "..", "phase-10-applied", "_data.py")
    spec = importlib.util.spec_from_file_location("pch_phase10_data", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def setup():
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    data = _phase10()
    X, y, _ = data.fraud()
    amount = data.amounts_for(X)

    X_fit, X_rest, y_fit, y_rest, a_fit, a_rest = train_test_split(
        X, y, amount, test_size=0.5, random_state=0, stratify=y)
    _, X_te, _, y_te, _, a_te = train_test_split(
        X_rest, y_rest, a_rest, test_size=0.6, random_state=0, stratify=y_rest)

    model = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=3000)).fit(X_fit, y_fit)
    return {"proba": model.predict_proba(X_te)[:, 1], "y_te": np.asarray(y_te),
            "a_te": np.asarray(a_te), "n": len(y_te)}


def cost_of(pred, y_te, c_fn=C_FN):
    fp = int(((pred == 1) & (y_te == 0)).sum())
    missed = (pred == 0) & (y_te == 1)
    loss = (float(np.asarray(c_fn)[missed].sum()) if np.ndim(c_fn)
            else int(missed.sum()) * c_fn)
    return fp * C_FP, loss, fp, int(missed.sum())


def policies(fig, axes, p: Palette) -> None:
    """Four screening policies, priced in review cost and fraud losses."""
    d = setup()
    proba, y_te = d["proba"], d["y_te"]

    top = np.zeros(len(proba), dtype=int)
    top[np.argsort(-proba)[:BUDGET]] = 1

    rows = [
        ("do nothing", np.zeros(len(proba), dtype=int)),
        ("default 0.50", (proba >= 0.5).astype(int)),
        (f"top {BUDGET} alerts\n(capacity limit)", top),
        (f"cost-optimal\nt* = {T_STAR:.4f}", (proba >= T_STAR).astype(int)),
    ]

    review, losses, labels, notes = [], [], [], []
    for label, pred in rows:
        r, l, fp, missed = cost_of(pred, y_te)
        review.append(r)
        losses.append(l)
        labels.append(label)
        notes.append(f"EUR {r + l:,.0f}\n{int(pred.sum())} alerts, "
                     f"{missed} missed")

    idx = np.arange(len(rows))
    axes.bar(idx, review, color=p.blue, label=f"reviews ({C_FP:.0f} EUR each)")
    axes.bar(idx, losses, bottom=review, color=p.red,
             label=f"fraud that got through ({C_FN:.0f} EUR each)")
    for i, note in enumerate(notes):
        axes.annotate(note, (i, review[i] + losses[i] + 500), ha="center",
                      fontsize=9, color=p.muted)
    axes.set_xticks(idx)
    axes.set_xticklabels(labels, fontsize=9)
    axes.set_ylim(0, max(r + l for r, l in zip(review, losses)) * 1.28)
    axes.set_ylabel(f"cost over {d['n']:,} transactions (EUR)")
    best = int(np.argmin([r + l for r, l in zip(review, losses)]))
    axes.set_title(f"Cheapest policy: {labels[best]} at "
                   f"EUR {review[best] + losses[best]:,.0f} — "
                   f"EUR {(review[best] + losses[best]) / d['n']:.4f} per "
                   f"transaction".replace("\n", " "))
    axes.legend(loc="upper right", fontsize=9)


FIGURES = [
    figure("policies", policies, size=(8.4, 4.2)),
]
