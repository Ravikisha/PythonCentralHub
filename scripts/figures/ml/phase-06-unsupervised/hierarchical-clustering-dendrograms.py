"""Figures for *Hierarchical Clustering (Dendrograms)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import blobs, moons, scatter  # noqa: E402
from _style import Palette, figure  # noqa: E402

# The eight-point toy set the page works through by hand.
TOY = np.array(
    [
        [1.0, 1.0],
        [1.5, 1.2],
        [1.2, 2.0],
        [5.0, 5.0],
        [5.4, 5.6],
        [6.0, 5.1],
        [9.0, 1.0],
        [9.4, 1.6],
    ]
)


def toy_dendrogram(fig, axes, p: Palette) -> None:
    """The eight hand-worked points, and the tree the merges build."""
    from scipy.cluster.hierarchy import dendrogram, linkage

    axs = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.25]})

    axs[0].scatter(TOY[:, 0], TOY[:, 1], s=70, c=p.blue, zorder=4)
    for i, (x, y) in enumerate(TOY):
        axs[0].annotate(chr(ord("A") + i), (x + 0.18, y + 0.18), color=p.amber,
                        fontsize=11)
    axs[0].set_title("Eight points")
    axs[0].set_xticks([])
    axs[0].set_yticks([])

    Z = linkage(TOY, method="ward")
    dendrogram(Z, ax=axs[1], labels=[chr(ord("A") + i) for i in range(8)],
               color_threshold=4.0,
               above_threshold_color=p.muted,
               link_color_func=None)
    axs[1].set_title("Ward dendrogram (cut at height 4 gives 3 clusters)")
    axs[1].axhline(4.0, color=p.red, ls="--", lw=1.6)
    axs[1].set_ylabel("merge distance")
    for spine in ("top", "right"):
        axs[1].spines[spine].set_visible(False)
    axs[1].grid(axis="y")


def linkage_comparison(fig, axes, p: Palette) -> None:
    """Four linkage rules on identical points: four different trees."""
    from scipy.cluster.hierarchy import dendrogram, linkage

    X, _ = blobs(n=60, k=3, seed=8, std=1.1)
    axs = fig.subplots(1, 4, sharey=False)
    for ax, method in zip(axs, ("single", "complete", "average", "ward")):
        Z = linkage(X, method=method)
        dendrogram(Z, ax=ax, no_labels=True, color_threshold=0,
                   above_threshold_color=p.blue)
        ax.set_title(method, fontsize=10)
        ax.set_xticks([])
        ax.grid(axis="y")
    axs[0].set_ylabel("merge distance")
    fig.suptitle("Single linkage chains; complete and Ward make compact balls",
                 fontsize=11, color=p.muted)


def linkage_on_moons(fig, axes, p: Palette) -> None:
    """Where single linkage wins and Ward loses, and vice versa."""
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import adjusted_rand_score

    Xm, ym = moons(n=240, seed=2, noise=0.05)
    Xb, yb = blobs(n=240, k=3, seed=2, std=1.0)

    axs = fig.subplots(2, 4)
    for row, (X, y, k, name) in enumerate([(Xm, ym, 2, "moons"),
                                           (Xb, yb, 3, "blobs")]):
        for col, method in enumerate(("single", "complete", "average", "ward")):
            lab = AgglomerativeClustering(n_clusters=k, linkage=method).fit_predict(X)
            scatter(axs[row, col], X, lab, p, size=11)
            axs[row, col].set_xlabel(f"ARI {adjusted_rand_score(y, lab):.2f}",
                                     fontsize=9, color=p.muted)
            if row == 0:
                axs[row, col].set_title(method, fontsize=10)
        axs[row, 0].set_ylabel(name, fontsize=10, color=p.fg)


def cutting_the_tree(fig, axes, p: Palette) -> None:
    """Read the plateau: cheap merges join points, expensive ones join groups."""
    from scipy.cluster.hierarchy import fcluster, linkage

    X, _ = blobs(n=200, k=4, seed=13, std=0.8)
    Z = linkage(X, method="ward")
    last = Z[-12:, 2]
    k_before = np.arange(13, 1, -1)  # merging k_before clusters down to k_before-1

    axs = fig.subplots(1, 2)
    axs[0].plot(k_before, last, "o-", color=p.blue)
    axs[0].axhline(20, color=p.red, ls="--", lw=1.5, label="cut at height 20")
    axs[0].annotate("cheap merges:\njoining nearby points", (12.6, 52),
                    color=p.muted, fontsize=9)
    axs[0].annotate("expensive merges:\njoining whole groups", (4.2, 70),
                    color=p.amber, fontsize=9)
    axs[0].set_xlabel("clusters before this merge")
    axs[0].set_ylabel("merge distance")
    axs[0].set_title("The plateau ends at 4 clusters")
    axs[0].invert_xaxis()
    axs[0].legend(loc="center left")

    labels = fcluster(Z, t=20, criterion="distance")
    scatter(axs[1], X, labels - 1, p, size=14)
    axs[1].set_title(f"Cutting at 20 gives {len(set(labels))} clusters")


FIGURES = [
    figure("toy-dendrogram", toy_dendrogram, size=(8.8, 3.6), axes=False),
    figure("linkage-comparison", linkage_comparison, size=(9.0, 3.2), axes=False),
    figure("linkage-on-moons", linkage_on_moons, size=(9.0, 4.6), axes=False),
    figure("cutting-the-tree", cutting_the_tree, size=(8.6, 3.4), axes=False),
]
