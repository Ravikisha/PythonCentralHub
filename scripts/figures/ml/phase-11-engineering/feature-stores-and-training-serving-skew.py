"""Figures for *Feature Stores and Training-Serving Skew*."""

import functools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import CUTOFF, event_log, window_features  # noqa: E402
from _style import Palette, figure  # noqa: E402

WINDOW = 30


@functools.lru_cache(maxsize=1)
def setup():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    events, future, churn = event_log()
    ids = np.arange(len(churn))
    rng = np.random.default_rng(21)
    train_mask = np.zeros(len(churn), dtype=bool)
    train_mask[rng.permutation(len(churn))[:int(0.7 * len(churn))]] = True

    correct = window_features(events, WINDOW, CUTOFF, ids)
    model = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=2000))
    model.fit(correct[train_mask], churn[train_mask])

    return {"events": events, "future": future, "churn": churn, "ids": ids,
            "train": train_mask, "correct": correct, "model": model}


def score(frame):
    """AUC and accuracy of the fitted model on a (possibly skewed) feature frame."""
    from sklearn.metrics import accuracy_score, roc_auc_score

    d = setup()
    test = ~d["train"]
    proba = d["model"].predict_proba(frame[test])[:, 1]
    return (roc_auc_score(d["churn"][test], proba),
            accuracy_score(d["churn"][test], d["model"].predict(frame[test])))


@functools.lru_cache(maxsize=1)
def skews():
    """Every serving variant, scored with the model trained on the correct one."""
    d = setup()
    events, ids = d["events"], d["ids"]
    correct = d["correct"]

    hours = correct.copy()
    hours["days_since"] = hours["days_since"] * 24
    per_day = correct.copy()
    per_day["events"] = per_day["events"] / WINDOW

    variants = {
        "point-in-time (correct)": correct,
        "cache 3 days stale": window_features(events, WINDOW,
                                              CUTOFF - pd.Timedelta(days=3), ids),
        "cache 7 days stale": window_features(events, WINDOW,
                                              CUTOFF - pd.Timedelta(days=7), ids),
        "7-day window, not 30": window_features(events, 7, CUTOFF, ids),
        "90-day window, not 30": window_features(events, 90, CUTOFF, ids),
        "days_since in hours": hours,
        "events per day, not per window": per_day,
    }
    return {name: score(frame) for name, frame in variants.items()}


def skew_table(fig, axes, p: Palette) -> None:
    """Seven serving implementations of the same three features."""
    results = skews()
    names = list(results)
    aucs = [results[n][0] for n in names]
    accs = [results[n][1] for n in names]
    base_auc, base_acc = results[names[0]]

    idx = np.arange(len(names))
    axes.barh(idx + 0.2, aucs, 0.36, color=p.blue, label="AUC")
    axes.barh(idx - 0.2, accs, 0.36, color=p.amber, label="accuracy")
    for i, n in enumerate(names):
        axes.annotate(f"{aucs[i]:.4f}", (aucs[i] + 0.006, i + 0.2), va="center",
                      fontsize=8.5, color=p.blue)
        axes.annotate(f"{accs[i]:.4f}", (accs[i] + 0.006, i - 0.2), va="center",
                      fontsize=8.5, color=p.amber)
    axes.axvline(base_auc, color=p.blue, lw=1, ls="--", alpha=0.6)
    axes.axvline(base_acc, color=p.amber, lw=1, ls="--", alpha=0.6)
    axes.set_yticks(idx)
    axes.set_yticklabels(names, fontsize=9)
    axes.set_xlim(0, 0.92)
    axes.set_xlabel("score on the same test customers")
    worst = min(accs)
    axes.set_title(f"One trained model, seven serving paths: accuracy "
                   f"{base_acc:.4f} down to {worst:.4f}")
    axes.legend(loc="lower right", fontsize=9)


def point_in_time(fig, axes, p: Palette) -> None:
    """A window that ends after the label period is not a feature."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    d = setup()
    ids, churn, train = d["ids"], d["churn"], d["train"]
    everything = pd.concat([d["events"], d["future"]], ignore_index=True)

    rows = []
    for label, frame in (
        ("point-in-time\n(window ends at the cutoff)", d["correct"]),
        ("window ends 30 days late\n(includes the label period)",
         window_features(everything, WINDOW, CUTOFF + pd.Timedelta(days=30), ids)),
    ):
        model = make_pipeline(StandardScaler(),
                              LogisticRegression(max_iter=2000))
        model.fit(frame[train], churn[train])
        auc = roc_auc_score(churn[~train],
                            model.predict_proba(frame[~train])[:, 1])
        rows.append((label, auc))

    axs = fig.subplots(1, 2, width_ratios=[1.25, 1])

    # a timeline of what each window sees
    axs[0].axvspan(-30, 0, color=p.blue, alpha=0.18)
    axs[0].axvspan(0, 30, color=p.red, alpha=0.18)
    axs[0].axvline(0, color=p.amber, lw=2)
    axs[0].annotate("cutoff", (0.6, 1.72), fontsize=9.5, color=p.amber)
    axs[0].annotate("features may use this", (-29, 1.72), fontsize=9.5,
                    color=p.blue)
    axs[0].annotate("the label lives here", (1.5, 1.35), fontsize=9.5,
                    color=p.red)
    axs[0].plot([-30, 0], [1.0, 1.0], color=p.blue, lw=6, solid_capstyle="butt")
    axs[0].annotate("correct window", (-29, 0.86), fontsize=9, color=p.blue)
    axs[0].plot([0, 30], [0.45, 0.45], color=p.red, lw=6, solid_capstyle="butt")
    axs[0].plot([-30, 0], [0.45, 0.45], color=p.red, lw=6, alpha=0.5,
                solid_capstyle="butt")
    axs[0].annotate("window that ends 30 days late", (-29, 0.31), fontsize=9,
                    color=p.red)
    axs[0].set_xlim(-32, 32)
    axs[0].set_ylim(0, 2)
    axs[0].set_yticks([])
    axs[0].set_xlabel("days relative to the cutoff")
    axs[0].grid(False)
    axs[0].set_title("What each window is allowed to see", fontsize=10.5)

    positions = np.arange(len(rows))
    axs[1].bar(positions, [r[1] for r in rows], color=[p.blue, p.red], width=0.5)
    for i, r in enumerate(rows):
        axs[1].annotate(f"{r[1]:.4f}", (i, r[1] + 0.015), ha="center",
                        fontsize=10.5, color=p.muted)
    axs[1].set_xticks(positions)
    axs[1].set_xticklabels([r[0] for r in rows], fontsize=8.5)
    axs[1].set_ylim(0, 1.12)
    axs[1].set_ylabel("test AUC")
    axs[1].set_title(f"{rows[1][1] - rows[0][1]:+.4f} of pure leakage",
                     fontsize=10.5)

    fig.suptitle("Both frames are computed by the same function. Only the `asof` "
                 "argument differs.", fontsize=10.5, color=p.muted)


def parity_check(fig, axes, p: Palette) -> None:
    """The test that catches skew before production does."""
    d = setup()
    events, ids = d["events"], d["ids"]
    correct = d["correct"]

    variants = {
        "same function, same args": correct,
        "cache 3 days stale": window_features(events, WINDOW,
                                              CUTOFF - pd.Timedelta(days=3), ids),
        "7-day window": window_features(events, 7, CUTOFF, ids),
        "events per day": None,
    }
    per_day = correct.copy()
    per_day["events"] = per_day["events"] / WINDOW
    variants["events per day"] = per_day

    labels, mismatch, max_diff = [], [], []
    for name, frame in variants.items():
        differs = ~np.isclose(frame.to_numpy(dtype=float),
                              correct.to_numpy(dtype=float), rtol=1e-9,
                              atol=1e-9)
        labels.append(name)
        mismatch.append(differs.any(axis=1).mean())
        max_diff.append(float(np.abs(frame.to_numpy(dtype=float)
                                     - correct.to_numpy(dtype=float)).max()))

    idx = np.arange(len(labels))
    colours = [p.green if m == 0 else p.red for m in mismatch]
    axes.bar(idx, mismatch, color=colours, width=0.5)
    for i, m in enumerate(mismatch):
        axes.annotate(f"{m:.1%} of rows differ\nmax |diff| {max_diff[i]:.3f}",
                      (i, m + 0.03), ha="center", fontsize=9, color=colours[i])
    axes.set_xticks(idx)
    axes.set_xticklabels(labels, fontsize=9)
    axes.set_ylim(0, 1.28)
    axes.set_ylabel("fraction of customers whose features differ")
    axes.set_title("A parity test compares the two paths row by row, before any "
                   "model is involved")


FIGURES = [
    figure("skew-table", skew_table, size=(8.6, 4.2)),
    figure("point-in-time", point_in_time, size=(8.8, 3.9), axes=False),
    figure("parity-check", parity_check, size=(8.2, 4.0)),
]
