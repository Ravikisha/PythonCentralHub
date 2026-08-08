"""Figures for *Experiment Tracking and Reproducibility*."""

import functools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import tabular  # noqa: E402
from _style import Palette, figure  # noqa: E402


def _forest(seed=0, **kwargs):
    from sklearn.ensemble import RandomForestClassifier
    return RandomForestClassifier(n_estimators=200, random_state=seed, **kwargs)


@functools.lru_cache(maxsize=1)
def seed_spread(n_seeds=30):
    """Accuracy across split seeds and across model seeds, separately."""
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split

    X, y = tabular()
    by_split, by_model = [], []

    for s in range(n_seeds):
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                                  random_state=s, stratify=y)
        by_split.append(accuracy_score(y_te, _forest(0).fit(X_tr, y_tr)
                                       .predict(X_te)))

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                              random_state=0, stratify=y)
    for s in range(n_seeds):
        by_model.append(accuracy_score(y_te, _forest(s).fit(X_tr, y_tr)
                                       .predict(X_te)))

    return np.array(by_split), np.array(by_model)


@functools.lru_cache(maxsize=1)
def candidates(n=20):
    """Twenty near-identical configurations, scored on validation and on test."""
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split

    X, y = tabular()
    X_fit, X_rest, y_fit, y_rest = train_test_split(X, y, test_size=0.4,
                                                    random_state=0, stratify=y)
    X_val, X_te, y_val, y_te = train_test_split(X_rest, y_rest, test_size=0.5,
                                                random_state=0, stratify=y_rest)

    val, test = [], []
    for s in range(n):
        model = _forest(s, max_features=None if s % 4 == 0 else "sqrt",
                        min_samples_leaf=1 + (s % 5)).fit(X_fit, y_fit)
        val.append(accuracy_score(y_val, model.predict(X_val)))
        test.append(accuracy_score(y_te, model.predict(X_te)))
    return np.array(val), np.array(test), len(y_val), len(y_te)


@functools.lru_cache(maxsize=1)
def paired_difference(n_splits=15):
    """The same two configurations, compared on identical splits."""
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split

    X, y = tabular()
    a, b = [], []
    for s in range(n_splits):
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                                  random_state=100 + s,
                                                  stratify=y)
        a.append(accuracy_score(y_te, _forest(0, min_samples_leaf=1)
                                .fit(X_tr, y_tr).predict(X_te)))
        b.append(accuracy_score(y_te, _forest(0, min_samples_leaf=5)
                                .fit(X_tr, y_tr).predict(X_te)))
    return np.array(a), np.array(b)


def seeds(fig, axes, p: Palette) -> None:
    """One reported number, thirty possible values."""
    by_split, by_model = seed_spread()

    axs = fig.subplots(1, 2, sharey=True)

    for ax, values, name, colour in ((axs[0], by_split, "split seed", p.blue),
                                     (axs[1], by_model, "model seed", p.amber)):
        jitter = np.linspace(-0.25, 0.25, len(values))
        ax.scatter(jitter, values, s=34, color=colour, alpha=0.85)
        ax.axhline(values.mean(), color=p.muted, lw=1.2, ls="--")
        ax.annotate(f"mean {values.mean():.4f}", (0.28, values.mean()),
                    fontsize=9, color=p.muted, va="center")
        ax.annotate(f"range {values.max() - values.min():.4f}\n"
                    f"sd {values.std(ddof=1):.4f}",
                    (-0.44, values.max()), fontsize=9.5, color=colour, va="top")
        ax.set_xlim(-0.5, 0.6)
        ax.set_xticks([])
        ax.set_title(f"varying only the {name}", fontsize=10.5)

    axs[0].set_ylabel("test accuracy")
    fig.suptitle("Same data, same code: the split seed moves accuracy by 0.0300 "
                 "and the model seed by 0.0092.",
                 fontsize=10.5, color=p.muted)


def winners_curse(fig, axes, p: Palette) -> None:
    """Selecting the best of twenty on a small validation set selects noise."""
    val, test, n_val, n_te = candidates()
    best = int(np.argmax(val))
    best_test = int(np.argmax(test))

    axes.scatter(val, test, s=48, color=p.blue, alpha=0.85, label="candidate")
    axes.scatter([val[best]], [test[best]], s=150, facecolor="none",
                 edgecolor=p.red, lw=2.2,
                 label=f"chosen on validation ({val[best]:.4f} -> "
                       f"{test[best]:.4f})")
    axes.scatter([val[best_test]], [test[best_test]], s=150, facecolor="none",
                 edgecolor=p.green, lw=2.2,
                 label=f"actually best on test ({test[best_test]:.4f})")

    lo = min(val.min(), test.min()) - 0.004
    hi = max(val.max(), test.max()) + 0.004
    axes.plot([lo, hi], [lo, hi], color=p.muted, lw=1, ls="--",
              label="validation = test")
    axes.set_xlim(lo, hi)
    axes.set_ylim(lo, hi)
    axes.set_xlabel(f"validation accuracy ({n_val} rows)")
    axes.set_ylabel(f"test accuracy ({n_te} rows)")
    corr = float(np.corrcoef(val, test)[0, 1])
    axes.set_title(f"20 candidates, validation-test correlation {corr:+.4f}")
    axes.legend(loc="lower left", fontsize=8.5)


def paired_versus_unpaired(fig, axes, p: Palette) -> None:
    """The same effect is invisible unpaired and obvious paired."""
    a, b = paired_difference()
    diff = a - b
    val, test, n_val, _ = candidates()

    axs = fig.subplots(1, 2, width_ratios=[1.1, 1])

    idx = np.arange(len(a))
    axs[0].plot(idx, a, "o-", color=p.blue, lw=1.6, label="min_samples_leaf=1")
    axs[0].plot(idx, b, "o-", color=p.amber, lw=1.6, label="min_samples_leaf=5")
    for i in idx:
        axs[0].plot([i, i], [b[i], a[i]], color=p.muted, lw=0.8)
    axs[0].set_xlabel("split (same data, 15 different partitions)")
    axs[0].set_ylabel("test accuracy")
    axs[0].set_title(f"Both configurations swing by {max(a.max() - a.min(), b.max() - b.min()):.4f} "
                     f"across splits", fontsize=10.5)
    axs[0].legend(loc="lower left", fontsize=8.5)

    se = np.sqrt(0.906 * (1 - 0.906) / n_val)
    bars = [
        ("one split,\nunpaired\n(95% CI)", 1.96 * np.sqrt(2) * se, p.red),
        ("15 splits,\npaired\n(95% CI of the mean)",
         2.145 * diff.std(ddof=1) / np.sqrt(len(diff)), p.green),
    ]
    positions = np.arange(len(bars))
    axs[1].bar(positions, [bb[1] for bb in bars], color=[bb[2] for bb in bars],
               width=0.5)
    for i, bb in enumerate(bars):
        axs[1].annotate(f"±{bb[1]:.4f}", (i, bb[1] + 0.0009), ha="center",
                        fontsize=10, color=bb[2])
    axs[1].axhline(abs(diff.mean()), color=p.blue, lw=1.6, ls="--",
                   label=f"the real effect: {diff.mean():+.4f}")
    axs[1].set_xticks(positions)
    axs[1].set_xticklabels([bb[0] for bb in bars], fontsize=9)
    axs[1].set_ylim(0, max(bb[1] for bb in bars) * 1.25)
    axs[1].set_ylabel("resolvable difference in accuracy")
    axs[1].set_title(f"Paired t = {diff.mean() / (diff.std(ddof=1) / np.sqrt(len(diff))):+.2f}, "
                     f"{int((diff > 0).sum())} of {len(diff)} wins", fontsize=10.5)
    axs[1].legend(loc="upper right", fontsize=8.5)

    fig.suptitle("A 0.0059 improvement needs 26,000 unpaired rows — or four "
                 "paired splits.", fontsize=10.5, color=p.muted)


FIGURES = [
    figure("seed-spread", seeds, size=(8.4, 3.8), axes=False),
    figure("winners-curse", winners_curse, size=(7.8, 4.4)),
    figure("paired-versus-unpaired", paired_versus_unpaired, size=(8.8, 3.9),
           axes=False),
]
