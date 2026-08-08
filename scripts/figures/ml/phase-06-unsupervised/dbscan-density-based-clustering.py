"""Figures for *DBSCAN - Density-Based Clustering*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import blobs, moons, scatter, two_rings_with_noise  # noqa: E402
from _style import Palette, figure  # noqa: E402


def core_border_noise(fig, axes, p: Palette) -> None:
    """The three point types, drawn with the eps disc that defines them."""
    from sklearn.cluster import DBSCAN

    from matplotlib.patches import Circle

    rng = np.random.default_rng(1)
    # a jittered grid, so every interior point genuinely has >= min_samples
    gx, gy = np.meshgrid(np.linspace(-0.6, 0.6, 5), np.linspace(-0.6, 0.6, 5))
    dense = np.column_stack([gx.ravel(), gy.ravel()])
    dense = dense + rng.uniform(-0.07, 0.07, dense.shape)
    far = np.array([[1.9, 1.2], [-1.7, 1.1]])
    X = np.vstack([dense, far])

    eps, min_samples = 0.5, 5
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    core_mask = np.zeros(len(X), bool)
    core_mask[db.core_sample_indices_] = True
    kind = np.where(core_mask, 0, np.where(db.labels_ != -1, 1, 2))

    for i, (x, y) in enumerate(X):
        axes.scatter(x, y, s=45, c=[p.blue, p.amber, p.red][kind[i]], zorder=5)

    # one dashed eps disc per point type, so the definition is readable off the plot
    for k, col in zip((0, 1, 2), (p.blue, p.amber, p.red)):
        i = int(np.flatnonzero(kind == k)[12 if k == 0 else 0])
        axes.add_patch(Circle(X[i], eps, fill=False, ls="--", lw=1.3,
                              color=col, alpha=0.8, zorder=2))
        n_in = int((np.linalg.norm(X - X[i], axis=1) < eps).sum()) - 1
        axes.annotate(f"{n_in} within eps", X[i] + [0, -eps - 0.22],
                      ha="center", fontsize=9, color=col)

    axes.set_xlim(-2.4, 2.6)
    axes.set_ylim(-1.7, 2.3)

    from matplotlib.lines import Line2D

    axes.legend(handles=[
        Line2D([], [], marker="o", ls="", color=p.blue,
               label=f"core: ≥ {min_samples} neighbours within eps"),
        Line2D([], [], marker="o", ls="", color=p.amber,
               label="border: too few, but inside a core point's disc"),
        Line2D([], [], marker="o", ls="", color=p.red, label="noise: neither"),
    ], loc="upper left")
    axes.set_aspect("equal")
    axes.set_xticks([])
    axes.set_yticks([])
    axes.grid(False)
    axes.set_title(f"eps = {eps},  min_samples = {min_samples}")


def eps_sweep(fig, axes, p: Palette) -> None:
    """One parameter, four completely different answers."""
    from sklearn.cluster import DBSCAN

    X, _ = two_rings_with_noise(seed=7)
    axs = fig.subplots(1, 4, sharex=True, sharey=True)
    for ax, eps in zip(axs, (0.08, 0.16, 0.30, 0.60)):
        lab = DBSCAN(eps=eps, min_samples=5).fit_predict(X)
        n_clusters = len(set(lab)) - (1 if -1 in lab else 0)
        n_noise = int((lab == -1).sum())
        scatter(ax, X, lab, p, size=13)
        ax.set_title(f"eps = {eps}\n{n_clusters} clusters, {n_noise} noise",
                     fontsize=10)


def k_distance_plot(fig, axes, p: Palette) -> None:
    """The knee of the sorted k-distance curve is the eps to try first."""
    from sklearn.neighbors import NearestNeighbors

    X, _ = two_rings_with_noise(seed=7)
    k = 5
    nn = NearestNeighbors(n_neighbors=k).fit(X)
    d, _ = nn.kneighbors(X)
    kd = np.sort(d[:, -1])

    axes.plot(np.arange(len(kd)), kd, color=p.blue)
    knee = float(np.percentile(kd, 88))
    axes.axhline(knee, color=p.amber, ls="--", lw=1.6,
                 label=f"knee ≈ {knee:.3f}  →  a good first eps")
    axes.set_xlabel("points, sorted by distance to their 5th nearest neighbour")
    axes.set_ylabel(f"distance to {k}th neighbour")
    axes.set_title("The k-distance plot picks eps for you")
    axes.legend(loc="upper left")


def dbscan_vs_kmeans(fig, axes, p: Palette) -> None:
    """Two datasets, two algorithms, one clear division of labour."""
    from sklearn.cluster import DBSCAN, KMeans

    Xm, _ = moons(n=300, seed=4, noise=0.06)
    Xb, _ = blobs(n=300, k=3, seed=4, std=0.9)

    axs = fig.subplots(2, 2)
    combos = [
        (0, 0, Xm, KMeans(n_clusters=2, n_init=10, random_state=0), "k-means on moons"),
        (0, 1, Xm, DBSCAN(eps=0.25, min_samples=5), "DBSCAN on moons"),
        (1, 0, Xb, KMeans(n_clusters=3, n_init=10, random_state=0), "k-means on blobs"),
        (1, 1, Xb, DBSCAN(eps=0.9, min_samples=5), "DBSCAN on blobs"),
    ]
    for r, c, X, model, title in combos:
        lab = model.fit_predict(X)
        scatter(axs[r, c], X, lab, p, size=13)
        axs[r, c].set_title(title, fontsize=10)


FIGURES = [
    figure("core-border-noise", core_border_noise, size=(7.2, 4.4)),
    figure("eps-sweep", eps_sweep, size=(9.0, 3.0), axes=False),
    figure("k-distance-plot", k_distance_plot, size=(7.6, 3.8)),
    figure("dbscan-vs-kmeans", dbscan_vs_kmeans, size=(7.6, 5.4), axes=False),
]
