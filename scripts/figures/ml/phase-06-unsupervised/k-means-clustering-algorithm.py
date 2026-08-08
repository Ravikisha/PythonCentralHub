"""Figures for *K-Means Clustering Algorithm*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import anisotropic, blobs, structureless, varied_variance  # noqa: E402
from _style import Palette, figure  # noqa: E402

COLS = lambda p: [p.blue, p.amber, p.green, p.purple, p.red]  # noqa: E731


def lloyd_iterations(fig, axes, p: Palette) -> None:
    """Assign, update, repeat — the first three passes and the fixed point."""
    from sklearn.cluster import KMeans

    X, _ = blobs(n=280, k=3, seed=4, std=0.95)
    init = np.array([[-8.0, 8.0], [-7.0, 7.0], [-6.5, 9.0]])  # deliberately bad
    axs = fig.subplots(1, 4, sharex=True, sharey=True)
    cols = COLS(p)

    for ax, it in zip(axs, (1, 2, 3, 20)):
        km = KMeans(n_clusters=3, init=init, n_init=1, max_iter=it,
                    algorithm="lloyd", random_state=0).fit(X)
        lab = km.predict(X)
        for c in range(3):
            m = lab == c
            ax.scatter(X[m, 0], X[m, 1], s=11, c=cols[c], alpha=0.75,
                       edgecolors="none")
        ax.scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1],
                   s=150, marker="X", c=p.fg, edgecolors=p.bg, linewidths=1.5,
                   zorder=6)
        ax.set_xticks([])
        ax.set_yticks([])
        label = "converged" if it == 20 else f"iteration {it}"
        ax.set_title(f"{label}\ninertia {km.inertia_:.1f}", fontsize=10)


def elbow_and_silhouette(fig, axes, p: Palette) -> None:
    """Inertia always falls; the silhouette has an actual maximum."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    X, _ = blobs(n=400, k=4, seed=11, std=0.9)
    ks = list(range(1, 11))
    inertia, sil = [], []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
        inertia.append(km.inertia_)
        sil.append(silhouette_score(X, km.labels_) if k > 1 else np.nan)

    axs = fig.subplots(1, 2)
    axs[0].plot(ks, inertia, "o-", color=p.blue)
    axs[0].axvline(4, color=p.amber, ls="--", lw=1.5)
    axs[0].annotate("elbow", (4.15, inertia[3] * 2.2), color=p.amber)
    axs[0].set_xlabel("k")
    axs[0].set_ylabel("inertia")
    axs[0].set_title("Inertia never increases")

    axs[1].plot(ks[1:], sil[1:], "o-", color=p.green)
    best = int(np.nanargmax(sil))
    axs[1].scatter([ks[best]], [sil[best]], s=130, facecolors="none",
                   edgecolors=p.red, linewidths=2,
                   label=f"best k = {ks[best]} ({sil[best]:.3f})")
    axs[1].set_xlabel("k")
    axs[1].set_ylabel("mean silhouette")
    axs[1].set_title("The silhouette peaks")
    axs[1].legend()


def init_matters(fig, axes, p: Palette) -> None:
    """A single unlucky start can leave k-means in a bad local optimum."""
    from sklearn.cluster import KMeans

    X, _ = blobs(n=300, k=5, seed=3, std=0.7)
    axs = fig.subplots(1, 3, sharex=True, sharey=True)
    cols = COLS(p)

    runs = [
        ("random init, n_init=1\n(seed 5)", dict(init="random", n_init=1, random_state=5)),
        ("random init, n_init=1\n(seed 9)", dict(init="random", n_init=1, random_state=9)),
        ("k-means++, n_init=10", dict(init="k-means++", n_init=10, random_state=0)),
    ]
    for ax, (title, kw) in zip(axs, runs):
        km = KMeans(n_clusters=5, **kw).fit(X)
        for c in range(5):
            m = km.labels_ == c
            ax.scatter(X[m, 0], X[m, 1], s=11, c=cols[c], alpha=0.75,
                       edgecolors="none")
        ax.scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1],
                   s=140, marker="X", c=p.fg, edgecolors=p.bg, linewidths=1.5,
                   zorder=6)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"{title}\ninertia {km.inertia_:.1f}", fontsize=10)


def voronoi_boundaries(fig, axes, p: Palette) -> None:
    """k-means partitions the whole plane into straight-edged cells."""
    from sklearn.cluster import KMeans

    X, _ = blobs(n=300, k=4, seed=42, std=0.9)
    km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(X)

    pad = 1.2
    xx, yy = np.meshgrid(
        np.linspace(X[:, 0].min() - pad, X[:, 0].max() + pad, 400),
        np.linspace(X[:, 1].min() - pad, X[:, 1].max() + pad, 400),
    )
    Z = km.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    from matplotlib.colors import ListedColormap

    cmap = ListedColormap([p.blue, p.amber, p.green, p.purple])
    axes.contourf(xx, yy, Z, alpha=0.16, cmap=cmap, levels=[-0.5, 0.5, 1.5, 2.5, 3.5])
    axes.contour(xx, yy, Z, colors=p.muted, linewidths=1.0,
                 levels=[0.5, 1.5, 2.5])
    axes.scatter(X[:, 0], X[:, 1], s=13, c=p.fg, alpha=0.55, edgecolors="none")
    axes.scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1], s=170,
                 marker="X", c=p.red, edgecolors=p.bg, linewidths=1.5, zorder=6)
    axes.set_xticks([])
    axes.set_yticks([])
    axes.grid(False)
    axes.set_title("Every boundary is the perpendicular bisector of two centroids")


def where_kmeans_fails(fig, axes, p: Palette) -> None:
    """Three geometries the equal-round-cluster assumption cannot express."""
    from sklearn.cluster import KMeans

    from sklearn.metrics import adjusted_rand_score

    cases = [
        ("Sheared clusters", *anisotropic()),
        ("Different spreads", *varied_variance()),
        ("No clusters at all", *structureless()),
    ]
    axs = fig.subplots(2, 3)
    cols = COLS(p)
    for col, (title, X, truth) in enumerate(cases):
        km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)
        ari = adjusted_rand_score(truth, km.labels_)
        for row, lab in enumerate((truth, km.labels_)):
            ax = axs[row, col]
            for c in range(3):
                m = lab == c
                ax.scatter(X[m, 0], X[m, 1], s=8, c=cols[c], alpha=0.7,
                           edgecolors="none")
            ax.set_xticks([])
            ax.set_yticks([])
        axs[1, col].scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1],
                            s=130, marker="X", c=p.fg, edgecolors=p.bg,
                            linewidths=1.4, zorder=6)
        axs[0, col].set_title(title, fontsize=10)
        axs[1, col].set_xlabel(f"adjusted Rand index {ari:.3f}", fontsize=9,
                               color=p.muted)
    axs[0, 0].set_ylabel("the real groups", fontsize=10, color=p.fg)
    axs[1, 0].set_ylabel("what k-means finds", fontsize=10, color=p.fg)
    fig.suptitle("k-means splits by distance to a centre, so it cuts through "
                 "the real groups", fontsize=11, color=p.muted)


FIGURES = [
    figure("lloyd-iterations", lloyd_iterations, size=(9.0, 2.9), axes=False),
    figure("elbow-and-silhouette", elbow_and_silhouette, size=(8.6, 3.6), axes=False),
    figure("init-matters", init_matters, size=(8.6, 3.4), axes=False),
    figure("voronoi-boundaries", voronoi_boundaries, size=(7.0, 4.6)),
    figure("where-kmeans-fails", where_kmeans_fails, size=(8.8, 5.4), axes=False),
]
