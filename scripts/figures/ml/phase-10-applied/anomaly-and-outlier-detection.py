"""Figures for *Anomaly and Outlier Detection*."""

import functools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import DENSE_CENTRE, anomalies  # noqa: E402
from _style import Palette, figure  # noqa: E402

CONTAMINATION = 0.02


def score_all(X, contamination=CONTAMINATION):
    """Higher means more anomalous, for five detectors on the same data."""
    from sklearn.covariance import EllipticEnvelope
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import OneClassSVM

    out = {}
    out["Isolation Forest"] = -IsolationForest(
        random_state=0, contamination=contamination).fit(X).score_samples(X)

    lof = LocalOutlierFactor(n_neighbors=20, contamination=contamination)
    lof.fit_predict(X)
    out["LOF (k=20)"] = -lof.negative_outlier_factor_

    lof10 = LocalOutlierFactor(n_neighbors=10, contamination=contamination)
    lof10.fit_predict(X)
    out["LOF (k=10)"] = -lof10.negative_outlier_factor_

    out["Elliptic Envelope"] = -EllipticEnvelope(
        random_state=0, contamination=contamination).fit(X).score_samples(X)

    Z = StandardScaler().fit_transform(X)
    out["One-class SVM"] = -OneClassSVM(nu=contamination,
                                        gamma="scale").fit(Z).score_samples(Z)
    out["distance from the mean"] = np.linalg.norm(Z - Z.mean(0), axis=1)
    return out


@functools.lru_cache(maxsize=8)
def setup(n_noise=0):
    X, y = anomalies(n_noise=n_noise)
    return {"X": X, "y": y, "scores": score_all(X)}


def two_kinds(fig, axes, p: Palette) -> None:
    """The data, and the two anomaly types that need different tools."""
    d = setup()
    X, y = d["X"], d["y"]

    axs = fig.subplots(1, 2, width_ratios=[1.25, 1])

    axs[0].scatter(X[y == 0, 0], X[y == 0, 1], s=5, color=p.muted, alpha=0.55,
                   label=f"normal ({int((y == 0).sum()):,})")
    axs[0].scatter(X[y == 1, 0], X[y == 1, 1], s=34, color=p.red,
                   label=f"global anomaly ({int((y == 1).sum())})")
    axs[0].scatter(X[y == 2, 0], X[y == 2, 1], s=34, color=p.amber,
                   label=f"local anomaly ({int((y == 2).sum())})")
    axs[0].set_title(f"{len(X):,} points, {int((y > 0).sum())} of them anomalous "
                     f"({(y > 0).mean():.2%})", fontsize=10.5)
    axs[0].legend(loc="upper left", fontsize=8.5)

    win = 2.2
    mask = (np.abs(X[:, 0] - DENSE_CENTRE[0]) < win) & \
           (np.abs(X[:, 1] - DENSE_CENTRE[1]) < win)
    axs[1].scatter(X[mask & (y == 0), 0], X[mask & (y == 0), 1], s=9,
                   color=p.muted, alpha=0.7)
    axs[1].scatter(X[mask & (y == 2), 0], X[mask & (y == 2), 1], s=44,
                   color=p.amber)
    axs[1].set_xlim(DENSE_CENTRE[0] - win, DENSE_CENTRE[0] + win)
    axs[1].set_ylim(DENSE_CENTRE[1] - win, DENSE_CENTRE[1] + win)
    axs[1].set_title("Zoom on the tight cluster (sd 0.28)", fontsize=10.5)
    axs[1].annotate("these sit 3-5 sd out —\nordinary inside the diffuse\ncluster, "
                    "impossible here",
                    (DENSE_CENTRE[0] - 2.0, DENSE_CENTRE[1] + 1.2), fontsize=9,
                    color=p.amber)

    fig.suptitle("One cluster has sd 0.28 and the other 1.35, which is what makes "
                 "'anomalous' a local question.",
                 fontsize=10.5, color=p.muted)


def method_comparison(fig, axes, p: Palette) -> None:
    """Average precision overall, and split by anomaly type."""
    from sklearn.metrics import average_precision_score

    d = setup()
    y = d["y"]
    names = ["Isolation Forest", "LOF (k=20)", "LOF (k=10)", "Elliptic Envelope",
             "One-class SVM", "distance from the mean"]

    overall, glob, loc = [], [], []
    for name in names:
        s = d["scores"][name]
        overall.append(average_precision_score((y > 0).astype(int), s))
        glob.append(average_precision_score((y == 1).astype(int), s))
        loc.append(average_precision_score((y == 2).astype(int), s))

    idx = np.arange(len(names))
    axes.barh(idx + 0.26, glob, 0.25, color=p.red, label="global anomalies (45)")
    axes.barh(idx, overall, 0.25, color=p.blue, label="all anomalies (65)")
    axes.barh(idx - 0.26, loc, 0.25, color=p.amber, label="local anomalies (20)")
    for i in range(len(names)):
        for offset, values, colour in ((0.26, glob, p.red), (0, overall, p.blue),
                                       (-0.26, loc, p.amber)):
            axes.annotate(f"{values[i]:.4f}", (values[i] + 0.012, i + offset),
                          va="center", fontsize=8, color=colour)
    axes.set_yticks(idx)
    axes.set_yticklabels(names, fontsize=9)
    axes.set_xlim(0, 1.16)
    axes.set_xlabel("average precision")
    axes.set_title("Isolation Forest owns the far outliers; only LOF sees the "
                   "local ones")
    axes.legend(loc="lower right", fontsize=8.5)


def k_sensitivity(fig, axes, p: Palette) -> None:
    """The one hyperparameter that matters, and no labels to tune it with."""
    from sklearn.metrics import average_precision_score
    from sklearn.neighbors import LocalOutlierFactor

    d = setup()
    X, y = d["X"], d["y"]
    ks = [5, 10, 15, 20, 30, 50, 80, 120]
    overall, glob, loc = [], [], []
    for k in ks:
        lof = LocalOutlierFactor(n_neighbors=k, contamination=CONTAMINATION)
        lof.fit_predict(X)
        s = -lof.negative_outlier_factor_
        overall.append(average_precision_score((y > 0).astype(int), s))
        glob.append(average_precision_score((y == 1).astype(int), s))
        loc.append(average_precision_score((y == 2).astype(int), s))

    axes.plot(ks, glob, "o-", color=p.red, lw=2.0, label="global anomalies")
    axes.plot(ks, overall, "o-", color=p.blue, lw=2.2, label="all anomalies")
    axes.plot(ks, loc, "o-", color=p.amber, lw=2.0, label="local anomalies")
    best_local = int(np.argmax(loc))
    axes.annotate(f"local best at k={ks[best_local]}\nAP {loc[best_local]:.4f}",
                  (ks[best_local], loc[best_local]),
                  textcoords="offset points", xytext=(14, 10), fontsize=9,
                  color=p.amber)
    axes.set_xscale("log")
    axes.set_xlabel("LOF n_neighbors (log scale)")
    axes.set_ylabel("average precision")
    axes.set_ylim(0, 1.08)
    axes.set_title("k trades local sensitivity against global sensitivity")
    axes.legend(loc="center right", fontsize=9)


def noise_dimensions(fig, axes, p: Palette) -> None:
    """Add columns that contain nothing, and watch the detectors fall over."""
    from sklearn.metrics import average_precision_score

    counts = (0, 4, 10, 20, 40)
    names = ["Isolation Forest", "LOF (k=20)", "Elliptic Envelope",
             "distance from the mean"]
    colours = {"Isolation Forest": p.blue, "LOF (k=20)": p.amber,
               "Elliptic Envelope": p.green,
               "distance from the mean": p.muted}

    series = {n: [] for n in names}
    for n_noise in counts:
        d = setup(n_noise)
        y = d["y"]
        for name in names:
            series[name].append(
                average_precision_score((y > 0).astype(int), d["scores"][name]))

    for name in names:
        axes.plot([2 + c for c in counts], series[name], "o-",
                  color=colours[name], lw=2.0, label=name)
        axes.annotate(f"{series[name][-1]:.3f}", (2 + counts[-1] + 1,
                                                  series[name][-1]),
                      va="center", fontsize=9, color=colours[name])
    axes.set_xlabel("total dimensions (2 informative + noise)")
    axes.set_ylabel("average precision, all anomalies")
    axes.set_ylim(0, 1.05)
    axes.set_xlim(1, 2 + counts[-1] + 7)
    first, last = series["Isolation Forest"][0], series["Isolation Forest"][-1]
    axes.set_title(f"Isolation Forest falls from {first:.3f} to {last:.3f} as "
                   f"noise columns are added")
    axes.legend(loc="upper right", fontsize=8.5)


def contamination_threshold(fig, axes, p: Palette) -> None:
    """`contamination` moves the cut. It does not change the ranking."""
    from sklearn.ensemble import IsolationForest
    from sklearn.metrics import average_precision_score, precision_score, recall_score

    d = setup()
    X, y = d["X"], d["y"]
    truth = (y > 0).astype(int)

    settings = [0.005, 0.01, 0.02, 0.05, 0.10]
    precisions, recalls, aps, flagged = [], [], [], []
    for c in settings:
        model = IsolationForest(random_state=0, contamination=c).fit(X)
        pred = (model.predict(X) == -1).astype(int)
        precisions.append(precision_score(truth, pred, zero_division=0))
        recalls.append(recall_score(truth, pred))
        aps.append(average_precision_score(truth, -model.score_samples(X)))
        flagged.append(int(pred.sum()))

    idx = np.arange(len(settings))
    axes.plot(idx, precisions, "o-", color=p.blue, lw=2.2, label="precision")
    axes.plot(idx, recalls, "o-", color=p.amber, lw=2.2, label="recall")
    axes.plot(idx, aps, "s--", color=p.green, lw=1.8,
              label="average precision (ranking quality)")
    for i, (pr, rc, n) in enumerate(zip(precisions, recalls, flagged)):
        axes.annotate(f"{n} flagged", (i, min(pr, rc) - 0.09), ha="center",
                      fontsize=8.5, color=p.muted)
    axes.set_xticks(idx)
    axes.set_xticklabels([f"{c:.3f}" for c in settings], fontsize=9.5)
    axes.set_xlabel("contamination")
    axes.set_ylim(0, 1.05)
    axes.set_title(f"Ranking quality is flat at {aps[0]:.4f}; only the cut moves")
    axes.legend(loc="center right", fontsize=9)


FIGURES = [
    figure("two-kinds", two_kinds, size=(8.8, 3.9), axes=False),
    figure("method-comparison", method_comparison, size=(8.6, 4.4)),
    figure("k-sensitivity", k_sensitivity, size=(8.0, 4.0)),
    figure("noise-dimensions", noise_dimensions, size=(8.0, 4.0)),
    figure("contamination-threshold", contamination_threshold, size=(8.0, 4.0)),
]
