"""Figures for *Imbalanced Classification and Fraud Detection*."""

import functools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import fraud, smote, undersample  # noqa: E402
from _style import Palette, figure  # noqa: E402


@functools.lru_cache(maxsize=1)
def setup():
    """Fit the four strategies once and reuse across figures and both themes."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y, p_true = fraud()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                              random_state=0, stratify=y)
    A_tr, A_te = X_tr.to_numpy(), X_te.to_numpy()

    def fit(fit_X, fit_y, weight=None):
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, class_weight=weight))
        model.fit(fit_X, fit_y)
        return model.predict_proba(A_te)[:, 1]

    X_sm, y_sm = smote(A_tr, y_tr, seed=1)
    X_us, y_us = undersample(A_tr, y_tr, seed=1)

    scores = {
        "nothing": fit(A_tr, y_tr),
        "class_weight\nbalanced": fit(A_tr, y_tr, "balanced"),
        "SMOTE\n1:1": fit(X_sm, y_sm),
        "random\nundersample": fit(X_us, y_us),
    }
    return {
        "y_test": np.asarray(y_te),
        "scores": scores,
        "oracle": np.asarray(p_true[X_te.index]),
        "n_train": (len(y_tr), len(y_sm), len(y_us)),
    }


@functools.lru_cache(maxsize=1)
def bootstrap_ap(n_boot=2000):
    """Percentile CI for average precision, resampling the test rows."""
    from sklearn.metrics import average_precision_score

    d = setup()
    y_te, rng = d["y_test"], np.random.default_rng(0)
    out = {k: [] for k in d["scores"]}
    for _ in range(n_boot):
        idx = rng.integers(0, len(y_te), len(y_te))
        yy = y_te[idx]
        if yy.sum() == 0:
            continue
        for name, pr in d["scores"].items():
            out[name].append(average_precision_score(yy, pr[idx]))
    return {k: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))
            for k, v in out.items()}


def accuracy_paradox(fig, axes, p: Palette) -> None:
    """Accuracy improves by 0.0005 while the useful work goes from 0 to 5."""
    d = setup()
    y_te = d["y_test"]
    proba = d["scores"]["nothing"]

    nothing = np.zeros_like(y_te)
    at_half = (proba >= 0.5).astype(int)
    accs = [(nothing == y_te).mean(), (at_half == y_te).mean()]
    caught = [0, int(((at_half == 1) & (y_te == 1)).sum())]
    total = int(y_te.sum())
    labels = ["predict\n'never fraud'", "logistic at 0.50"]

    axs = fig.subplots(1, 2)
    idx = np.arange(2)

    bars = axs[0].bar(idx, accs, color=[p.red, p.blue], width=0.55)
    for b, v in zip(bars, accs):
        axs[0].annotate(f"{v:.4f}", (b.get_x() + b.get_width() / 2, v + 0.00004),
                        ha="center", fontsize=10, color=p.muted)
    axs[0].set_xticks(idx)
    axs[0].set_xticklabels(labels, fontsize=9.5)
    axs[0].set_ylim(0.994, 0.9968)
    axs[0].set_ylabel("accuracy")
    axs[0].set_title(f"Accuracy: a {accs[1] - accs[0]:.4f} difference",
                     fontsize=10.5)

    bars = axs[1].bar(idx, caught, color=[p.red, p.blue], width=0.55)
    for b, v in zip(bars, caught):
        axs[1].annotate(f"{v} of {total}",
                        (b.get_x() + b.get_width() / 2, v + 0.4),
                        ha="center", fontsize=10, color=p.muted)
    axs[1].axhline(total, color=p.amber, lw=1.4, ls="--",
                   label=f"{total} frauds in the test set")
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels(labels, fontsize=9.5)
    axs[1].set_ylim(0, total * 1.25)
    axs[1].set_ylabel("frauds caught")
    axs[1].set_title("Frauds caught: 0 against 5", fontsize=10.5)
    axs[1].legend(loc="upper left", fontsize=8.5)

    fig.suptitle("The same two models, scored two ways. Only one of the scores "
                 "is about the job.", fontsize=10.5, color=p.muted)


def roc_versus_pr(fig, axes, p: Palette) -> None:
    """ROC-AUC 0.9848 and average precision 0.4561, on identical predictions."""
    from sklearn.metrics import (average_precision_score,
                                 precision_recall_curve, roc_auc_score,
                                 roc_curve)

    d = setup()
    y_te = d["y_test"]
    proba = d["scores"]["nothing"]

    axs = fig.subplots(1, 2)

    fpr, tpr, _ = roc_curve(y_te, proba)
    axs[0].plot(fpr, tpr, color=p.blue, lw=2.4)
    axs[0].plot([0, 1], [0, 1], color=p.muted, lw=1, ls="--")
    axs[0].set_xlabel("false positive rate")
    axs[0].set_ylabel("true positive rate")
    axs[0].set_title(f"ROC — AUC {roc_auc_score(y_te, proba):.4f}", fontsize=10.5)
    axs[0].annotate("'this model is excellent'", (0.42, 0.35), fontsize=9.5,
                    color=p.muted)

    prec, rec, _ = precision_recall_curve(y_te, proba)
    ap = average_precision_score(y_te, proba)
    axs[1].plot(rec, prec, color=p.amber, lw=2.4)
    axs[1].axhline(y_te.mean(), color=p.red, lw=1.2, ls="--",
                   label=f"chance = base rate {y_te.mean():.4f}")
    axs[1].set_xlabel("recall")
    axs[1].set_ylabel("precision")
    axs[1].set_ylim(0, 1.02)
    axs[1].set_title(f"Precision-recall — AP {ap:.4f}", fontsize=10.5)
    axs[1].annotate("'and here is the actual\noperating problem'",
                    (0.04, 0.22), fontsize=9.5, color=p.muted)
    axs[1].legend(loc="upper right", fontsize=8.5)

    fig.suptitle("One set of predictions. The left panel divides by the 5,974 "
                 "negatives; the right one does not.",
                 fontsize=10.5, color=p.muted)


def threshold_sweep(fig, axes, p: Palette) -> None:
    """Every recall target has a price, and it is quoted in alerts per day."""
    from sklearn.metrics import precision_recall_curve

    d = setup()
    y_te = d["y_test"]
    proba = d["scores"]["nothing"]
    prec, rec, thr = precision_recall_curve(y_te, proba)

    axs = fig.subplots(1, 2)

    axs[0].plot(thr, prec[:-1], color=p.blue, lw=2.2, label="precision")
    axs[0].plot(thr, rec[:-1], color=p.amber, lw=2.2, label="recall")
    f1 = 2 * prec[:-1] * rec[:-1] / np.maximum(prec[:-1] + rec[:-1], 1e-12)
    axs[0].plot(thr, f1, color=p.green, lw=1.6, ls="--", label="F1")
    best = int(np.argmax(f1))
    axs[0].scatter([thr[best]], [f1[best]], color=p.green, zorder=5, s=45)
    axs[0].annotate(f"best F1 {f1[best]:.4f} at {thr[best]:.3f}",
                    (1.5e-4, 0.72), fontsize=9, color=p.green)
    axs[0].set_xscale("log")
    axs[0].set_xlim(1e-4, 1.2)
    axs[0].set_xlabel("threshold (log scale)")
    axs[0].set_ylim(0, 1.05)
    axs[0].set_title("Precision and recall trade along the threshold",
                     fontsize=10.5)
    axs[0].legend(loc="center left", fontsize=8.5)

    targets = [0.50, 0.70, 0.90]
    rows = []
    for t in targets:
        ok = np.flatnonzero(rec[:-1] >= t)
        i = int(ok[-1])
        alerts = int((proba >= thr[i]).sum())
        rows.append((t, thr[i], prec[i], rec[i], alerts))

    idx = np.arange(len(rows))
    axs[1].bar(idx, [r[4] for r in rows], color=p.red, width=0.55)
    for i, r in enumerate(rows):
        axs[1].annotate(f"{r[4]} alerts\nprecision {r[2]:.3f}",
                        (i, r[4] + 8), ha="center", fontsize=9, color=p.muted)
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels([f"recall\n{r[3]:.2f}" for r in rows], fontsize=9.5)
    axs[1].set_ylim(0, max(r[4] for r in rows) * 1.45)
    axs[1].set_ylabel("rows sent to a human")
    axs[1].set_title(f"To catch 24 of {int(y_te.sum())}, review 232 rows",
                     fontsize=10.5)

    fig.suptitle("The threshold is the product decision. Nothing about "
                 "training changes this curve.",
                 fontsize=10.5, color=p.muted)


def resampling_scorecard(fig, axes, p: Palette) -> None:
    """Four strategies, one indistinguishable AP, four very different Briers."""
    from sklearn.metrics import average_precision_score, brier_score_loss

    d = setup()
    y_te = d["y_test"]
    cis = bootstrap_ap()

    names = list(d["scores"])
    ap = [average_precision_score(y_te, d["scores"][n]) for n in names]
    lo = [ap[i] - cis[n][0] for i, n in enumerate(names)]
    hi = [cis[n][1] - ap[i] for i, n in enumerate(names)]
    brier = [brier_score_loss(y_te, d["scores"][n]) for n in names]
    mean_pred = [d["scores"][n].mean() for n in names]
    oracle = average_precision_score(y_te, d["oracle"])

    axs = fig.subplots(1, 2)
    idx = np.arange(len(names))

    axs[0].bar(idx, ap, yerr=[lo, hi], color=p.blue, width=0.55,
               error_kw={"ecolor": p.muted, "lw": 1.4, "capsize": 5})
    for i, name in enumerate(names):
        axs[0].annotate(f"{ap[i]:.4f}", (i, cis[name][1] + 0.02), ha="center",
                        fontsize=9, color=p.muted)
    axs[0].axhline(oracle, color=p.green, lw=1.4, ls="--",
                   label=f"oracle (true probabilities) {oracle:.4f}")
    axs[0].set_xticks(idx)
    axs[0].set_xticklabels([n.replace("\n", " ") for n in names], fontsize=8,
                           rotation=20, ha="right")
    axs[0].set_ylim(0, 0.75)
    axs[0].set_ylabel("average precision")
    axs[0].set_title("Ranking quality: identical, within a wide CI",
                     fontsize=10.5)
    axs[0].legend(loc="upper left", fontsize=8)

    axs[1].bar(idx, mean_pred, color=p.amber, width=0.55)
    for i, (m, b) in enumerate(zip(mean_pred, brier)):
        axs[1].annotate(f"{m:.4f}\nBrier {b:.4f}", (i, m + 0.004), ha="center",
                        fontsize=8.5, color=p.muted)
    axs[1].axhline(y_te.mean(), color=p.red, lw=1.4, ls="--",
                   label=f"true fraud rate {y_te.mean():.4f}")
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels([n.replace("\n", " ") for n in names], fontsize=8,
                           rotation=20, ha="right")
    axs[1].set_ylim(0, 0.165)
    axs[1].set_ylabel("mean predicted probability")
    axs[1].set_title("Calibration: destroyed by every resampler",
                     fontsize=10.5)
    axs[1].legend(loc="upper left", fontsize=8)

    fig.suptitle("Resampling did not improve the ranking. It did multiply every "
                 "predicted probability.", fontsize=10.5, color=p.muted)


def resample_before_split(fig, axes, p: Palette) -> None:
    """The 0.9879 that comes from scoring synthetic rows."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import average_precision_score
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y, _ = fraud()
    d = setup()

    X_all, y_all = smote(X.to_numpy(), y, seed=2)      # WRONG: before the split
    Xa_tr, Xa_te, ya_tr, ya_te = train_test_split(
        X_all, y_all, test_size=0.3, random_state=0, stratify=y_all)
    leaky = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=2000)).fit(Xa_tr, ya_tr)

    _, X_te, _, y_te = train_test_split(X, y, test_size=0.3, random_state=0,
                                        stratify=y)
    bars = [
        ("resample, then split\nscored on synthetic rows",
         average_precision_score(ya_te, leaky.predict_proba(Xa_te)[:, 1]), p.red),
        ("the same model\non the real test set",
         average_precision_score(y_te, leaky.predict_proba(X_te.to_numpy())[:, 1]),
         p.amber),
        ("resample inside training\nonly (correct)",
         average_precision_score(np.asarray(y_te), d["scores"]["SMOTE\n1:1"]),
         p.green),
    ]

    idx = np.arange(len(bars))
    axes.bar(idx, [b[1] for b in bars], color=[b[2] for b in bars], width=0.5)
    for i, b in enumerate(bars):
        axes.annotate(f"{b[1]:.4f}", (i, b[1] + 0.02), ha="center", fontsize=10.5,
                      color=p.muted)
    axes.set_xticks(idx)
    axes.set_xticklabels([b[0] for b in bars], fontsize=9)
    axes.set_ylim(0, 1.12)
    axes.set_ylabel("average precision")
    axes.set_title("Synthetic minority rows leak across the split, and the "
                   "score doubles")


FIGURES = [
    figure("accuracy-paradox", accuracy_paradox, size=(8.6, 3.6), axes=False),
    figure("roc-versus-pr", roc_versus_pr, size=(8.6, 3.8), axes=False),
    figure("threshold-sweep", threshold_sweep, size=(8.8, 3.8), axes=False),
    figure("resampling-scorecard", resampling_scorecard, size=(8.8, 4.0),
           axes=False),
    figure("resample-before-split", resample_before_split, size=(7.6, 3.8)),
]
