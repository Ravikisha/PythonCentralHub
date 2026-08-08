"""Figures for *Anomaly Detection with Isolation Forests*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import contaminated  # noqa: E402
from _style import Palette, figure  # noqa: E402


def path_lengths(fig, axes, p: Palette) -> None:
    """Isolating an outlier takes few random cuts; a dense point takes many."""
    X, y = contaminated(seed=3)

    rng = np.random.default_rng(0)

    def isolate(point, data, depth_limit=30):
        """One isolation tree, followed only down the branch holding `point`."""
        lo = data.min(0).astype(float)
        hi = data.max(0).astype(float)
        cur = data
        for depth in range(depth_limit):
            if len(cur) <= 1:
                return depth
            f = rng.integers(0, 2)
            if hi[f] - lo[f] < 1e-9:
                return depth
            cut = rng.uniform(lo[f], hi[f])
            if point[f] < cut:
                cur = cur[cur[:, f] < cut]
                hi[f] = cut
            else:
                cur = cur[cur[:, f] >= cut]
                lo[f] = cut
        return depth_limit

    depths = np.array([np.mean([isolate(x, X) for _ in range(60)]) for x in X])

    axs = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.1]})
    sc = axs[0].scatter(X[:, 0], X[:, 1], c=depths, cmap="viridis_r", s=18)
    axs[0].set_title("Mean isolation depth over 60 random trees", fontsize=10)
    axs[0].set_xticks([])
    axs[0].set_yticks([])
    fig.colorbar(sc, ax=axs[0], fraction=0.046).ax.tick_params(colors=p.muted)

    axs[1].hist(depths[y == 1], bins=18, color=p.blue, alpha=0.85, label="inliers")
    axs[1].hist(depths[y == -1], bins=18, color=p.red, alpha=0.85, label="outliers")
    axs[1].set_xlabel("mean depth to isolation")
    axs[1].set_ylabel("count")
    axs[1].set_title(f"Outliers isolate at depth {depths[y == -1].mean():.1f}; "
                     f"inliers at {depths[y == 1].mean():.1f}", fontsize=10)
    axs[1].legend()


def score_surface(fig, axes, p: Palette) -> None:
    """The learned anomaly-score contour and the decision boundary on it."""
    from sklearn.ensemble import IsolationForest

    X, y = contaminated(seed=3)
    clf = IsolationForest(contamination=0.07, random_state=0).fit(X)

    xx, yy = np.meshgrid(np.linspace(-6, 6, 300), np.linspace(-6, 6, 300))
    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    cs = axes.contourf(xx, yy, Z, levels=18, cmap="RdBu")
    axes.contour(xx, yy, Z, levels=[0], colors=[p.fg], linewidths=2)
    pred = clf.predict(X)
    axes.scatter(X[pred == 1, 0], X[pred == 1, 1], s=16, c=p.fg, alpha=0.6,
                 edgecolors="none", label="predicted inlier")
    axes.scatter(X[pred == -1, 0], X[pred == -1, 1], s=48, marker="X",
                 c=p.amber, edgecolors="black", linewidths=0.5,
                 label="flagged anomaly")
    axes.legend(loc="upper left")
    axes.set_title("decision_function: positive inside, negative outside; "
                   "the thick line is 0")
    axes.set_xticks([])
    axes.set_yticks([])
    axes.grid(False)
    fig.colorbar(cs, ax=axes, fraction=0.046).ax.tick_params(colors=p.muted)


def contamination_sweep(fig, axes, p: Palette) -> None:
    """contamination sets the threshold, not the model — precision/recall trade."""
    from sklearn.ensemble import IsolationForest
    from sklearn.metrics import precision_score, recall_score

    X, y = contaminated(n_inliers=280, n_outliers=20, seed=3)
    truth = (y == -1).astype(int)

    rates = [0.01, 0.02, 0.04, 0.0667, 0.10, 0.15, 0.20, 0.30]
    prec, rec, flagged = [], [], []
    for r in rates:
        pred = IsolationForest(contamination=r, random_state=0).fit_predict(X)
        hit = (pred == -1).astype(int)
        prec.append(precision_score(truth, hit, zero_division=0))
        rec.append(recall_score(truth, hit))
        flagged.append(int(hit.sum()))

    axs = fig.subplots(1, 2)
    axs[0].plot(rates, prec, "o-", color=p.blue, label="precision")
    axs[0].plot(rates, rec, "o-", color=p.amber, label="recall")
    axs[0].axvline(20 / 300, color=p.green, ls="--", lw=1.4,
                   label="true rate 6.7%")
    axs[0].set_xlabel("contamination")
    axs[0].set_ylabel("score")
    axs[0].set_title("Setting it right matters more than tuning trees")
    axs[0].legend()

    axs[1].bar([f"{r:.0%}" for r in rates], flagged, color=p.purple)
    axs[1].axhline(20, color=p.green, ls="--", lw=1.4, label="20 real outliers")
    axs[1].set_ylabel("points flagged")
    axs[1].set_title("contamination × n = how many you get back")
    axs[1].legend()
    axs[1].tick_params(axis="x", rotation=45)


def detector_comparison(fig, axes, p: Palette) -> None:
    """Four detectors on the same contaminated cloud."""
    from sklearn.covariance import EllipticEnvelope
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.svm import OneClassSVM

    X, y = contaminated(seed=3)
    truth = y == -1

    models = [
        ("IsolationForest", IsolationForest(contamination=0.07, random_state=0)),
        ("LocalOutlierFactor", LocalOutlierFactor(n_neighbors=20, contamination=0.07)),
        ("OneClassSVM", OneClassSVM(nu=0.07, gamma=0.1)),
        ("EllipticEnvelope", EllipticEnvelope(contamination=0.07, random_state=0)),
    ]
    axs = fig.subplots(1, 4, sharex=True, sharey=True)
    for ax, (name, m) in zip(axs, models):
        pred = m.fit_predict(X)
        hit = pred == -1
        tp = int((hit & truth).sum())
        fp = int((hit & ~truth).sum())
        ax.scatter(X[~hit, 0], X[~hit, 1], s=10, c=p.muted, edgecolors="none")
        ax.scatter(X[hit & truth, 0], X[hit & truth, 1], s=34, c=p.green,
                   marker="X")
        ax.scatter(X[hit & ~truth, 0], X[hit & ~truth, 1], s=34, c=p.red,
                   marker="X")
        ax.set_title(f"{name}\n{tp} correct, {fp} false", fontsize=9.5)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Green = a real outlier caught, red = an inlier wrongly flagged "
                 "(20 real outliers in 300 points)", fontsize=10, color=p.muted)


FIGURES = [
    figure("path-lengths", path_lengths, size=(8.8, 3.6), axes=False),
    figure("score-surface", score_surface, size=(7.4, 4.6)),
    figure("contamination-sweep", contamination_sweep, size=(9.0, 3.6), axes=False),
    figure("detector-comparison", detector_comparison, size=(9.2, 3.0), axes=False),
]
