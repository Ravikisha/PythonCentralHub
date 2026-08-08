"""Figures for *Introduction to Clustering*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import anisotropic, blobs, moons, scatter, varied_variance  # noqa: E402
from _style import Palette, figure  # noqa: E402


def distance_metrics(fig, axes, p: Palette) -> None:
    """The same two points are 'close' or 'far' depending on the metric."""
    axs = fig.subplots(1, 3)
    a = np.array([1.0, 1.0])
    b = np.array([4.0, 5.0])

    for ax in axs:
        ax.set_xlim(-0.4, 5.6)
        ax.set_ylim(-0.4, 6.2)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.scatter(*a, s=70, c=p.blue, zorder=5)
        ax.scatter(*b, s=70, c=p.amber, zorder=5)
        ax.annotate("a", a + [0.15, -0.45], color=p.blue, fontsize=11)
        ax.annotate("b", b + [0.15, 0.2], color=p.amber, fontsize=11)

    euclid = float(np.linalg.norm(a - b))
    manhattan = float(np.abs(a - b).sum())
    cos_sim = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

    axs[0].plot([a[0], b[0]], [a[1], b[1]], color=p.green, lw=2.5)
    axs[0].set_title(f"Euclidean  =  {euclid:.2f}")

    axs[1].plot([a[0], b[0], b[0]], [a[1], a[1], b[1]], color=p.green, lw=2.5)
    axs[1].annotate("3", (2.5, 0.6), color=p.muted)
    axs[1].annotate("4", (4.15, 3.0), color=p.muted)
    axs[1].set_title(f"Manhattan  =  {manhattan:.2f}")

    ang_a = float(np.arctan2(*a[::-1]))
    ang_b = float(np.arctan2(*b[::-1]))
    for v, c in ((a, p.blue), (b, p.amber)):
        u = v / np.linalg.norm(v)
        axs[2].annotate("", xy=7.2 * u, xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=c, lw=2))
    axs[2].annotate(f"{np.degrees(ang_b - ang_a):.1f}° apart", (2.2, 3.5),
                    color=p.green, fontsize=10)
    axs[2].set_title(f"cosine distance  =  {1 - cos_sim:.4f}")

    fig.suptitle("Three metrics, one pair of points", fontsize=12,
                 fontweight="bold", color=p.fg)


def scaling_changes_everything(fig, axes, p: Palette) -> None:
    """Unscaled features let the widest column dictate the clusters."""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    rng = np.random.default_rng(0)
    # age in years, income in dollars: two real groups, but wildly different units
    age = np.concatenate([rng.normal(28, 4, 90), rng.normal(52, 4, 90)])
    income = np.concatenate([rng.normal(60_000, 12_000, 90),
                             rng.normal(64_000, 12_000, 90)])
    X = np.column_stack([age, income])
    truth = np.concatenate([np.zeros(90), np.ones(90)])

    raw = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X)
    Xs = StandardScaler().fit_transform(X)
    scaled = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(Xs)

    axs = fig.subplots(1, 3, sharex=True, sharey=True)
    for ax, lab, title in zip(
        axs, (truth, raw, scaled),
        ("The real groups", "k-means on raw columns", "k-means after scaling"),
    ):
        for c in (0, 1):
            m = lab == c
            ax.scatter(X[m, 0], X[m, 1] / 1000, s=14,
                       c=(p.blue if c == 0 else p.amber), edgecolors="none")
        ax.set_title(title)
        ax.set_xlabel("age (years)")
    axs[0].set_ylabel("income ($1000s)")
    fig.suptitle("Income spans 60,000 units and age spans 40 — unscaled, only "
                 "income counts", fontsize=11, color=p.muted)


def cluster_shapes(fig, axes, p: Palette) -> None:
    """Four geometries; k-means only truly handles the first."""
    from sklearn.cluster import DBSCAN, KMeans

    datasets = [
        ("Round, equal blobs", blobs(n=600, k=3, seed=1)[0], 3, 0.6),
        ("Sheared (anisotropic)", anisotropic()[0], 3, 0.4),
        ("Different spreads", varied_variance()[0], 3, 0.5),
        ("Non-convex (moons)", moons(n=600, seed=1)[0], 2, 0.16),
    ]
    axs = fig.subplots(2, 4)
    for col, (title, X, k, eps) in enumerate(datasets):
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
        db = DBSCAN(eps=eps, min_samples=6).fit_predict(X)
        for row, lab in enumerate((km, db)):
            ax = axs[row, col]
            scatter(ax, X, lab, p, size=11)
            if row == 0:
                ax.set_title(title, fontsize=10)
        axs[0, col].set_ylabel("")
    axs[0, 0].set_ylabel("k-means", fontsize=10, color=p.fg)
    axs[1, 0].set_ylabel("DBSCAN", fontsize=10, color=p.fg)


def silhouette_anatomy(fig, axes, p: Palette) -> None:
    """A silhouette plot beside the clustering it scores."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_samples, silhouette_score

    X, _ = blobs(n=300, k=4, seed=5, std=1.1)
    labels = KMeans(n_clusters=4, n_init=10, random_state=0).fit_predict(X)
    sil = silhouette_samples(X, labels)
    overall = silhouette_score(X, labels)

    axs = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1]})
    colors = [p.blue, p.amber, p.green, p.purple]

    y0 = 0
    for c in range(4):
        vals = np.sort(sil[labels == c])
        axs[0].fill_betweenx(np.arange(y0, y0 + len(vals)), 0, vals,
                             color=colors[c], alpha=0.85)
        axs[0].text(-0.06, y0 + len(vals) / 2, str(c), color=p.muted, va="center")
        y0 += len(vals) + 10
    axs[0].axvline(overall, color=p.red, ls="--", lw=1.6,
                   label=f"mean = {overall:.3f}")
    axs[0].set_xlabel("silhouette coefficient")
    axs[0].set_yticks([])
    axs[0].set_title("Every point, sorted within its cluster")
    axs[0].legend(loc="lower right")

    scatter(axs[1], X, labels, p, size=14)
    axs[1].set_title("The clustering being scored")


FIGURES = [
    figure("distance-metrics", distance_metrics, size=(8.6, 3.2), axes=False),
    figure("scaling-changes-everything", scaling_changes_everything,
           size=(9.0, 3.5), axes=False),
    figure("cluster-shapes", cluster_shapes, size=(9.0, 4.8), axes=False),
    figure("silhouette-anatomy", silhouette_anatomy, size=(8.8, 4.0), axes=False),
]
