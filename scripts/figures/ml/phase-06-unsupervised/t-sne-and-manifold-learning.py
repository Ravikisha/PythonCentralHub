"""Figures for *t-SNE and Manifold Learning*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import swiss_roll  # noqa: E402
from _style import Palette, figure  # noqa: E402


def swiss_roll_unrolled(fig, axes, p: Palette) -> None:
    """PCA flattens the roll; the manifold methods unroll it."""
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE, LocallyLinearEmbedding

    X, t = swiss_roll(n=1200, seed=42)
    axs = fig.subplots(1, 4)

    axs[0].remove()
    ax3d = fig.add_subplot(1, 4, 1, projection="3d")
    ax3d.scatter(X[:, 0], X[:, 1], X[:, 2], c=t, cmap="viridis", s=5)
    ax3d.set_title("Swiss roll in 3-D", fontsize=10)
    ax3d.set_xticks([])
    ax3d.set_yticks([])
    ax3d.set_zticks([])
    ax3d.set_facecolor(p.bg)
    for pane in (ax3d.xaxis, ax3d.yaxis, ax3d.zaxis):
        pane.set_pane_color((0, 0, 0, 0))
        pane.line.set_color(p.grid)
        pane._axinfo["grid"]["color"] = p.grid
    ax3d.view_init(elev=10, azim=-72)
    ax3d.set_box_aspect((1, 1, 1), zoom=1.35)

    embeddings = [
        ("PCA", PCA(n_components=2, random_state=0).fit_transform(X)),
        ("Modified LLE (k = 12)",
         LocallyLinearEmbedding(n_neighbors=12, n_components=2,
                                method="modified",
                                random_state=0).fit_transform(X)),
        ("t-SNE (perplexity 30)",
         TSNE(n_components=2, perplexity=30, init="pca",
              random_state=0).fit_transform(X)),
    ]
    for ax, (title, Z) in zip(axs[1:], embeddings):
        ax.scatter(Z[:, 0], Z[:, 1], c=t, cmap="viridis", s=6)
        ax.set_title(title, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])


def perplexity_sweep(fig, axes, p: Palette) -> None:
    """Perplexity is a guess at the neighbourhood size, and it changes the map."""
    from sklearn.datasets import load_digits
    from sklearn.manifold import TSNE

    d = load_digits()
    X, y = d.data[:800], d.target[:800]
    axs = fig.subplots(1, 4, sharex=False, sharey=False)
    for ax, per in zip(axs, (2, 5, 30, 100)):
        Z = TSNE(n_components=2, perplexity=per, init="pca",
                 random_state=0).fit_transform(X)
        ax.scatter(Z[:, 0], Z[:, 1], c=y, cmap="tab10", s=5)
        ax.set_title(f"perplexity = {per}", fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Same 800 digits, four perplexities — the shapes are not "
                 "comparable across panels", fontsize=11, color=p.muted)


def pca_vs_tsne_digits(fig, axes, p: Palette) -> None:
    """Two 2-D views of the same 64-D digits."""
    from sklearn.datasets import load_digits
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE

    d = load_digits()
    X, y = d.data, d.target
    axs = fig.subplots(1, 2)

    Zp = PCA(n_components=2, random_state=0).fit_transform(X)
    Zt = TSNE(n_components=2, perplexity=30, init="pca",
              random_state=0).fit_transform(X)
    for ax, Z, title in [(axs[0], Zp, "PCA: 2 of 64 components"),
                         (axs[1], Zt, "t-SNE: perplexity 30")]:
        sc = ax.scatter(Z[:, 0], Z[:, 1], c=y, cmap="tab10", s=6)
        ax.set_title(title, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
    cb = fig.colorbar(sc, ax=axs, ticks=range(10), fraction=0.03)
    cb.set_label("digit", color=p.fg)
    cb.ax.tick_params(colors=p.muted)


def cluster_sizes_lie(fig, axes, p: Palette) -> None:
    """t-SNE equalises cluster size and destroys between-cluster distance."""
    from sklearn.manifold import TSNE

    rng = np.random.default_rng(0)
    tight = rng.normal([0, 0], 0.30, size=(150, 2))
    loose = rng.normal([6, 0], 1.60, size=(150, 2))
    far = rng.normal([40, 0], 0.30, size=(150, 2))
    X = np.vstack([tight, loose, far])
    y = np.repeat([0, 1, 2], 150)

    Z = TSNE(n_components=2, perplexity=30, init="pca",
             random_state=0).fit_transform(X)

    axs = fig.subplots(1, 2)
    cols = [p.blue, p.amber, p.green]
    for c in range(3):
        axs[0].scatter(X[y == c, 0], X[y == c, 1], s=10, c=cols[c],
                       edgecolors="none")
        axs[1].scatter(Z[y == c, 0], Z[y == c, 1], s=10, c=cols[c],
                       edgecolors="none")
    axs[0].set_title("Truth: one tight blob, one 5× wider,\none 40 units away",
                     fontsize=10)
    axs[1].set_title("t-SNE: three similar puffs,\nspacing unrelated to the truth",
                     fontsize=10)
    for ax in axs:
        ax.set_xticks([])
        ax.set_yticks([])


FIGURES = [
    figure("swiss-roll-unrolled", swiss_roll_unrolled, size=(9.4, 2.9), axes=False),
    figure("perplexity-sweep", perplexity_sweep, size=(9.2, 3.0), axes=False),
    figure("pca-vs-tsne-digits", pca_vs_tsne_digits, size=(8.6, 3.8), axes=False),
    figure("cluster-sizes-lie", cluster_sizes_lie, size=(8.2, 3.6), axes=False),
]
